"""
全局配置文件
"""

# 软件信息
APP_NAME = "桌面图标管理器"
APP_VERSION = "1.0.0"
APP_AUTHOR = "meitool.cn"
APP_COPYRIGHT = "Copyright (c) 2024"
APP_DESCRIPTION = "一个用于管理Windows桌面图标的工具"

# 调试模式
DEBUG = False

# 文件路径配置
import os
import sys
from pathlib import Path

def detect_environment():
    """通过文件系统特征判断"""
    dev_markers = [
        Path("requirements.txt").exists(),  # 开发依赖文件
        Path(".git").is_dir(),                  # 版本控制目录
        # Path("tests").is_dir()                 # 测试目录
    ]
    return "dev" if any(dev_markers) else "pro"

def get_icon_path():
    """ 获取资源绝对路径 """
    if detect_environment() == "dev":
        icon_path = os.path.join(os.path.dirname(__file__),  "resources", "icon.ico")
    else:
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        #tmp_path = base_path.replace("gui", "")
        tmp2_path = base_path.replace("src", "resources")
        icon_path = os.path.join(tmp2_path, "icon.ico")

    return icon_path
    
# 资源文件路径
ICON_PATH = get_icon_path()
LOG_PATH = os.path.join(os.getenv('APPDATA'), APP_NAME, 'logs')

# 应用设置
DEFAULT_SETTINGS = {
    "auto_start": False,
    "minimize_to_tray": True,
    "check_updates": True
}

# API 配置
API_VERSION = "v1"
API_BASE_URL = "https://api.example.com"  # 如果有在线服务

# 其他常量
MAX_RETRY_COUNT = 3
REFRESH_INTERVAL = 5000  # 毫秒