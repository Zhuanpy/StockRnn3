import os
from App.codes.MySql.DB_MySql import MysqlAlchemy as mysql
from App.codes.utils.Normal import ResampleData
from App.codes.MySql.DB_MySql import MysqlAlchemy
import pandas as pd
from App.utils.file_utils import get_stock_data_path, get_processed_data_path
from App.codes.MySql.DataBaseStockData1m import StockData1m
import logging
from config import Config

logger = logging.getLogger(__name__)

def save_1m_to_mysql(stock_code: str, year: str, data):
    """保存1分钟数据到MySQL数据库"""
    try:
        StockData1m.append_1m(stock_code, year, data)
        logger.info(f"成功保存1分钟数据到MySQL: {stock_code}")
        return True
    except Exception as e:
        logger.error(f"保存1分钟数据到MySQL失败: {stock_code}, 错误: {str(e)}")
        raise

def save_1m_to_csv(df, stock_code: str):
    """
    将1分钟级别的股票数据保存为CSV文件，按季度保存
    
    Args:
        df: 包含股票数据的DataFrame，需包含 'date' 列
        stock_code: 股票代码
    """
    try:
        # 确保日期列为datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])

        # 按季度分组保存数据
        for name, group in df.groupby(df['date'].dt.to_period('Q')):
            # 获取季度信息
            year = name.year
            quarter = (name.month - 1) // 3 + 1
            quarter_str = f"Q{quarter}"
            
            # 构建保存路径
            base_dir = os.path.join(Config.get_project_root(), 'data', 'data', 'quarters', str(year), quarter_str)
            file_path = os.path.join(base_dir, f"{stock_code}.csv")
            
            # 确保目录存在
            os.makedirs(base_dir, exist_ok=True)
            
            # 如果文件存在，读取并合并数据
            if os.path.exists(file_path):
                existing_data = pd.read_csv(file_path)
                existing_data['date'] = pd.to_datetime(existing_data['date'])
                combined_data = pd.concat([existing_data, group]).drop_duplicates(subset=['date'])
                combined_data = combined_data.sort_values('date')
            else:
                combined_data = group
            
            # 保存数据
            combined_data.to_csv(file_path, index=False)
            logger.info(f"成功保存1分钟数据到CSV: {stock_code}, 季度: {year}-{quarter_str}")
            
    except Exception as e:
        logger.error(f"保存1分钟数据到CSV失败: {stock_code}, 错误: {str(e)}")
        raise

def save_1m_to_daily(df, stock_code: str):
    """
    将1分钟数据转换并保存为日线数据
    
    Args:
        df: 1分钟数据DataFrame
        stock_code: 股票代码
    """
    try:
        # 转换为日线数据
        df_daily = ResampleData.resample_1m_data(df, 'd')
        
        # 保存到数据库
        database = 'datadaily'
        table = stock_code
        MysqlAlchemy.pd_append(df_daily, database, table)
        
        # 保存到CSV文件
        file_path = get_stock_data_path(stock_code, data_type='daily')
        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            existing_data['date'] = pd.to_datetime(existing_data['date'])
            combined_data = pd.concat([existing_data, df_daily]).drop_duplicates(subset=['date'])
            combined_data = combined_data.sort_values('date')
        else:
            combined_data = df_daily
            
        combined_data.to_csv(file_path, index=False)
        logger.info(f"成功保存日线数据: {stock_code}")
        return True
        
    except Exception as e:
        logger.error(f"保存日线数据失败: {stock_code}, 错误: {str(e)}")
        raise

if __name__ == '__main__':
    # 测试代码
    try:
        db = 'data1m2024'
        tb = '000001'
        data = mysql.pd_read(db, tb)
        save_1m_to_csv(data, tb)
        logger.info("测试完成")
    except Exception as e:
        logger.error(f"测试失败: {str(e)}")
