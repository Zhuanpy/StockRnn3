import pandas as pd

from ..exts import db

# 缓存动态生成的模型类
model_cache = {}


def create_1m_stock_model(stock_code, year):
    """
    动态生成股票分时数据模型，根据股票代码和年份创建表名。
    """
    # 缓存键：基于股票代码和年份
    cache_key = (stock_code, year)

    if cache_key in model_cache:
        return model_cache[cache_key]

    # 构造唯一的类名
    class_name = f"TimeSeriesData_{stock_code}_{year}"

    # 动态定义类
    TimeSeriesData = type(
        class_name,
        (db.Model,),
        {
            '__tablename__': f"{stock_code}",
            '__bind_key__': f"data1m{year}",
            'date': db.Column(db.DateTime, primary_key=True, nullable=False),
            'open': db.Column(db.Float, nullable=False),
            'close': db.Column(db.Float, nullable=False),
            'high': db.Column(db.Float, nullable=False),
            'low': db.Column(db.Float, nullable=False),
            'volume': db.Column(db.Integer, nullable=False),
            'money': db.Column(db.Integer, nullable=False),
        },
    )

    # 缓存生成的类
    model_cache[cache_key] = TimeSeriesData

    return TimeSeriesData


def save_1m_stock_data_to_sql(stock_code, year, data: pd.DataFrame):
    """
    将股票分时数据保存至按年份和股票代码划分的数据库表中。

    参数：
    - stock_code (str): 股票代码
    - year (int): 年份
    - data (pd.DataFrame): 股票分时数据的 DataFrame，每行包含 date、open、close 等字段
    """
    # 动态创建模型类
    StockModel = create_1m_stock_model(stock_code, year)

    # 将 DataFrame 转为字典列表
    records = data.to_dict(orient='records')

    # 获取已存在的日期
    existing_dates = {record.date for record in StockModel.query.with_entities(StockModel.date).all()}

    # 拆分插入与更新
    new_records = []
    for record in records:
        if record['date'] in existing_dates:
            # 更新已有记录
            StockModel.query.filter_by(date=record['date']).update(record)
        else:
            # 收集需要插入的新记录
            new_records.append(StockModel(**record))

    # 批量插入新记录
    if new_records:
        db.session.bulk_save_objects(new_records)

    # 提交事务
    db.session.commit()


def load_1m_stock_data_from_sql_efficient(stock_code, year):
    """
    高效地从按年份和股票代码划分的数据库表中加载股票分时数据到Pandas DataFrame中。

    参数：
    - stock_code (str): 股票代码
    - year (int): 年份

    返回：
    - pd.DataFrame: 包含股票分时数据的DataFrame
    """
    StockModel = create_1m_stock_model(stock_code, year)

    # 使用yield_per分批加载数据以减少内存使用
    query = StockModel.query.yield_per(1000)  # 每次从数据库获取1000条记录

    # 创建一个空的DataFrame来存储结果
    df = pd.DataFrame()

    # 遍历查询结果并添加到DataFrame中
    for record in query:
        # 转换为字典并移除不需要的键
        record_dict = record.__dict__
        record_dict = {k: v for k, v in record_dict.items() if not k.startswith('_')}
        # 创建一个临时的DataFrame并追加到主DataFrame中
        temp_df = pd.DataFrame([record_dict])
        df = pd.concat([df, temp_df], ignore_index=True)

    # 如果数据库中的日期是datetime对象，确保DataFrame中的日期也是datetime类型
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])

    return df