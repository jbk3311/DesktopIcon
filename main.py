# main.py
import sys
import os
import ctypes
import win32con
from src.gui.main_window import DesktopIconManagerGUI
from src.utils.logger import setup_logger

def is_admin():
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_python_executable():
    """获取正确的Python解释器路径"""
    if getattr(sys, 'frozen', False):
        # 如果是打包后的exe
        return sys.executable
    else:
        # 如果是.py文件，使用当前Python解释器
        return sys.executable

def elevate_privileges():
    """提升到管理员权限"""
    try:
        if not is_admin():
            # 获取当前脚本的完整路径
            script = os.path.abspath(sys.argv[0])
            python_exe = get_python_executable()
            
            print(f"Using Python: {python_exe}")
            print(f"Script path: {script}")
            
            # 构建命令行参数
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            
            # 使用 ShellExecute 请求管理员权限
            ret = ctypes.windll.shell32.ShellExecuteW(
                None,
                "runas",
                python_exe,
                f'"{script}" {params}',
                os.path.dirname(script),
                1  # SW_SHOWNORMAL
            )
            
            if ret <= 32:
                raise Exception(f"ShellExecute failed with code {ret}")
            
            return True
            
    except Exception as e:
        print(f"权限提升失败: {str(e)}")
        return False
    
def set_app_id():
    appid = 'meitool.cn.DesktopIcon.1.0.0'  # 自定义唯一ID格式
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
   # time.sleep(1)
    # messagebox.showerror("错误", "错误")
    # ctypes.windll.user32.MessageBoxW(
    #                 None,
    #                 "注意事项：\n1. 需要管理员权限才能运行本程序\n2. 修改后可能需要刷新才能看到效果\n3. 如果程序异常中断导致图标消失，请重新运行程序然后打开显示即可",
    #                 "使用说明",
    #                 win32con.MB_OK | win32con.MB_ICONINFORMATION
    #             )

def main():
    if not is_admin():
        # 显示 UAC 提示
        result = ctypes.windll.user32.MessageBoxW(
            None,
            "需要管理员权限才能完全控制桌面图标。\n是否以管理员身份重新运行程序？",
            "权限请求",
            win32con.MB_YESNO | win32con.MB_ICONQUESTION
        )
        
        if result == win32con.IDYES:
            if elevate_privileges():
                print("正在以管理员身份重启程序...")
                sys.exit(0)
            else:
                ctypes.windll.user32.MessageBoxW(
                    None,
                    "无法获取管理员权限，某些功能可能受限。",
                    "警告",
                    win32con.MB_OK | win32con.MB_ICONWARNING
                )
    
    # 再次检查权限
    if not is_admin():
        print("警告: 程序未以管理员身份运行，某些功能可能受限")
    else:
        print("程序已以管理员身份运行")
    
    app = DesktopIconManagerGUI()
    app.run()

if __name__ == "__main__":
    # 初始化日志系统
    setup_logger()

    set_app_id()
    # 启动应用
    main()