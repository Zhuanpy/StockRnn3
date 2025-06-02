from flask import Flask
from .exts import init_exts
import secrets
from .utils.file_utils import ensure_data_directories

secret_key = secrets.token_hex(16)  # 生成一个 32 字节的十六进制字符串


class Config:
    SQLALCHEMY_DATABASE_URI = "mysql://root:651748264Zz@localhost/mystockrecord"
    SQLALCHEMY_BINDS = {
        # 定义按年分时数据库绑定
        **{f"data1m{year}": f"mysql://root:651748264Zz@localhost/data1m{year}"
           for year in range(2024, 2026)},

        # 定义每日数据绑定
        "datadaily": "mysql://root:651748264Zz@localhost/datadaily",
        # 定义基金重仓数据绑定
        "funds_awkward": "mysql://root:651748264Zz@localhost/funds_awkward",
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secret_key  # 使用一个随机的密钥字符串
    app.secret_key = secret_key  # 确保设置了 secret_key 用于会话

    # 确保数据目录存在
    ensure_data_directories()
    
    # 注册蓝图
    from .routes.main import main_bp  # 导入主蓝图
    from .routes.download_data_route import dl_bp
    from .routes.download_top500_funds_awkward import dl_funds_awkward_bp
    from .routes.download_EastMoney import dl_eastmoney_bp
    from .routes.rnn_data import rnn_bp  # 导入RNN蓝图
    from .routes.issues import issue_bp  # 导入问题管理蓝图
    
    app.register_blueprint(main_bp)  # 注册主蓝图
    app.register_blueprint(dl_bp)
    app.register_blueprint(dl_funds_awkward_bp)
    app.register_blueprint(dl_eastmoney_bp)
    app.register_blueprint(rnn_bp)  # 注册RNN蓝图
    app.register_blueprint(issue_bp)  # 注册问题管理蓝图

    # 配置数据库
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:651748264Zz@localhost/mystockrecord'
    app.config.from_object(Config)  # 加载配置

    # 初始化插件
    init_exts(app=app)

    return app
