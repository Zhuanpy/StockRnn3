import os
from pathlib import Path
from dotenv import load_dotenv  # 推荐使用python-dotenv

# 加载环境变量
load_dotenv()

class Config:
    # 基础配置
    BASE_DIR = Path(__file__).resolve().parent
    
    # 数据库配置 - 从环境变量获取
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', '651748264Zz'),
        'charset': 'utf8mb4'
    }
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    
    @classmethod
    def get_project_root(cls):
        """返回项目根目录路径"""
        return str(cls.BASE_DIR)
    
    @classmethod
    def get_database_uri(cls, database):
        """生成数据库URI"""
        return f"mysql://{cls.DB_CONFIG['user']}:{cls.DB_CONFIG['password']}@{cls.DB_CONFIG['host']}/{database}"
    
    @classmethod
    def get_sqlalchemy_binds(cls):
        """获取所有数据库绑定"""
        binds = {
            # 主数据库绑定
            "quanttradingsystem": cls.get_database_uri("quanttradingsystem"),
        }
        return binds
    
    @classmethod
    def get_database_uri_main(cls):
        """获取主数据库URI"""
        return cls.get_database_uri("quanttradingsystem")
    
    @classmethod
    def get_password_path(cls):
        """获取密码文件路径"""
        return cls.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password'
    
    @classmethod
    def get_eastmoney_path(cls):
        """获取东方财富相关文件路径"""
        return cls.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password' / 'EastMoney'
    
    @classmethod
    def get_xueqiu_path(cls):
        """获取雪球相关文件路径"""
        return cls.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password' / 'XueQiu'
    
    @classmethod
    def get_code_data_path(cls):
        """获取代码数据路径"""
        return cls.BASE_DIR / 'App' / 'codes' / 'code_data'
    
    @classmethod
    def get_eastmoney_headers(cls, header_type: str = 'stock_1m_multiple_days'):
        """获取东方财富请求头配置"""
        headers_config = {
            'stock_1m_multiple_days': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Host': 'push2his.eastmoney.com',
                'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
            }
        }
        
        return headers_config.get(header_type, {})
    
    @classmethod
    def get_eastmoney_urls(cls, url_type: str = 'stock_1m_multiple_days'):
        """获取东方财富URL配置"""
        urls_config = {
            'stock_1m_multiple_days': 'https://push2his.eastmoney.com/api/qt/stock/trends2/get?fields1=f1&fields2=f51,f52,f53,f54,f55,f56,f57&ut=fa5fd1943c7b386f172d6893dbfba10b&ndays={}&iscr=0&secid={}&cb=jQuery112406290464117319126_1645838221914&_=1645838221952'
        }
        
        return urls_config.get(url_type, '')
    
    # 数据库URI配置 - 使用类变量
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_BINDS = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 雪球API配置
    @property
    def XUEQIU_CONFIG(self):
        return {
            'cookies_path': self.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password' / 'XueQiu' / 'cookies.txt',
            'headers_path': self.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password' / 'XueQiu' / 'headers.txt'
        }
    
    # 文件路径配置 - 使用pathlib
    @property
    def FILE_PATHS(self):
        return {
            'project_root': str(self.BASE_DIR),
            'code_data': self.BASE_DIR / 'App' / 'codes' / 'code_data',
            'password_path': self.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password',
            'sql_password_path': self.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password' / 'sql.txt',
            'xueqiu_cookies_path': self.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password' / 'XueQiu' / 'cookies.txt',
            'xueqiu_headers_path': self.BASE_DIR / 'App' / 'codes' / 'code_data' / 'password' / 'XueQiu' / 'headers.txt'
        }
    
    def get_sql_password(self):
        """获取SQL密码"""
        path = self.FILE_PATHS['sql_password_path']
        with open(path, 'r') as f:
            return f.read().strip()
    
    def get_xueqiu_cookies(self):
        """获取雪球cookies"""
        path = self.FILE_PATHS['xueqiu_cookies_path']
        cookies = {}
        with open(path, 'r') as f:
            for line in f.read().split(';'):
                if '=' in line:
                    name, value = line.strip().split('=', 1)
                    cookies[name] = value
        return cookies
    
    def get_xueqiu_headers(self):
        """获取雪球headers"""
        path = self.FILE_PATHS['xueqiu_headers_path']
        headers = {}
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if ': ' in line:
                    name, value = line.split(': ', 1)
                    headers[name] = value
        return headers

# 环境配置
class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # 生产环境使用独立环境变量前缀
    DB_CONFIG = {
        'host': os.getenv('PROD_DB_HOST', 'localhost'),
        'user': os.getenv('PROD_DB_USER', 'root'),
        'password': os.getenv('PROD_DB_PASSWORD', ''),
        'charset': 'utf8mb4'
    }

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

# 初始化数据库URI配置
Config.SQLALCHEMY_DATABASE_URI = Config.get_database_uri_main()
Config.SQLALCHEMY_BINDS = Config.get_sqlalchemy_binds() 