import os
import datetime
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_current_quarter():
    """获取当前季度"""
    now = datetime.datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year}Q{quarter}"

def create_stock_dirs(base_path, start_quarter=None, end_quarter=None):
    """
    创建股票数据目录结构
    :param base_path: 基础路径
    :param start_quarter: 起始季度（格式：YYYYQN，例如2024Q1）
    :param end_quarter: 结束季度（格式：YYYYQN，例如2024Q4）
    """
    # 数据类型目录
    data_types = ['1m', '15m', 'day', 'funds_awkward']
    
    # 如果没有指定季度，使用当前季度
    if not start_quarter:
        start_quarter = get_current_quarter()
    if not end_quarter:
        end_quarter = get_current_quarter()
        
    # 解析季度
    try:
        start_year = int(start_quarter[:4])
        start_q = int(start_quarter[5])
        end_year = int(end_quarter[:4])
        end_q = int(end_quarter[5])
        
        if start_year > end_year or (start_year == end_year and start_q > end_q):
            logger.error("起始季度不能大于结束季度")
            return
    except (ValueError, IndexError):
        logger.error("季度格式错误，应为YYYYQN格式，例如2024Q1")
        return
        
    # 创建目录
    base_path = Path(base_path)
    current_year = start_year
    current_q = start_q
    
    while current_year < end_year or (current_year == end_year and current_q <= end_q):
        quarter = f"{current_year}Q{current_q}"
        quarter_path = base_path / 'quarters' / quarter
        
        # 创建季度目录
        try:
            # 创建季度目录
            quarter_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建季度目录: {quarter_path}")
            
            # 创建数据类型目录
            for data_type in data_types:
                data_type_path = quarter_path / data_type
                data_type_path.mkdir(exist_ok=True)
                logger.info(f"创建数据类型目录: {data_type_path}")
                
        except Exception as e:
            logger.error(f"创建目录时出错: {e}")
            return
            
        # 更新季度
        current_q += 1
        if current_q > 4:
            current_q = 1
            current_year += 1
            
    logger.info("目录创建完成")

def verify_dirs(base_path, quarter=None):
    """
    验证目录结构是否完整
    :param base_path: 基础路径
    :param quarter: 要验证的特定季度（可选）
    """
    base_path = Path(base_path)
    data_types = ['1m', '15m', 'day', 'funds_awkward']
    missing_dirs = []
    
    quarters_path = base_path / 'quarters'
    if not quarters_path.exists():
        logger.warning(f"quarters目录不存在: {quarters_path}")
        return
        
    if quarter:
        quarters_to_check = [quarter]
    else:
        quarters_to_check = [q.name for q in quarters_path.iterdir() if q.is_dir()]
        
    for quarter in quarters_to_check:
        quarter_path = quarters_path / quarter
        if not quarter_path.exists():
            missing_dirs.append(str(quarter_path))
            continue
            
        for data_type in data_types:
            data_type_path = quarter_path / data_type
            if not data_type_path.exists():
                missing_dirs.append(str(data_type_path))
                
    if missing_dirs:
        logger.warning("发现缺失的目录:")
        for dir_path in missing_dirs:
            logger.warning(f"  - {dir_path}")
    else:
        logger.info("所有目录结构完整")

if __name__ == "__main__":
    # 示例用法
    import argparse
    
    parser = argparse.ArgumentParser(description='创建股票数据目录结构')
    parser.add_argument('--path', type=str, default='data/data',
                        help='基础路径，默认为 data/data')
    parser.add_argument('--start', type=str,
                        help='起始季度，格式：YYYYQN，例如 2024Q1')
    parser.add_argument('--end', type=str,
                        help='结束季度，格式：YYYYQN，例如 2024Q4')
    parser.add_argument('--verify', action='store_true',
                        help='验证目录结构')
    parser.add_argument('--quarter', type=str,
                        help='要验证的特定季度')
    
    args = parser.parse_args()
    
    if args.verify:
        verify_dirs(args.path, args.quarter)
    else:
        create_stock_dirs(args.path, args.start, args.end) 