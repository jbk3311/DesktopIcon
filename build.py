import os
import subprocess
import shutil
from src.config import APP_NAME, APP_VERSION, APP_AUTHOR, APP_COPYRIGHT, APP_DESCRIPTION

def clean_build():
    """清理旧的构建文件"""
    build_dirs = [
        'build',
        'dist',
        '__pycache__',
        'main.build',
        'main.dist',
        'main.onefile-build'
    ]
    
    for dir_name in build_dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理: {dir_name}")

def build_exe():
    """使用 Nuitka 构建可执行文件"""
    try:
        # 清理旧文件
        clean_build()
        
        # Nuitka 打包命令
        cmd = [
            "python", "-m", "nuitka",
            "--windows-console-mode=disable",      # 禁用控制台
            "--windows-uac-admin",           # 请求管理员权限
            "--windows-icon-from-ico=src/resources/icon.ico",  # 设置图标
            "--include-data-dir=src/resources=resources",  # 包含资源文件夹
            "--follow-imports",              # 自动包含导入的模块
            "--onefile",                     # 生成单个文件
            "--enable-plugin=tk-inter",      # 支持 tkinter
            "--include-package=win32api",    # 包含 win32api
            "--include-package=win32con",    # 包含 win32con
            "--output-dir=dist",             # 输出目录
            f"--output-filename=桌面图标管理器v{APP_VERSION}.exe",  # 输出文件名
            "--assume-yes-for-downloads",    # 自动下载依赖
            "--remove-output",               # 移除中间文件

            f"--company-name={APP_AUTHOR}",           # 公司名称
            f"--product-name=DesktopIconManager",         # 产品名称
            f"--product-version={APP_VERSION}",            # 产品版本
            f"--file-version={APP_VERSION}",               # 文件版本
            f"--file-description={APP_DESCRIPTION}",   # 文件描述
            f"--copyright={APP_COPYRIGHT}",    # 版权信息
            "main.py"                        # 主程序文件
        ]

        # 设置环境变量以确保正确的编码
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        
        # 执行打包命令
        subprocess.run(cmd, check=True, env=env)
        
        print("\n构建成功！")
        print("可执行文件位于: dist/桌面图标管理器.exe")
        
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    build_exe() 