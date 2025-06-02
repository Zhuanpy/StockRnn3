from sqlalchemy import Column, Integer, String, Enum, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class DataSummary(Base):
    """股票数据汇总表模型"""
    __tablename__ = 'data_summary'
    __table_args__ = {'schema': 'stockdata'}  # 指定schema为stockdata

    # 定义列
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_code = Column(String(10), nullable=False, comment='股票代码')
    stock_name = Column(String(100), nullable=True, comment='股票名称')
    data_type = Column(
        Enum('1m', '15m', '120m', 'Daily', name='data_type_enum'),
        nullable=False,
        comment='数据类型'
    )
    quarter = Column(String(7), nullable=False, comment='季度')
    is_complete = Column(Boolean, default=False, comment='是否完整')
    record_count = Column(Integer, default=0, comment='记录数量')

    def __repr__(self):
        return f"<DataSummary(stock_code='{self.stock_code}', data_type='{self.data_type}', quarter='{self.quarter}')>"

    @classmethod
    def create_table(cls, engine):
        """创建表格"""
        Base.metadata.create_all(engine)

# 数据库连接和会话管理
def get_db_session(db_url):
    """
    获取数据库会话
    :param db_url: 数据库连接URL，例如: 'mysql+pymysql://user:password@localhost/stockdata'
    :return: Session对象
    """
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    return Session()

# 使用示例
if __name__ == '__main__':
    # 数据库连接URL（需要根据实际情况修改）
    DB_URL = 'mysql+pymysql://user:password@localhost/stockdata'
    
    # 创建引擎
    engine = create_engine(DB_URL)
    
    # 创建表（如果不存在）
    DataSummary.create_table(engine)
    
    # 创建会话
    session = get_db_session(DB_URL)
    
    try:
        # 示例：添加数据
        new_summary = DataSummary(
            stock_code='000001',
            stock_name='平安银行',
            data_type='1m',
            quarter='2024Q1',
            is_complete=True,
            record_count=1000
        )
        session.add(new_summary)
        session.commit()
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        
    finally:
        session.close() 