import subprocess
import platform
import os
import ctypes
from src.utils.logger import get_logger
import time
import ctypes.wintypes as wintypes

# 定义 LRESULT 类型
if not hasattr(wintypes, 'LRESULT'):
    wintypes.LRESULT = ctypes.c_ssize_t

class SystemSettingsManager:
    def __init__(self):
        self.system = platform.system()
        if self.system not in ['Windows', 'Darwin']:
            raise NotImplementedError(f"不支持的操作系统: {self.system}")
        
        self.logger = get_logger(__name__)
        # 设置日志级别，确保能看到详细信息
        #self.logger.setLevel(logging.DEBUG)
        
        # 保存初始状态
        self.initial_show_hidden = self._get_hidden_files_state()
        self.logger.info(f"初始状态已保存: {'显示' if self.initial_show_hidden else '隐藏'} 隐藏文件")

        # Windows API类型定义
        self.user32 = ctypes.WinDLL('user32')

        # 函数原型声明
        self.user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
        self.user32.FindWindowW.restype = wintypes.HWND

        self.user32.FindWindowExW.argtypes = [wintypes.HWND, wintypes.HWND, wintypes.LPCWSTR, wintypes.LPCWSTR]
        self.user32.FindWindowExW.restype = wintypes.HWND

        self.user32.SendMessageTimeoutW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
            wintypes.UINT,
            wintypes.UINT,
            ctypes.POINTER(wintypes.DWORD)
        ]
        self.user32.SendMessageTimeoutW.restype = ctypes.c_void_p

    def is_admin(self):
        """检查是否具有管理员权限"""
        try:
            if self.system == 'Windows':
                return ctypes.windll.shell32.IsUserAnAdmin()
            elif self.system == 'Darwin':
                return 'SUDO_USER' in os.environ
        except Exception as e:
            self.logger.error(f"检查管理员权限时出错: {e}")
            return False
        return False

    def run_command(self, command):
        """运行系统命令"""
        try:
            if self.system == 'Windows':
                # result = subprocess.run(['powershell', '-Command', command],
                #                      capture_output=True, text=True)
                # 使用 -WindowStyle Hidden 和 -NonInteractive 参数使 PowerShell 静默运行
                result = subprocess.run(
                    ['powershell', '-WindowStyle', 'Hidden', '-NonInteractive', '-Command', command],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW  # 防止显示命令行窗口
                )
            else:
                result = subprocess.run(command, shell=True,
                                     capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"命令执行失败: {result.stderr}")
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"执行命令失败: {e}")
            return False

    def _get_hidden_files_state(self):
        """获取当前隐藏文件的显示状态"""
        try:
            if self.system == 'Windows':
                command = 'Get-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name "Hidden" | Select-Object -ExpandProperty Hidden'
                result = subprocess.run(['powershell', '-Command', command],
                                     capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                # 转换为整数并判断
                value = int(result.stdout.strip())
                is_showing = (value == 1)
                self.logger.debug(f"获取到的Hidden值: {value}, 表示{'显示' if is_showing else '隐藏'}隐藏文件")
                return is_showing
            else:
                command = 'defaults read com.apple.finder AppleShowAllFiles'
                result = subprocess.run(command, shell=True,
                                     capture_output=True, text=True)
                return result.stdout.strip().lower() == 'true'
        except Exception as e:
            self.logger.error(f"获取隐藏文件状态时出错: {e}")
            return True  # 出错时默认返回True，确保安全

    def set_show_hidden_files(self, show):
        """设置隐藏文件显示状态"""
        self.logger.info(f"正在设置为{'显示' if show else '隐藏'}隐藏文件...")
        try:
            if self.system == 'Windows':
                return self._set_windows_hidden_files(show)
            else:
                return self._set_mac_hidden_files(show)
        except Exception as e:
            self.logger.error(f"设置隐藏文件显示状态时出错: {e}")
            return False

    def _set_windows_hidden_files(self, show):
        """Windows 系统设置隐藏文件"""
        # 修改注册表
        command = f'Set-ItemProperty -Path "HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" -Name "Hidden" -Value {1 if show else 2}'
        
        self.logger.debug(f"执行命令: {command}")
        if not self.run_command(command):
            self.logger.error("修改 Windows 设置失败")
            return False

        # 刷新 Explorer
        refresh_commands = [
            # 通过 COM 对象刷新
            '''
            $shell = New-Object -ComObject Shell.Application
            $shell.Windows() | ForEach-Object {
                $_.Refresh()
            }
            ''',
            # 发送刷新消息
            '''
            $signature = @'
            [DllImport("user32.dll", SetLastError = true)]
            public static extern IntPtr SendMessageTimeout(
                IntPtr hWnd, uint Msg, UIntPtr wParam, IntPtr lParam,
                uint fuFlags, uint uTimeout, out UIntPtr lpdwResult);
            '@
            $type = Add-Type -MemberDefinition $signature -Name WinAPI -Namespace Win32 -PassThru
            $HWND_BROADCAST = [IntPtr]0xffff
            $WM_SETTINGCHANGE = 0x1A
            $result = [UIntPtr]::Zero
            $type::SendMessageTimeout($HWND_BROADCAST, $WM_SETTINGCHANGE, [UIntPtr]::Zero, [IntPtr]::Zero, 2, 5000, [ref]$result)
            '''
        ]
        
        success = True
        for cmd in refresh_commands:
            self.logger.debug("执行刷新命令...")
            if not self.run_command(cmd):
                self.logger.warning("刷新命令执行失败，尝试下一个...")
                success = False
            else:
                success = True
                break
        
        return success

    def _set_mac_hidden_files(self, show):
        """Mac 系统设置隐藏文件"""
        command = f'defaults write com.apple.finder AppleShowAllFiles {str(show).lower()}'
        
        self.logger.info("正在修改 Mac 设置...")
        if not self.run_command(command):
            self.logger.error("修改 Mac 设置失败")
            return False

        self.logger.info("正在重启 Finder...")
        return self.run_command('killall Finder')

    def restore_initial_state(self):
        """恢复初始状态"""
        self.logger.info(f"正在恢复到初始状态: {'显示' if self.initial_show_hidden else '隐藏'}隐藏文件")
        result = self.set_show_hidden_files(self.initial_show_hidden)
        if result:
            self.logger.info("成功恢复初始状态")
        else:
            self.logger.error("恢复初始状态失败")
        return result
    
    def _get_desktop_handles(self):
        """获取桌面相关的所有重要句柄"""
        handles = {}
        
        # 获取 Progman
        handles['progman'] = self.user32.FindWindowW("Progman", "Program Manager")
        
        # 获取 SHELLDLL_DefView
        if handles['progman']:
            handles['defview'] = self.user32.FindWindowExW(handles['progman'], None, "SHELLDLL_DefView", None)
            if handles['defview']:
                # 获取 SysListView32
                handles['listview'] = self.user32.FindWindowExW(handles['defview'], None, "SysListView32", "FolderView")
        
        # 尝试从 WorkerW 获取
        workerw = self.user32.FindWindowW("WorkerW", None)
        while workerw:
            shell = self.user32.FindWindowExW(workerw, None, "SHELLDLL_DefView", None)
            if shell:
                handles['workerw_defview'] = shell
                handles['workerw_listview'] = self.user32.FindWindowExW(shell, None, "SysListView32", "FolderView")
                break
            workerw = self.user32.FindWindowExW(None, workerw, "WorkerW", None)
        
        return handles

    def refresh_desktop(self):
        """刷新桌面"""
        try:
            if self.system == 'Windows':
                handles = self._get_desktop_handles()
                self.logger.debug(f"获取到的窗口句柄: {handles}")
                
                result = wintypes.DWORD()
                success = False
                
                # 定义所有可能的刷新消息
                refresh_messages = [
                    (0x0111, 0xA220, 0),  # WM_COMMAND with refresh
                    (0x0111, 0x7103, 0),  # Another refresh command
                    (0x0F, 0, 0),         # WM_PAINT
                    (0x001A, 0, 0)        # WM_SETTINGCHANGE
                ]
                
                # 对每个句柄尝试所有刷新消息
                for handle_name, hwnd in handles.items():
                    if not hwnd:
                        continue
                        
                    self.logger.debug(f"尝试刷新 {handle_name} (句柄: {hwnd})")
                    for msg, wparam, lparam in refresh_messages:
                        try:
                            ret = self.user32.SendMessageTimeoutW(
                                hwnd,
                                msg,
                                wparam,
                                lparam,
                                0x0002,  # SMTO_ABORTIFHUNG
                                1000,    # 1秒超时
                                ctypes.byref(result)
                            )
                            if ret:
                                success = True
                                self.logger.debug(f"成功发送消息到 {handle_name} (消息: 0x{msg:X})")
                        except Exception as e:
                            self.logger.error(f"发送消息失败: {e}")
                
                # 短暂延迟确保刷新完成
                if success:
                    time.sleep(0.1)
                return success
            else:
                return self.run_command('killall Finder')
                
        except Exception as e:
            self.logger.error(f"刷新桌面时出错: {e}")
            return False