# 插件管理

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


def init_exts(app):

    """初始化数据库扩展和迁移功能."""

    db.init_app(app=app)
    migrate.init_app(app=app, db=db)

    # 导入模型并创建所有表
    with app.app_context():
        from .models import CountBoard, CountStockPool
        from .models import RnnRunningRecord, RnnTrainingRecord
        from .models import Download1MRecord
        from .models import Top500FundRecord
        from .models import StockBasicInformationOthersCode, StockBasicInformationStock
        from .models import Issue,RnnTrainingRecords
        db.create_all()
