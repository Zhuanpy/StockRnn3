from ..exts import db


class RnnRunningRecord(db.Model):
    """模型类，用于记录RNN运行记录。

    Attributes:
        id (int): 记录的唯一标识符
        name (str): 记录名称
        code (str): 记录代码
        parser_month (str): 解析月份
        trends (str): 趋势信息
        signal_start_time (datetime): 信号开始时间
        predict_cycle_length (int): 预测周期长度
        real_cycle_length (int): 实际周期长度
        predict_cycle_change (float): 预测周期变化
        predict_cycle_price (float): 预测周期价格
        real_cycle_change (float): 实际周期变化
        predict_bar_change (float): 预测条变化
        real_bar_change (float): 实际条变化
        predict_bar_volume (float): 预测条数量
        real_bar_volume (float): 实际条数量
        score_trends (float): 趋势分数
        trade_point (float): 交易点
        time_run_bar (datetime): 运行条时间
        time_15m (datetime): 15分钟时间
        renew_date (datetime): 更新日期
    """
    __tablename__ = 'rnn_running_records'  # 表名定义

    id = db.Column(db.Integer, primary_key=True)  # 主键：记录的唯一标识符
    name = db.Column(db.String(100), nullable=False)  # 记录名称
    code = db.Column(db.String(10), nullable=False)  # 记录代码
    parser_month = db.Column(db.String(10), nullable=False)  # 解析的月份

    trends = db.Column(db.String(100), nullable=False)  # 趋势信息
    signal_start_time = db.Column(db.DateTime, nullable=False)  # 信号开始时间

    predict_cycle_length = db.Column(db.Integer, nullable=False)  # 预测的周期长度
    real_cycle_length = db.Column(db.Integer, nullable=False)  # 实际的周期长度

    predict_cycle_change = db.Column(db.Float, nullable=False)  # 预测周期的变化
    predict_cycle_price = db.Column(db.Float, nullable=False)  # 预测周期的价格
    real_cycle_change = db.Column(db.Float, nullable=False)  # 实际周期的变化

    predict_bar_change = db.Column(db.Float, nullable=False)  # 预测条的变化
    real_bar_change = db.Column(db.Float, nullable=False)  # 实际条的变化

    predict_bar_volume = db.Column(db.Float, nullable=False)  # 预测条的数量
    real_bar_volume = db.Column(db.Float, nullable=False)  # 实际条的数量

    score_trends = db.Column(db.Float, nullable=False)  # 趋势分数
    trade_point = db.Column(db.Float, nullable=False)  # 交易点

    time_run_bar = db.Column(db.DateTime, nullable=False)  # 运行条的时间
    time_15m = db.Column(db.DateTime, nullable=False)  # 15分钟的时间
    renew_date = db.Column(db.DateTime, nullable=False)  # 更新日期

    # 如果有需要，可以添加索引和唯一性约束
    # db.Index('ix_code', code, unique=True)


# rnn_training_records
class RnnTrainingRecord(db.Model):

    """模型类，用于记录RNN训练记录。

    Attributes:
        id (int): 记录的唯一标识符
        name (str): 记录名称
        code (str): 记录代码
        parser_month (str): 解析的月份
        starting_date (datetime): 训练开始日期
        model_data (str): 模型数据
        model_data_timing (datetime): 模型数据时间
        model_create (str): 模型创建者
        model_create_timing (datetime): 模型创建时间
        model_check (str): 模型检查者
        model_error (str): 模型错误信息
        model_check_timing (datetime): 模型检查时间
    """

    __tablename__ = 'rnn_training_records'  # 表名定义

    id = db.Column(db.Integer, primary_key=True)  # 主键：记录的唯一标识符
    name = db.Column(db.String(100), nullable=False)  # 记录名称
    code = db.Column(db.String(10), nullable=False)  # 记录代码
    parser_month = db.Column(db.String(10), nullable=False)  # 解析的月份

    starting_date = db.Column(db.DateTime, nullable=False)  # 训练开始日期
    model_data = db.Column(db.String(100), nullable=False)  # 模型数据
    model_data_timing = db.Column(db.DateTime, nullable=False)  # 模型数据时间

    model_create = db.Column(db.String(100), nullable=False)  # 模型创建者
    model_create_timing = db.Column(db.DateTime, nullable=False)  # 模型创建时间

    model_check = db.Column(db.String(100), nullable=False)  # 模型检查者
    model_error = db.Column(db.String(100), nullable=False)  # 模型错误信息
    model_check_timing = db.Column(db.DateTime, nullable=False)  # 模型检查时间

    # 如果有需要，可以添加索引和唯一性约束
    # db.Index('ix_code', code, unique=True)
