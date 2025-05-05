from ..exts import db
from sqlalchemy import Column, String, Text, DateTime, BigInteger
from datetime import datetime

class RnnTrainingRecords(db.Model):
    """RNN模型训练记录表"""
    __tablename__ = 'rnn_training_records'
    __table_args__ = {'extend_existing': True}  # 允许表的重定义

    # 状态常量
    STATUS_PENDING = 'pending'    # 待处理
    STATUS_PROCESSING = 'processing'  # 处理中
    STATUS_SUCCESS = 'success'    # 处理成功
    STATUS_FAILED = 'failed'      # 处理失败
    
    # 主键ID
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # 股票基本信息
    name = Column(String(100), nullable=True, comment='股票名称')
    code = Column(String(10), nullable=True, comment='股票代码')
    
    # 解析信息
    parser_month = Column(String(10), nullable=True, comment='解析月份')
    starting_date = Column(DateTime, nullable=True, comment='开始日期')
    
    # 模型数据相关
    model_data = Column(Text, nullable=True, comment='模型数据状态')
    model_data_timing = Column(DateTime, nullable=True, comment='数据处理时间')
    
    # 模型创建相关
    model_create = Column(String(20), nullable=True, comment='模型创建状态')
    model_create_timing = Column(DateTime, nullable=True, comment='模型创建时间')
    
    # 模型检查相关
    model_check = Column(String(20), nullable=True, comment='模型检查状态')
    model_error = Column(Text, nullable=True, comment='错误信息')
    model_check_timing = Column(DateTime, nullable=True, comment='检查时间')

    # 15分钟原始数据处理相关
    original_15M_year = Column(String(4), nullable=True, comment='原始数据处理年份')
    original_15M_status = Column(String(10), nullable=True, comment='原始数据处理状态')
    original_15M_time = Column(DateTime, nullable=True, comment='原始数据处理时间')
    original_15M_message = Column(Text, nullable=True, comment='原始数据处理消息')

    # 15分钟标准化数据处理相关
    standard_15M_year = Column(String(4), nullable=True, comment='标准化数据处理年份')
    standard_15M_status = Column(String(10), nullable=True, comment='标准化数据处理状态')
    standard_15M_time = Column(DateTime, nullable=True, comment='标准化数据处理时间')
    standard_15M_message = Column(Text, nullable=True, comment='标准化数据处理消息')

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parser_month': self.parser_month,
            'starting_date': self.starting_date.strftime('%Y-%m-%d %H:%M:%S') if self.starting_date else None,
            'model_data': self.model_data,
            'model_data_timing': self.model_data_timing.strftime('%Y-%m-%d %H:%M:%S') if self.model_data_timing else None,
            'model_create': self.model_create,
            'model_create_timing': self.model_create_timing.strftime('%Y-%m-%d %H:%M:%S') if self.model_create_timing else None,
            'model_check': self.model_check,
            'model_error': self.model_error,
            'model_check_timing': self.model_check_timing.strftime('%Y-%m-%d %H:%M:%S') if self.model_check_timing else None,
            'original_15M': {
                'year': self.original_15M_year,
                'status': self.original_15M_status,
                'time': self.original_15M_time.strftime('%Y-%m-%d %H:%M:%S') if self.original_15M_time else None,
                'message': self.original_15M_message
            },
            'standard_15M': {
                'year': self.standard_15M_year,
                'status': self.standard_15M_status,
                'time': self.standard_15M_time.strftime('%Y-%m-%d %H:%M:%S') if self.standard_15M_time else None,
                'message': self.standard_15M_message
            }
        }

    def __repr__(self):
        return f"<RnnTrainingRecords(id={self.id}, code={self.code}, name={self.name})>"

    @classmethod
    def init_process_year(cls, year):
        """初始化指定年份的处理状态"""
        try:
            # 更新所有记录的年份和状态
            cls.query.update({
                'original_15M_year': str(year),
                'original_15M_status': cls.STATUS_PENDING,
                'original_15M_time': None,
                'original_15M_message': None,
                'standard_15M_year': str(year),
                'standard_15M_status': cls.STATUS_PENDING,
                'standard_15M_time': None,
                'standard_15M_message': None
            })
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"初始化处理状态时出错: {str(e)}")
            return False

    def set_original_status(self, status, message=None):
        """设置原始数据处理状态"""
        try:
            self.original_15M_status = status
            self.original_15M_time = datetime.now()
            if message:
                self.original_15M_message = message
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"更新原始数据处理状态时出错: {str(e)}")
            return False

    def set_standard_status(self, status, message=None):
        """设置标准化数据处理状态"""
        try:
            self.standard_15M_status = status
            self.standard_15M_time = datetime.now()
            if message:
                self.standard_15M_message = message
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"更新标准化数据处理状态时出错: {str(e)}")
            return False

    def is_original_processed(self):
        """检查原始数据是否处理成功"""
        return self.original_15M_status == self.STATUS_SUCCESS

    def is_standard_processed(self):
        """检查标准化数据是否处理成功"""
        return self.standard_15M_status == self.STATUS_SUCCESS 