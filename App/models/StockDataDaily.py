from ..exts import db
import pandas as pd
from sqlalchemy.exc import IntegrityError

daily_model_cache = {}  # 缓存动态生成的模型类


def create_daily_stock_model(stock_code):
    """
    动态生成按天储存的股票数据模型，表格命名为股票代码。
    """

    # 缓存键：基于股票代码
    cache_key = stock_code

    # 如果模型类已缓存，则直接返回
    if cache_key in daily_model_cache:
        return daily_model_cache[cache_key]

    # 构造唯一的类名
    class_name = f"DailyStockData_{stock_code}"

    # 动态定义类
    DailyStockData = type(
        class_name,
        (db.Model,),  # 继承 db.Model
        {
            "__tablename__": f"{stock_code}",  # 表名即为股票代码
            "__bind_key__": "datadaily",  # 绑定到 datadaily 数据库

            # 核心字段定义
            "date": db.Column(db.Date, primary_key=True, nullable=False),
            "open": db.Column(db.Float, nullable=False),
            "close": db.Column(db.Float, nullable=False),
            "high": db.Column(db.Float, nullable=False),
            "low": db.Column(db.Float, nullable=False),
            "volume": db.Column(db.Integer, nullable=False),
            "money": db.Column(db.Integer, nullable=False),

            # 补充的字段15分钟K线数据趋势信息
            "trends": db.Column(db.Integer, nullable=True, default=1),
            "signal_times": db.Column(db.Text, nullable=True),
            "signal_start_time": db.Column(db.Text, nullable=True),
            "re_trend": db.Column(db.Integer, nullable=True, default=1),

            # 补充的字段15分钟K线周期信息
            "cycle_amplitude_per_bar": db.Column(db.Float, nullable=True, default=0),
            "cycle_amplitude_max": db.Column(db.Float, nullable=True, default=0),
            "cycle_1m_vol_max1": db.Column(db.Integer, nullable=True, default=0),
            "cycle_1m_vol_max5": db.Column(db.Integer, nullable=True, default=0),
            "cycle_length_per_bar": db.Column(db.Integer, nullable=True, default=0),

            # 补充的字段15分钟K线预测周期信息
            "predict_cycle_length": db.Column(db.Integer, nullable=True, default=0),
            "predict_cycle_change": db.Column(db.Float, nullable=True, default=0),
            "predict_cycle_price": db.Column(db.Float, nullable=True, default=0),
            "predict_bar_change": db.Column(db.Float, nullable=True, default=0),
            "predict_bar_price": db.Column(db.Float, nullable=True, default=0),
            "predict_bar_volume": db.Column(db.Integer, nullable=True, default=0),

            # 补充的字段15分钟K线预测周期得分信息
            "score_rnn_model": db.Column(db.Float, nullable=True, default=0),
            "score_board_boll": db.Column(db.Float, nullable=True, default=0),
            "score_board_money": db.Column(db.Float, nullable=True, default=0),
            "score_board_hot": db.Column(db.Float, nullable=True, default=0),
            "score_funds_awkward": db.Column(db.Float, nullable=True, default=0),
            "trend_probability": db.Column(db.Float, nullable=True, default=0),
            "rnn_model_score": db.Column(db.Float, nullable=True, default=0),
            "cycle_amplitude": db.Column(db.Float, nullable=True, default=0),

            # 补充的字段持仓&交易信息
            "position": db.Column(db.Integer, nullable=True, default=1),
            "position_num": db.Column(db.Float, nullable=True, default=0),
            "stop_loss": db.Column(db.Float, nullable=True, default=0),
        }
    )

    # 缓存生成的类
    daily_model_cache[cache_key] = DailyStockData

    return DailyStockData


def save_daily_stock_data_to_sql(stock_code, data: pd.DataFrame):
    """
    将股票按天数据保存至 datadaily 数据库中，按股票代码创建表格。

    参数：
    - stock_code (str): 股票代码
    - code_data (pd.DataFrame): 每天的股票数据 DataFrame，每行包含 date、open_price 等列
    """
    # 动态创建模型类
    DailyStockModel = create_daily_stock_model(stock_code)

    # 将 DataFrame 转换为模型对象列表
    daily_stock_records = []

    for _, row in data.iterrows():
        record = DailyStockModel(
            date=row['date'],
            open=row['open'],
            close=row['close'],
            high=row['high'],
            low=row['low'],
            volume=row['volume'],
            money=row['money'],

            # 为新增字段设置默认值
            trends=row.get('trends', 1),
            signal_times=row.get('signal_times', None),
            signal_start_time=row.get('signal_start_time', None),
            re_trend=row.get('re_trend', 1),
            cycle_amplitude_per_bar=row.get('cycle_amplitude_per_bar', 0),
            cycle_amplitude_max=row.get('cycle_amplitude_max', 0),
            cycle_1m_vol_max1=row.get('cycle_1m_vol_max1', 0),
            cycle_1m_vol_max5=row.get('cycle_1m_vol_max5', 0),
            cycle_length_per_bar=row.get('cycle_length_per_bar', 0),
            predict_cycle_length=row.get('predict_cycle_length', 0),
            predict_cycle_change=row.get('predict_cycle_change', 0),
            predict_cycle_price=row.get('predict_cycle_price', 0),
            predict_bar_change=row.get('predict_bar_change', 0),
            predict_bar_price=row.get('predict_bar_price', 0),
            predict_bar_volume=row.get('predict_bar_volume', 0),
            score_rnn_model=row.get('score_rnn_model', 0),
            score_board_boll=row.get('score_board_boll', 0),
            score_board_money=row.get('score_board_money', 0),
            score_board_hot=row.get('score_board_hot', 0),
            score_funds_awkward=row.get('score_funds_awkward', 0),
            trend_probability=row.get('trend_probability', 0),
            rnn_model_score=row.get('rnn_model_score', 0),
            cycle_amplitude=row.get('cycle_amplitude', 0),
            position=row.get('position', 0),
            position_num=row.get('position_num', 0),
            stop_loss=row.get('stop_loss', 0),
        )
        daily_stock_records.append(record)

    # 批量插入到数据库
    try:
        db.session.add_all(daily_stock_records)
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()  # 回滚事务，避免锁定数据库
        print(f"Error: {e}")  # 可根据需要记录日志或处理冲突逻辑
