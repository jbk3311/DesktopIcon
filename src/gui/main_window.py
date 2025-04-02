import tkinter as tk
from tkinter import ttk, messagebox
from ..core.icon_manager import IconManager
from .widgets import ScrollableIconFrame
import os
from ..utils.system_settings import SystemSettingsManager
from src.utils.logger import get_logger
import win32api
import win32con
from pathlib import Path
import sys
import ctypes
import win32gui
from ctypes import windll

from src.config import ICON_PATH,APP_VERSION
# 定义Windows API函数原型
user32 = ctypes.WinDLL('user32', use_last_error=True)
shell32 = ctypes.WinDLL('shell32', use_last_error=True)

# 常量定义
WM_SETICON = 0x0080
ICON_SMALL = 0
ICON_BIG = 1
SHCNE_ASSOCCHANGED = 0x08000000
SHCNF_IDLIST = 0x0000

class DesktopIconManagerGUI:
    def __init__(self):
        self.logger = get_logger(__name__)
        
        self.root = tk.Tk()
        self.root.title(f"桌面图标管理器 v{APP_VERSION}")
        self.root.geometry("550x600")
        self.root.minsize(550, 600)
        
        # 设置窗口图标
        try:
            # 假设图标文件在 src/resources/icon.ico
            # icon_path = self.get_icon_path()
            self.root.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"加载图标失败: {e}")

        try:
            # 获取窗口句柄
            hwnd = windll.user32.GetParent(self.root.winfo_id())
            
            # 获取图标句柄
            icon_handle = win32gui.LoadImage(
                0,
                ICON_PATH,  # 你的图标路径
                win32con.IMAGE_ICON,
                0,
                0,
                win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            )
            
            # 强制刷新任务栏图标
            self.force_taskbar_refresh(hwnd, icon_handle)
            
        except Exception as e:
            print(f"设置任务栏图标失败: {e}")
        
        # 初始化系统设置管理器
        try:
            self.settings_manager = SystemSettingsManager()
            if not self.settings_manager.is_admin():
                messagebox.showerror("错误", "请以管理员权限运行此程序！")
                self.root.destroy()
                return
                
            # 启动时设置为隐藏
            if not self.settings_manager.set_show_hidden_files(False):
                messagebox.showerror("错误", "无法修改系统隐藏文件设置")
                self.root.destroy()
                return
            else:
                # 刷新桌面
                self.settings_manager.refresh_desktop()
                
        except NotImplementedError as e:
            messagebox.showerror("错误", str(e))
            self.root.destroy()
            return
        
        # 设置窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.icon_manager = IconManager()
        self.create_widgets()
        self.refresh_icon_list()

    def force_taskbar_refresh(self, hwnd, icon_handle):
        """强制刷新任务栏图标"""
        try:
            # 发送多个刷新消息确保更新
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, icon_handle)
            win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_BIG, icon_handle)
            
            # 发送任务栏刷新消息
            win32gui.SendMessage(hwnd, win32con.WM_SETTINGCHANGE, 0, 0)
            
            # 强制重绘
            win32gui.RedrawWindow(
                hwnd, 
                None, 
                None, 
                win32con.RDW_INVALIDATE | win32con.RDW_UPDATENOW | win32con.RDW_FRAME
            )
            
            # 刷新系统任务栏
            taskbar_hwnd = win32gui.FindWindow("Shell_TrayWnd", None)
            if taskbar_hwnd:
                win32gui.SendMessage(taskbar_hwnd, win32con.WM_SETTINGCHANGE, 0, 0)
                win32gui.RedrawWindow(
                    taskbar_hwnd,
                    None,
                    None,
                    win32con.RDW_INVALIDATE | win32con.RDW_UPDATENOW | win32con.RDW_FRAME
                )
        except Exception as e:
            print(f"刷新任务栏图标失败: {e}")

    def on_closing(self):
        """程序关闭时的处理"""
        try:
            # 恢复初始状态
            if not self.settings_manager.restore_initial_state():
                messagebox.showerror("错误", "恢复系统设置失败")
        except Exception as e:
            messagebox.showerror("错误", f"恢复系统设置时出错: {e}")
        finally:
            self.root.destroy()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="桌面图标管理工具", 
            font=("微软雅黑", 10, "bold")
        )
        title_label.pack(pady=3)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10, fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="隐藏选中",
            command=lambda: self.toggle_selected_icons(True),
            width=15
        ).grid(row=0, column=0, padx=5)
        
        ttk.Button(
            button_frame,
            text="显示选中",
            command=lambda: self.toggle_selected_icons(False),
            width=15
        ).grid(row=0, column=1, padx=5)
        
        ttk.Button(
            button_frame,
            text="刷新列表",
            command=self.refresh_icon_list,
            width=15
        ).grid(row=0, column=2, padx=5)

        ttk.Button(
            button_frame,
            text="使用说明",
            command=self.show_help,
            width=15
        ).grid(row=0, column=3, padx=5)
        
        # 图标列表框架
        self.icon_frame = ScrollableIconFrame(main_frame)
        self.icon_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def toggle_selected_icons(self, hide=True):
        selected_paths = self.icon_frame.get_selected_items()
        if not selected_paths:
            messagebox.showinfo("提示", "请先选择要操作的图标")
            return
        
        try:
            success_count, failed_paths = self.icon_manager.toggle_icons(selected_paths, hide)
            
            if failed_paths:
                # 检查是否有权限相关的错误
                permission_errors = [p for p, e in failed_paths if "权限" in e or "Access" in e]
                if permission_errors:
                    messagebox.showerror(
                        "权限不足",
                        "需要管理员权限才能操作以下图标：\n" +
                        "\n".join([os.path.basename(p) for p in permission_errors]) +
                        "\n\n请以管理员身份运行程序。"
                    )
                    return
                
                # 其他错误
                error_msg = "以下图标操作失败：\n\n"
                for path, error in failed_paths:
                    error_msg += f"• {os.path.basename(path)}\n  原因: {error}\n"
                
                if success_count > 0:
                    error_msg = f"成功操作 {success_count} 个图标。\n\n" + error_msg
                
                messagebox.showwarning("部分操作失败", error_msg)
            else:
                messagebox.showinfo(
                    "成功",
                    f"已{'隐藏' if hide else '显示'}所有选中的图标"
                )
            
            self.refresh_icon_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"操作失败：{str(e)}")
    
    def refresh_icon_list(self):
        icons = self.icon_manager.get_desktop_icons()
        self.icon_frame.update_icons(icons)
    
    def show_help(self):
        """显示使用说明"""
        help_text = """使用说明：

1. 使用说明：
   - 隐藏选中：将选中的图标设为隐藏状态
   - 显示选中：将选中的图标恢复显示状态
   - 刷新列表：更新图标列表显示

2. 注意事项：
   - 需要管理员权限才能运行本程序
   - 修改后可能需要刷新才能看到效果
   - 建议定期备份重要文件


"""
        
        # 创建说明窗口
        help_window = tk.Toplevel(self.root)
        help_window.title("使用说明")
        help_window.geometry("500x400")
        
        # 添加文本框
        text = tk.Text(help_window, wrap=tk.WORD, padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True)
        
        # 插入说明文本
        text.insert(tk.END, help_text)
        
        # 设置为只读
        text.config(state=tk.DISABLED)
        
        # 添加关闭按钮
        tk.Button(help_window, text="关闭", command=help_window.destroy).pack(pady=10)
        
        # 设置模态窗口（用户必须先关闭说明窗口才能操作主窗口）
        help_window.transient(self.root)
        help_window.grab_set()

    def hide_icons(self):
        """隐藏选中的图标"""
        paths = self.get_selected_paths()
        if not paths:
            self.logger.info("未选择任何图标")
            messagebox.showwarning("警告", "请先选择要隐藏的图标")
            return
        
        try:
            for path in paths:
                attrs = win32api.GetFileAttributes(path)
                win32api.SetFileAttributes(path, attrs | win32con.FILE_ATTRIBUTE_HIDDEN)
            
            self.logger.info(f"成功隐藏 {len(paths)} 个图标")
            self.refresh_icon_list()
            messagebox.showinfo("成功", "已成功隐藏选中的图标")
        except Exception as e:
            self.logger.error(f"隐藏图标时出错: {e}")
            messagebox.showerror("错误", f"隐藏图标时出错: {e}")

    def run(self):
        self.root.mainloop()