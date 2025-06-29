"""
基金重仓数据模型
提供动态创建基金重仓数据表的功能
"""
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy.exc import SQLAlchemyError
from App.exts import db
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def create_funds_holdings_table(table_name: str):
    """
    动态生成基金重仓股票数据模型，并保存到按日期命名的 MySQL 表中。

    Args:
        table_name: 表名，通常为日期格式如 '2024-11-17'
        
    Returns:
        Table: 创建的表对象
    """
    try:
        # 确保运行在 Flask 应用上下文中
        metadata = MetaData()

        fund_table = Table(
            table_name,
            metadata,
            Column('id', Integer, primary_key=True, autoincrement=True, comment='主键ID'),
            Column('fund_name', String(255), comment='基金名称'),
            Column('fund_code', String(50), comment='基金代码'),
            Column('stock_name', String(255), comment='股票名称'),
            Column('stock_code', String(50), comment='股票代码'),
            Column('holdings_ratio', String(20), comment='持仓比例'),
            Column('market_value', String(50), comment='市值'),
            Column('shares', String(50), comment='持股数量'),
        )

        # 使用指定的数据库引擎创建表
        engine = db.get_engine(bind='funds_awkward')  # 绑定到 'funds_awkward' 数据库
        metadata.create_all(engine, checkfirst=True)  # 确保表已创建
        
        logger.info(f"成功创建基金重仓数据表: {table_name}")
        return fund_table
        
    except Exception as e:
        logger.error(f"创建基金重仓数据表 {table_name} 时发生错误: {e}")
        raise


def save_funds_holdings_to_sql(table_name: str, df: pd.DataFrame) -> bool:
    """
    将基金数据保存到指定的数据库表中。
    
    Args:
        table_name: 数据库表名
        df: pandas.DataFrame 数据框，包含需要插入的数据
        
    Returns:
        bool: 保存是否成功
    """
    try:
        # 动态创建表
        table = create_funds_holdings_table(table_name)

        # 将 DataFrame 转换为字典列表
        data = df.to_dict(orient='records')

        # 获取数据库引擎并使用事务块
        engine = db.get_engine(bind='funds_awkward')
        with engine.begin() as connection:
            # 批量插入数据
            connection.execute(table.insert(), data)
            
        logger.info(f"成功保存基金重仓数据到表 {table_name}，共 {len(data)} 条记录")
        return True

    except SQLAlchemyError as e:
        logger.error(f"保存基金重仓数据到表 {table_name} 时发生数据库错误: {e}")
        return False
    except Exception as e:
        logger.error(f"保存基金重仓数据到表 {table_name} 时发生未知错误: {e}")
        return False


def get_funds_holdings_from_sql(table_name: str) -> pd.DataFrame:
    """
    从指定的数据库表中获取基金重仓数据。
    
    Args:
        table_name: 数据库表名
        
    Returns:
        pd.DataFrame: 基金重仓数据
    """
    try:
        # 获取数据库引擎
        engine = db.get_engine(bind='funds_awkward')
        
        # 查询数据
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, engine)
        
        logger.info(f"成功从表 {table_name} 获取基金重仓数据，共 {len(df)} 条记录")
        return df
        
    except Exception as e:
        logger.error(f"从表 {table_name} 获取基金重仓数据时发生错误: {e}")
        return pd.DataFrame()


def get_funds_holdings_by_stock(table_name: str, stock_code: str) -> pd.DataFrame:
    """
    从指定的数据库表中获取特定股票的基金重仓数据。
    
    Args:
        table_name: 数据库表名
        stock_code: 股票代码
        
    Returns:
        pd.DataFrame: 特定股票的基金重仓数据
    """
    try:
        # 获取数据库引擎
        engine = db.get_engine(bind='funds_awkward')
        
        # 查询特定股票的数据
        query = f"SELECT * FROM {table_name} WHERE stock_code = '{stock_code}'"
        df = pd.read_sql(query, engine)
        
        logger.info(f"成功从表 {table_name} 获取股票 {stock_code} 的基金重仓数据，共 {len(df)} 条记录")
        return df
        
    except Exception as e:
        logger.error(f"从表 {table_name} 获取股票 {stock_code} 的基金重仓数据时发生错误: {e}")
        return pd.DataFrame()


def get_funds_holdings_by_fund(table_name: str, fund_code: str) -> pd.DataFrame:
    """
    从指定的数据库表中获取特定基金的持仓数据。
    
    Args:
        table_name: 数据库表名
        fund_code: 基金代码
        
    Returns:
        pd.DataFrame: 特定基金的持仓数据
    """
    try:
        # 获取数据库引擎
        engine = db.get_engine(bind='funds_awkward')
        
        # 查询特定基金的数据
        query = f"SELECT * FROM {table_name} WHERE fund_code = '{fund_code}'"
        df = pd.read_sql(query, engine)
        
        logger.info(f"成功从表 {table_name} 获取基金 {fund_code} 的持仓数据，共 {len(df)} 条记录")
        return df
        
    except Exception as e:
        logger.error(f"从表 {table_name} 获取基金 {fund_code} 的持仓数据时发生错误: {e}")
        return pd.DataFrame()
