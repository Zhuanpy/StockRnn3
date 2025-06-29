import os
from pathlib import Path
from config import Config
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def ensure_data_directories():
    """
    确保所有必要的数据目录都存在
    """
    # 获取项目根目录
    base_dir = Path(Config.get_project_root())
    
    # 定义需要创建的目录
    directories = [
        base_dir / 'App' / 'codes' / 'code_data',
        base_dir / 'App' / 'codes' / 'code_data' / 'password',
        base_dir / 'App' / 'codes' / 'code_data' / 'password' / 'XueQiu',
        base_dir / 'App' / 'codes' / 'code_data' / 'password' / 'sql.txt',
        base_dir / 'App' / 'codes' / 'code_data' / 'password' / 'XueQiu' / 'cookies.txt',
        base_dir / 'App' / 'codes' / 'code_data' / 'password' / 'XueQiu' / 'headers.txt'
    ]
    
    # 创建目录
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {directory}")

def get_stock_data_path(stock_code: str, data_type: str = '1m', create: bool = True) -> str:
    """
    获取股票数据的存储路径
    
    Args:
        stock_code: 股票代码
        data_type: 数据类型，可选 '1m', 'daily', 'real_time'
        create: 是否创建目录
        
    Returns:
        str: 数据存储路径
    """
    # 获取当前年月
    now = datetime.now()
    year = str(now.year)
    
    # 计算季度
    quarter = (now.month - 1) // 3 + 1
    quarter_str = f"Q{quarter}"
    
    # 构建路径 - 按季度保存到 data/data/quarters
    base_dir = os.path.join(Config.get_project_root(), 'data', 'data', 'quarters', year, quarter_str)
    
    if create and not os.path.exists(base_dir):
        os.makedirs(base_dir)
        logger.info(f"创建目录: {base_dir}")
    
    return os.path.join(base_dir, f"{stock_code}.csv")

def get_processed_data_path(data_type: str, filename: str, create: bool = True) -> str:
    """
    获取处理后数据的存储路径
    
    Args:
        data_type: 数据类型，可选 'features', 'signals', 'indicators'
        filename: 文件名
        create: 是否创建目录
        
    Returns:
        str: 数据存储路径
    """
    base_dir = os.path.join(Config.get_project_root(), 'data', 'processed', data_type)
    
    if create and not os.path.exists(base_dir):
        os.makedirs(base_dir)
        logger.info(f"创建目录: {base_dir}")
    
    return os.path.join(base_dir, filename)

def get_model_path(model_type: str, filename: str, create: bool = True) -> str:
    """
    获取模型相关文件的存储路径
    
    Args:
        model_type: 模型类型，可选 'trained', 'checkpoints', 'predictions'
        filename: 文件名
        create: 是否创建目录
        
    Returns:
        str: 模型文件存储路径
    """
    base_dir = os.path.join(Config.get_project_root(), 'data', 'models', model_type)
    
    if create and not os.path.exists(base_dir):
        os.makedirs(base_dir)
        logger.info(f"创建目录: {base_dir}")
    
    return os.path.join(base_dir, filename)

def get_temp_path(filename: str, create: bool = True) -> str:
    """
    获取临时文件的存储路径
    
    Args:
        filename: 文件名
        create: 是否创建目录
        
    Returns:
        str: 临时文件存储路径
    """
    base_dir = os.path.join(Config.get_project_root(), 'data', 'temp')
    
    if create and not os.path.exists(base_dir):
        os.makedirs(base_dir)
        logger.info(f"创建目录: {base_dir}")
    
    return os.path.join(base_dir, filename) 