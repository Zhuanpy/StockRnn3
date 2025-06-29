# 插件管理

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# 按正确顺序导入模型，确保外键引用的表先被导入
from .models.data.basic_info import StockCodes, StockClassification
# from .models.data.Download import Download1MRecord
from .models.data import StockDaily, Stock1m, Stock15m, FundsAwkward
from .models.data.summary import DataSummary

# 导入其他模型
from .models.evaluation import CountBoard, CountStockPool, StrategyPerformance, RiskMetrics
from .models.strategy import RnnTrainingRecords, RnnRunningRecord, Top500FundRecord, Issue
from .models.trade import TradeRecord, Position, Account, TradeSignal


def init_exts(app):
    """初始化数据库扩展和迁移功能."""
    
    db.init_app(app=app)
    migrate.init_app(app=app, db=db)

    # 创建所有数据库表
    with app.app_context():
        db.create_all()
