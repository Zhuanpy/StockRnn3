from flask import Flask
from config import config
from .exts import init_exts
from .utils.file_utils import ensure_data_directories

def create_app(config_name='default'):
    """
    创建Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    init_exts(app)
    
    # 确保数据目录存在
    ensure_data_directories()
    
    # 注册蓝图
    from .routes.views import main_bp, dl_bp, rnn_bp, issue_bp
    from .routes.data.download_data_route import download_data_bp
    from .routes.data.data_management import data_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(dl_bp)
    app.register_blueprint(rnn_bp)
    app.register_blueprint(issue_bp)
    app.register_blueprint(download_data_bp)
    app.register_blueprint(data_bp)
    
    return app
