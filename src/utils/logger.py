import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """配置全局日志系统"""
    try:
        # 创建日志目录
        log_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "DesktopIconManager", "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置日志文件
        log_file = os.path.join(log_dir, "app.log")
        
        # 创建日志处理器
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=1024 * 1024,  # 1MB
            backupCount=3,
            encoding='utf-8'
        )
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # 配置根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)  # 生产环境使用 INFO 级别
        
        # 清除现有的处理器
        root_logger.handlers = []
        
        # 添加文件处理器
        root_logger.addHandler(file_handler)
        
    except Exception as e:
        print(f"日志系统初始化失败: {e}")
        # 使用空处理器作为后备
        root_logger = logging.getLogger()
        root_logger.addHandler(logging.NullHandler())

# 初始化日志系统
setup_logger()

# 为不同模块创建日志器
def get_logger(name):
    """获取指定名称的日志器"""
    return logging.getLogger(name)
