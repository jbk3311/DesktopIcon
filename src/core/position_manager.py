import os
import json
import winreg
import time
import win32gui
import win32con
import win32com.client

class IconPositionManager:
    def __init__(self):
        # 使用程序目录存储配置文件
        self.position_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'icon_positions.json'
        )
        self.load_positions()
    
    def load_positions(self):
        """加载图标位置信息"""
        try:
            if os.path.exists(self.position_file):
                with open(self.position_file, 'r', encoding='utf-8') as f:
                    self.positions = json.load(f)
            else:
                self.positions = {}
        except Exception as e:
            print(f"加载图标位置失败: {str(e)}")
            self.positions = {}
    
    def save_positions(self):
        """保存所有图标位置"""
        try:
            positions = {}
            key_path = r"Software\Microsoft\Windows\Shell\Bags\1\Desktop"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                i = 0
                while True:
                    try:
                        name, value, type_ = winreg.EnumValue(key, i)
                        if name.startswith("ItemPos_"):
                            item_name = name[8:]  # 移除 "ItemPos_" 前缀
                            positions[item_name] = list(value)
                        i += 1
                    except WindowsError:
                        break
            
            with open(self.position_file, 'w', encoding='utf-8') as f:
                json.dump(positions, f, ensure_ascii=False, indent=2)
            
            self.positions = positions
            
        except Exception as e:
            print(f"保存图标位置失败: {str(e)}")
            raise
    
    def restore_positions(self, target_icons=None):
        """恢复指定图标的位置"""
        if not self.positions:
            return
        
        try:
            key_path = r"Software\Microsoft\Windows\Shell\Bags\1\Desktop"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
                for item_name, position in self.positions.items():
                    # 如果指定了目标图标，只恢复这些图标的位置
                    if target_icons and item_name not in target_icons:
                        continue
                        
                    try:
                        icon_key = f"ItemPos_{item_name}"
                        winreg.SetValueEx(
                            key,
                            icon_key,
                            0,
                            winreg.REG_BINARY,
                            bytes(position)
                        )
                    except Exception as e:
                        print(f"恢复图标 {item_name} 位置失败: {str(e)}")
            
        except Exception as e:
            print(f"恢复图标位置失败: {str(e)}")
            raise
    
    def force_refresh(self):
        """强制刷新桌面"""
        try:
            # 方法1：使用 Shell API
            shell = win32com.client.Dispatch("Shell.Application")
            shell.Windows().Item(0).Refresh()
            
            # 方法2：发送刷新消息
            hwnd = win32gui.FindWindow("Progman", None)
            if hwnd:
                win32gui.SendMessage(hwnd, win32con.WM_COMMAND, 0x7103, 0)
                time.sleep(0.1)
                
            # 方法3：尝试触发视图更新
            desktop = shell.NameSpace(0x0000)
            desktop.Items()
            
        except Exception as e:
            print(f"刷新桌面失败: {str(e)}")