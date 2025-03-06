from sqlalchemy import Table, Column, Integer, String,  MetaData
from sqlalchemy.exc import SQLAlchemyError
from ..exts import db


def download_funds_holdings(table_name):
    """
    动态生成基金重仓股票分时数据模型，并保存到按日期命名的 MySQL 表中。

    :param download_date: str 下载日期，格式如 '2024-11-17'，用作表名
    """
    # 确保运行在 Flask 应用上下文中
    metadata = MetaData()

    fund_table = Table(
        table_name,
        metadata,
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('fund_name', String(255)),  # 最大长度 255
        Column('fund_code', String(50)),   # 最大长度 50
        Column('stock_name', String(255)),
        Column('stock_code', String(50)),

    )

    # 使用指定的数据库引擎创建表
    engine = db.get_engine(bind='funds_awkward')  # 绑定到 'funds_awkward' 数据库
    metadata.create_all(engine, checkfirst=True)  # 确保表已创建
    return fund_table


def funds_holdings_to_sql(table_name, df):
    """
    将基金数据保存到指定的数据库表中。
    :param table_name: str 数据库表名
    :param df: pandas.DataFrame 数据框，包含需要插入的数据
    """
    try:
        # 动态创建表
        table = download_funds_holdings(table_name)

        # 将 DataFrame 转换为字典列表
        data = df.to_dict(orient='records')

        # 获取数据库引擎并使用事务块
        engine = db.get_engine(bind='funds_awkward')
        with engine.begin() as connection:
            # 批量插入数据
            connection.execute(table.insert(), data)

    except SQLAlchemyError as e:
        raise RuntimeError(f"保存数据失败: {e}")
