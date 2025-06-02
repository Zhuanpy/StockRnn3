import os
from pathlib import Path
from App.static import file_root
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def ensure_data_directories():
    """
    确保所有必要的数据目录都存在
    """
    base_dir = os.path.join(file_root(), 'data')
    
    # 定义需要创建的目录结构
    directories = [
        # 原始数据目录
        os.path.join(base_dir, 'raw', 'stock', '1m'),
        os.path.join(base_dir, 'raw', 'stock', 'daily'),
        os.path.join(base_dir, 'raw', 'stock', 'real_time'),
        os.path.join(base_dir, 'raw', 'funds'),
        os.path.join(base_dir, 'raw', 'index'),
        
        # 处理后的数据目录
        os.path.join(base_dir, 'processed', 'features'),
        os.path.join(base_dir, 'processed', 'signals'),
        os.path.join(base_dir, 'processed', 'indicators'),
        
        # 模型相关目录
        os.path.join(base_dir, 'models', 'trained'),
        os.path.join(base_dir, 'models', 'checkpoints'),
        os.path.join(base_dir, 'models', 'predictions'),
        
        # 临时数据目录
        os.path.join(base_dir, 'temp'),
    ]
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"创建目录: {directory}")
        except Exception as e:
            logger.error(f"创建目录失败 {directory}: {str(e)}")
            raise

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
    month = f"{now.month:02d}"
    
    # 构建路径
    base_dir = os.path.join(file_root(), 'data', 'raw', 'stock', data_type, year, month)
    
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
    base_dir = os.path.join(file_root(), 'data', 'processed', data_type)
    
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
    base_dir = os.path.join(file_root(), 'data', 'models', model_type)
    
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
    base_dir = os.path.join(file_root(), 'data', 'temp')
    
    if create and not os.path.exists(base_dir):
        os.makedirs(base_dir)
        logger.info(f"创建目录: {base_dir}")
    
    return os.path.join(base_dir, filename) 