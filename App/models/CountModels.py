from ..exts import db


# count_board
class CountBoard(db.Model):
    __tablename__ = 'count_board'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    code = db.Column(db.String(20))
    trends = db.Column(db.Integer)
    record_date = db.Column(db.Date)


class CountStockPool(db.Model):
    """统计股票池信息表"""
    __tablename__ = 'count_stock_pool'

    # 主键 ID
    id = db.Column(db.Integer, primary_key=True)

    # 记录日期
    date = db.Column(db.Date, nullable=False)

    # 上涨股票计数
    up = db.Column(db.Integer, default=0)

    # 上涨股票趋势反转股票计数
    up_reversal = db.Column(db.Integer, default=0)

    # 下跌股票计数
    down = db.Column(db.Integer, default=0)

    # 下跌股票反转股票计数
    down_reversal = db.Column(db.Integer, default=0)

    # 个股股票“上涨开始阶段”和“上涨结束阶段” 计数
    up_phase_start = db.Column(db.Integer, default=0)
    up_phase_end = db.Column(db.Integer, default=0)

    # 个股股票“下开始阶段”和“下结束阶段” 计数
    down_phase_start = db.Column(db.Integer, default=0)
    down_phase_end = db.Column(db.Integer, default=0)

    # 股票的上涨 "前期、中期、后期" 计数
    up_initial = db.Column(db.Integer, default=0)
    up_median = db.Column(db.Integer, default=0)
    up_final = db.Column(db.Integer, default=0)

    # 股票的下跌 "前期、中期、后期" 计数
    down_initial = db.Column(db.Integer, default=0)
    down_median = db.Column(db.Integer, default=0)
    down_final = db.Column(db.Integer, default=0)

    # 板块“上涨开始阶段”和“上涨结束阶段” 计数
    board_up_phase_start = db.Column(db.Integer, default=0)
    board_up_phase_end = db.Column(db.Integer, default=0)

    # 板块“下开始阶段”和“下结束阶段” 计数
    board_down_phase_start = db.Column(db.Integer, default=0)
    board_down_phase_end = db.Column(db.Integer, default=0)
