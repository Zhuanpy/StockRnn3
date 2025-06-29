import os
from config import Config

def file_root():
    """返回项目根目录路径"""
    return Config.get_project_root()

# 使用config中的路径配置
password_path = str(Config.get_password_path())