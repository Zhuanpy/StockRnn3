# """
# 股票日线数据模型
# 提供动态创建股票日线数据表的功能
# """
# from App.exts import db
# import pandas as pd
# from sqlalchemy.exc import IntegrityError
# from typing import Dict, Any, List
# import logging
#
# logger = logging.getLogger(__name__)
#
# # # 缓存动态生成的模型类
# # daily_model_cache: Dict[str, Any] = {}
#
# class StockDaily(db.Model):
#     __tablename__ = 'daily_stock_data'
#     __bind_key__ = 'datadaily'
#
# def create_daily_stock_model(stock_code: str):
#     """
#     动态生成按天储存的股票数据模型，表格命名为股票代码。
#
#     Args:
#         stock_code: 股票代码
#
#     Returns:
#         动态生成的模型类
#     """
#     # 缓存键：基于股票代码
#     cache_key = stock_code
#
#     # 如果模型类已缓存，则直接返回
#     if cache_key in daily_model_cache:
#         return daily_model_cache[cache_key]
#
#     # 构造唯一的类名
#     class_name = f"DailyStockData_{stock_code}"
#
#     # 动态定义类
#     DailyStockData = type(
#         class_name,
#         (db.Model,),  # 继承 db.Model
#         {
#             "__tablename__": f"{stock_code}",  # 表名即为股票代码
#             "__bind_key__": "datadaily",  # 绑定到 datadaily 数据库
#
#             # 核心字段定义
#             "date": db.Column(db.Date, primary_key=True, nullable=False, comment='交易日期'),
#             "open": db.Column(db.Float, nullable=False, comment='开盘价'),
#             "close": db.Column(db.Float, nullable=False, comment='收盘价'),
#             "high": db.Column(db.Float, nullable=False, comment='最高价'),
#             "low": db.Column(db.Float, nullable=False, comment='最低价'),
#             "volume": db.Column(db.Integer, nullable=False, comment='成交量'),
#             "money": db.Column(db.Integer, nullable=False, comment='成交额'),
#
#             # 补充的字段15分钟K线数据趋势信息
#             "trends": db.Column(db.Integer, nullable=True, default=1, comment='趋势'),
#             "signal_times": db.Column(db.Text, nullable=True, comment='信号时间'),
#             "signal_start_time": db.Column(db.Text, nullable=True, comment='信号开始时间'),
#             "re_trend": db.Column(db.Integer, nullable=True, default=1, comment='重新趋势'),
#
#             # 补充的字段15分钟K线周期信息
#             "cycle_amplitude_per_bar": db.Column(db.Float, nullable=True, default=0, comment='每根K线周期振幅'),
#             "cycle_amplitude_max": db.Column(db.Float, nullable=True, default=0, comment='最大周期振幅'),
#             "cycle_1m_vol_max1": db.Column(db.Integer, nullable=True, default=0, comment='1分钟最大成交量1'),
#             "cycle_1m_vol_max5": db.Column(db.Integer, nullable=True, default=0, comment='1分钟最大成交量5'),
#             "cycle_length_per_bar": db.Column(db.Integer, nullable=True, default=0, comment='每根K线周期长度'),
#
#             # 补充的字段15分钟K线预测周期信息
#             "predict_cycle_length": db.Column(db.Integer, nullable=True, default=0, comment='预测周期长度'),
#             "predict_cycle_change": db.Column(db.Float, nullable=True, default=0, comment='预测周期变化'),
#             "predict_cycle_price": db.Column(db.Float, nullable=True, default=0, comment='预测周期价格'),
#             "predict_bar_change": db.Column(db.Float, nullable=True, default=0, comment='预测K线变化'),
#             "predict_bar_price": db.Column(db.Float, nullable=True, default=0, comment='预测K线价格'),
#             "predict_bar_volume": db.Column(db.Integer, nullable=True, default=0, comment='预测K线成交量'),
#
#             # 补充的字段15分钟K线预测周期得分信息
#             "score_rnn_model": db.Column(db.Float, nullable=True, default=0, comment='RNN模型得分'),
#             "score_board_boll": db.Column(db.Float, nullable=True, default=0, comment='布林带得分'),
#             "score_board_money": db.Column(db.Float, nullable=True, default=0, comment='资金得分'),
#             "score_board_hot": db.Column(db.Float, nullable=True, default=0, comment='热度得分'),
#             "score_funds_awkward": db.Column(db.Float, nullable=True, default=0, comment='基金重仓得分'),
#             "trend_probability": db.Column(db.Float, nullable=True, default=0, comment='趋势概率'),
#             "rnn_model_score": db.Column(db.Float, nullable=True, default=0, comment='RNN模型评分'),
#             "cycle_amplitude": db.Column(db.Float, nullable=True, default=0, comment='周期振幅'),
#
#             # 补充的字段持仓&交易信息
#             "position": db.Column(db.Integer, nullable=True, default=1, comment='持仓状态'),
#             "position_num": db.Column(db.Float, nullable=True, default=0, comment='持仓数量'),
#             "stop_loss": db.Column(db.Float, nullable=True, default=0, comment='止损价格'),
#         }
#     )
#
#     # 缓存生成的类
#     daily_model_cache[cache_key] = DailyStockData
#
#     return DailyStockData
#
#
# def save_daily_stock_data_to_sql(stock_code: str, data: pd.DataFrame) -> bool:
#     """
#     将股票按天数据保存至 datadaily 数据库中，按股票代码创建表格。
#
#     Args:
#         stock_code: 股票代码
#         data: 每天的股票数据 DataFrame，每行包含 date、open、close 等列
#
#     Returns:
#         bool: 保存是否成功
#     """
#     try:
#         # 动态创建模型类
#         DailyStockModel = create_daily_stock_model(stock_code)
#
#         # 将 DataFrame 转换为模型对象列表
#         daily_stock_records = []
#
#         for _, row in data.iterrows():
#             record = DailyStockModel(
#                 date=row['date'],
#                 open=row['open'],
#                 close=row['close'],
#                 high=row['high'],
#                 low=row['low'],
#                 volume=row['volume'],
#                 money=row['money'],
#
#                 # 为新增字段设置默认值
#                 trends=row.get('trends', 1),
#                 signal_times=row.get('signal_times', None),
#                 signal_start_time=row.get('signal_start_time', None),
#                 re_trend=row.get('re_trend', 1),
#                 cycle_amplitude_per_bar=row.get('cycle_amplitude_per_bar', 0),
#                 cycle_amplitude_max=row.get('cycle_amplitude_max', 0),
#                 cycle_1m_vol_max1=row.get('cycle_1m_vol_max1', 0),
#                 cycle_1m_vol_max5=row.get('cycle_1m_vol_max5', 0),
#                 cycle_length_per_bar=row.get('cycle_length_per_bar', 0),
#                 predict_cycle_length=row.get('predict_cycle_length', 0),
#                 predict_cycle_change=row.get('predict_cycle_change', 0),
#                 predict_cycle_price=row.get('predict_cycle_price', 0),
#                 predict_bar_change=row.get('predict_bar_change', 0),
#                 predict_bar_price=row.get('predict_bar_price', 0),
#                 predict_bar_volume=row.get('predict_bar_volume', 0),
#                 score_rnn_model=row.get('score_rnn_model', 0),
#                 score_board_boll=row.get('score_board_boll', 0),
#                 score_board_money=row.get('score_board_money', 0),
#                 score_board_hot=row.get('score_board_hot', 0),
#                 score_funds_awkward=row.get('score_funds_awkward', 0),
#                 trend_probability=row.get('trend_probability', 0),
#                 rnn_model_score=row.get('rnn_model_score', 0),
#                 cycle_amplitude=row.get('cycle_amplitude', 0),
#                 position=row.get('position', 0),
#                 position_num=row.get('position_num', 0),
#                 stop_loss=row.get('stop_loss', 0),
#             )
#             daily_stock_records.append(record)
#
#         # 批量插入到数据库
#         db.session.add_all(daily_stock_records)
#         db.session.commit()
#
#         logger.info(f"成功保存股票 {stock_code} 的日线数据，共 {len(daily_stock_records)} 条记录")
#         return True
#
#     except IntegrityError as e:
#         db.session.rollback()  # 回滚事务，避免锁定数据库
#         logger.error(f"保存股票 {stock_code} 日线数据时发生完整性错误: {e}")
#         return False
#     except Exception as e:
#         db.session.rollback()
#         logger.error(f"保存股票 {stock_code} 日线数据时发生未知错误: {e}")
#         return False
#
#
# def get_daily_stock_data(stock_code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
#     """
#     获取股票日线数据
#
#     Args:
#         stock_code: 股票代码
#         start_date: 开始日期 (YYYY-MM-DD)
#         end_date: 结束日期 (YYYY-MM-DD)
#
#     Returns:
#         pd.DataFrame: 股票日线数据
#     """
#     try:
#         DailyStockModel = create_daily_stock_model(stock_code)
#
#         query = DailyStockModel.query
#
#         if start_date:
#             query = query.filter(DailyStockModel.date >= start_date)
#         if end_date:
#             query = query.filter(DailyStockModel.date <= end_date)
#
#         records = query.order_by(DailyStockModel.date).all()
#
#         # 转换为DataFrame
#         data = []
#         for record in records:
#             data.append({
#                 'date': record.date,
#                 'open': record.open,
#                 'close': record.close,
#                 'high': record.high,
#                 'low': record.low,
#                 'volume': record.volume,
#                 'money': record.money,
#                 'trends': record.trends,
#                 'signal_times': record.signal_times,
#                 'signal_start_time': record.signal_start_time,
#                 're_trend': record.re_trend,
#                 'cycle_amplitude_per_bar': record.cycle_amplitude_per_bar,
#                 'cycle_amplitude_max': record.cycle_amplitude_max,
#                 'cycle_1m_vol_max1': record.cycle_1m_vol_max1,
#                 'cycle_1m_vol_max5': record.cycle_1m_vol_max5,
#                 'cycle_length_per_bar': record.cycle_length_per_bar,
#                 'predict_cycle_length': record.predict_cycle_length,
#                 'predict_cycle_change': record.predict_cycle_change,
#                 'predict_cycle_price': record.predict_cycle_price,
#                 'predict_bar_change': record.predict_bar_change,
#                 'predict_bar_price': record.predict_bar_price,
#                 'predict_bar_volume': record.predict_bar_volume,
#                 'score_rnn_model': record.score_rnn_model,
#                 'score_board_boll': record.score_board_boll,
#                 'score_board_money': record.score_board_money,
#                 'score_board_hot': record.score_board_hot,
#                 'score_funds_awkward': record.score_funds_awkward,
#                 'trend_probability': record.trend_probability,
#                 'rnn_model_score': record.rnn_model_score,
#                 'cycle_amplitude': record.cycle_amplitude,
#                 'position': record.position,
#                 'position_num': record.position_num,
#                 'stop_loss': record.stop_loss,
#             })
#
#         return pd.DataFrame(data)
#
#     except Exception as e:
#         logger.error(f"获取股票 {stock_code} 日线数据时发生错误: {e}")
#         return pd.DataFrame()
