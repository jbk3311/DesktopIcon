# src/core/icon_manager.py
import os
import subprocess
import win32api
import win32con
from .position_manager import IconPositionManager
import time
import ctypes

class IconManager:
    def __init__(self):
        self.position_manager = IconPositionManager()
        # 在初始化时检查权限
        self.is_admin = self._check_admin()
        if not self.is_admin:
            print("警告: IconManager 未以管理员权限运行")
    
    def _check_admin(self):
        """检查是否具有管理员权限"""
        try:
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except:
            return False
    
    def _run_attrib_command(self, command):
        """以提升的权限运行 attrib 命令"""
        try:
            # 使用 subprocess 运行命令，捕获输出
            process = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return process.returncode == 0, process.stderr
        except Exception as e:
            return False, str(e)
    
    def get_desktop_icons(self):
        """获取所有桌面图标"""
        icons = []
        
        # 获取用户桌面路径
        user_desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        
        # 获取公共桌面路径
        public_desktop = os.path.join(os.environ.get('PUBLIC', ''), 'Desktop')
        
        # 获取所有桌面项目
        for desktop_path in [user_desktop, public_desktop]:
            if os.path.exists(desktop_path):
                for item in os.listdir(desktop_path):
                    full_path = os.path.join(desktop_path, item)
                    if os.path.exists(full_path):
                        icons.append({
                            'name': item,
                            'path': full_path,
                            'hidden': os.path.isfile(full_path) and 
                                     bool(os.stat(full_path).st_file_attributes & 2),
                            'is_public': desktop_path == public_desktop
                        })
        
        return sorted(icons, key=lambda x: x['name'].lower())
    
    def toggle_icons(self, paths, hide=True):
        """切换图标显示状态"""
        # 首先检查是否需要管理员权限
        needs_admin = any('Public' in path or 'public' in path for path in paths)
        if needs_admin and not self.is_admin:
            public_paths = [p for p in paths if 'Public' in p or 'public' in p]
            return 0, [(p, "需要管理员权限") for p in public_paths]
        
        if hide:
            self.position_manager.save_positions()
        
        success_count = 0
        failed_paths = []
        
        for path in paths:
            if os.path.exists(path):
                try:
                    # 使用 subprocess 以提升的权限运行命令
                    cmd = f'attrib {"+" if hide else "-"}h "{path}"'
                    process = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    if process.returncode == 0:
                        success_count += 1
                    else:
                        error_msg = process.stderr.strip() or "修改属性失败"
                        failed_paths.append((path, error_msg))
                        
                except Exception as e:
                    failed_paths.append((path, str(e)))
        
        if not hide and success_count > 0:
            # 在显示后等待一小段时间，确保文件属性修改生效
            time.sleep(0.5)
            # 多次尝试恢复位置
            for _ in range(3):
                try:
                    self.position_manager.restore_positions()
                    time.sleep(0.2)
                except Exception as e:
                    print(f"恢复位置失败，重试中: {str(e)}")
        
        # 刷新资源管理器
        try:
            import win32gui
            import win32con
            win32gui.SendMessage(
                win32gui.FindWindow("Progman", None),
                win32con.WM_COMMAND,
                0x7103,
                0
            )
        except Exception as e:
            print(f"刷新桌面失败: {str(e)}")
        
        return success_count, failed_paths

    def _set_file_attributes(self, path, hide):
        """使用 Windows API 设置文件属性"""
        try:
            # 获取当前文件属性
            attrs = win32api.GetFileAttributes(path)
            
            # 修改隐藏属性
            if hide:
                new_attrs = attrs | win32con.FILE_ATTRIBUTE_HIDDEN
            else:
                new_attrs = attrs & ~win32con.FILE_ATTRIBUTE_HIDDEN
            
            # 设置新属性
            win32api.SetFileAttributes(path, new_attrs)
            
        except Exception as e:
            raise Exception(f"设置文件属性失败: {str(e)}")