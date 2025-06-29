from flask import Blueprint, jsonify, render_template,  current_app
from datetime import datetime
import logging
import traceback
from sqlalchemy import and_, or_
from concurrent.futures import ThreadPoolExecutor
import threading
import os

from App.models.strategy import RnnTrainingRecords
from App.exts import db
from App.codes.RnnModel.DataProcessing import process_stock_data_for_year

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# 创建蓝图
RnnData = Blueprint('RnnData', __name__, url_prefix='/RnnData')

# 全局进度跟踪
class ProcessingProgress:
    def __init__(self):
        self.total = 0
        self.current = 0
        self.success = 0
        self.failed = 0
        self.lock = threading.Lock()
        self.processing_stocks = set()  # 记录正在处理的股票
    
    def update(self, stock_code, success=True):
        with self.lock:
            self.current += 1
            if success:
                self.success += 1
            else:
                self.failed += 1
            if stock_code in self.processing_stocks:
                self.processing_stocks.remove(stock_code)
    
    def add_stock(self, stock_code):
        with self.lock:
            self.processing_stocks.add(stock_code)
    
    def get_progress(self):
        with self.lock:
            return {
                'total': self.total,
                'current': self.current,
                'success': self.success,
                'failed': self.failed,
                'percentage': (self.current / self.total * 100) if self.total > 0 else 0,
                'processing_stocks': list(self.processing_stocks)
            }
    
    def reset(self):
        with self.lock:
            self.total = 0
            self.current = 0
            self.success = 0
            self.failed = 0
            self.processing_stocks.clear()

progress_tracker = ProcessingProgress()

def ensure_directory_exists(directory):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"创建目录: {directory}")
            return True
        except Exception as e:
            logger.error(f"创建目录失败 {directory}: {str(e)}")
            return False
    return True

def get_base_directory():
    """获取基础目录的绝对路径"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_data_directory(year):
    """获取数据目录的绝对路径"""
    base_dir = get_base_directory()
    return os.path.join(base_dir, 'static', 'data', 'years', str(year))

class ProcessContext:
    def __init__(self, app, stock_code, year):
        self.app = app
        self.stock_code = stock_code
        self.year = year

def process_stock_with_progress(process_context):
    """单个股票处理函数（用于多线程）"""
    stock_code = process_context.stock_code
    year = process_context.year
    app = process_context.app

    try:
        progress_tracker.add_stock(stock_code)
        
        # 获取并创建必要的目录
        data_dir = get_data_directory(year)
        input_dir = os.path.join(data_dir, '1m')
        output_dir = os.path.join(data_dir, '15m')
        
        # 确保目录存在
        if not ensure_directory_exists(input_dir) or not ensure_directory_exists(output_dir):
            raise Exception("无法创建必要的目录")
        
        # 检查输入目录是否存在数据
        if not os.path.exists(input_dir) or not os.listdir(input_dir):
            raise Exception(f"输入目录不存在或为空: {input_dir}")
            
        # 处理数据
        result = process_stock_data_for_year(year, stock_code)
        
        # 更新进度
        progress_tracker.update(stock_code, success=result)
        
        # 更新数据库状态
        with app.app_context():
            stock = RnnTrainingRecords.query.filter_by(code=stock_code).first()
            if stock:
                stock.original_15M_status = 'success' if result else 'failed'
                db.session.commit()
        
        return stock_code, result
        
    except Exception as e:
        logger.error(f"处理股票 {stock_code} 时出错: {str(e)}")
        logger.error(traceback.format_exc())
        progress_tracker.update(stock_code, success=False)
        
        # 更新数据库状态
        try:
            with app.app_context():
                stock = RnnTrainingRecords.query.filter_by(code=stock_code).first()
                if stock:
                    stock.original_15M_status = 'failed'
                    db.session.commit()
        except Exception as db_error:
            logger.error(f"更新数据库状态失败: {str(db_error)}")
        
        return stock_code, False

@RnnData.route('/processing_progress', methods=['GET'])
def get_processing_progress():
    """获取处理进度的API"""
    return jsonify(progress_tracker.get_progress())

def update_processing_status(stock_code, year, status, message=''):
    """更新股票处理状态"""
    try:
        record = RnnTrainingRecords.query.filter_by(code=stock_code).first()
        if record:
            record.set_process_status(year, status, message)
            db.session.commit()
            logging.info(f"Updated processing status for {stock_code}: {status}")
            return True
        else:
            logging.warning(f"Stock {stock_code} not found in database")
            return False
    except Exception as e:
        logging.error(f"Error updating status for {stock_code}: {str(e)}")
        db.session.rollback()
        return False

@RnnData.route('/rnn_data_page', methods=['GET', 'POST'])
def rnn_data_page():
    return render_template('RNN模型/模型数据处理.html')

# 计算15分钟原始数据
@RnnData.route('/original_15M/<year>', methods=['POST'])
def original_15M(year):
    try:
        # 验证年份
        year = str(year)
        if not (2000 <= int(year) <= 2099):
            return jsonify({
                'status': 'error',
                'message': '年份必须在2000-2099之间'
            }), 400

        # 检查数据目录
        data_dir = get_data_directory(year)
        input_dir = os.path.join(data_dir, '1m')
        output_dir = os.path.join(data_dir, '15m')
        
        if not os.path.exists(input_dir):
            return jsonify({
                'status': 'error',
                'message': f'输入目录不存在: {input_dir}'
            }), 400

        # 获取需要处理的股票列表
        stocks = RnnTrainingRecords.query.filter(
            or_(
                RnnTrainingRecords.original_15M_year.is_(None),
                RnnTrainingRecords.original_15M_year != year,
                and_(
                    RnnTrainingRecords.original_15M_year == year,
                    RnnTrainingRecords.original_15M_status.in_(['failed', 'pending'])
                )
            )
        ).all()

        if not stocks:
            success_records = RnnTrainingRecords.query.filter(
                and_(
                    RnnTrainingRecords.original_15M_year == year,
                    RnnTrainingRecords.original_15M_status == 'success'
                )
            ).count()
            
            total_records = RnnTrainingRecords.query.count()
            
            if success_records == total_records:
                return jsonify({
                    'status': 'success',
                    'message': f'{year}年的所有数据已经处理完成',
                    'data': {
                        'success_count': success_records,
                        'failed_count': 0
                    }
                })

        # 初始化进度跟踪器
        progress_tracker.reset()
        progress_tracker.total = len(stocks)

        # 更新所有股票状态为处理中
        for stock in stocks:
            stock.original_15M_year = year
            stock.original_15M_status = 'pending'
        db.session.commit()

        # 获取当前应用实例
        app = current_app._get_current_object()

        # 使用线程池处理数据
        with ThreadPoolExecutor(max_workers=min(8, len(stocks))) as executor:
            futures = []
            for stock in stocks:
                process_context = ProcessContext(app, stock.code, year)
                future = executor.submit(process_stock_with_progress, process_context)
                futures.append(future)

            # 等待所有任务完成
            for future in futures:
                try:
                    future.result()
                except Exception as e:
                    logger.error(f"处理任务失败: {str(e)}")

        # 获取最终进度
        final_progress = progress_tracker.get_progress()

        return jsonify({
            'status': 'success',
            'message': f'处理完成: 成功 {final_progress["success"]} 只，失败 {final_progress["failed"]} 只',
            'data': {
                'year': year,
                'success_count': final_progress["success"],
                'failed_count': final_progress["failed"],
                'processed_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"处理过程出错: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'处理失败: {str(e)}'
        }), 500

# 处理15分钟基础数据
@RnnData.route('/process_base_data/<int:year>', methods=['POST'])
def process_base_data(year):
    try:
        # 获取所有股票记录
        records = RnnTrainingRecords.query.all()
        
        if not records:
            # 如果没有记录，从股票列表创建新记录
            # TODO: 从你的股票列表数据源获取股票代码和名称
            stocks = [
                {'code': '000001', 'name': '平安银行'},
                # ... 其他股票
            ]
            for stock in stocks:
                record = RnnTrainingRecords(
                    stock_code=stock['code'],
                    stock_name=stock['name']
                )
                db.session.add(record)
            db.session.commit()
            records = RnnTrainingRecords.query.all()

        # 检查是否有正在处理的数据
        processing_records = RnnTrainingRecords.query.filter(
            and_(
                RnnTrainingRecords.original_15M_year == year,
                RnnTrainingRecords.original_15M_status.in_(['pending', 'failed'])
            )
        ).all()

        if processing_records:
            # 处理未完成或失败的记录
            for record in processing_records:
                try:
                    # TODO: 在这里添加你的15分钟数据处理逻辑
                    process_15min_data(record.stock_code, year)
                    record.original_15M_status = 'success'
                except Exception as e:
                    record.original_15M_status = 'failed'
                    print(f"处理失败 {record.stock_code}: {str(e)}")
                db.session.commit()
        else:
            # 开始新的处理
            for record in records:
                record.original_15M_year = year
                record.original_15M_status = 'pending'
                db.session.commit()
                
                try:
                    # TODO: 在这里添加你的15分钟数据处理逻辑
                    process_15min_data(record.stock_code, year)
                    record.original_15M_status = 'success'
                except Exception as e:
                    record.original_15M_status = 'failed'
                    print(f"处理失败 {record.stock_code}: {str(e)}")
                db.session.commit()

        # 获取处理结果统计
        success_count = RnnTrainingRecords.query.filter(
            and_(
                RnnTrainingRecords.original_15M_year == year,
                RnnTrainingRecords.original_15M_status == 'success'
            )
        ).count()
        
        failed_count = RnnTrainingRecords.query.filter(
            and_(
                RnnTrainingRecords.original_15M_year == year,
                RnnTrainingRecords.original_15M_status == 'failed'
            )
        ).count()

        return jsonify({
            'status': 'success',
            'message': f'处理完成。成功: {success_count}, 失败: {failed_count}',
            'data': {
                'success_count': success_count,
                'failed_count': failed_count
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': f'处理过程中发生错误: {str(e)}'
        }), 500

def process_15min_data(stock_code, year):
    """
    处理15分钟数据的具体逻辑
    这里需要实现你的数据处理逻辑
    """
    # TODO: 实现你的15分钟数据处理逻辑
    pass

# 处理15分钟标准化数据
@RnnData.route('/process_standard_data/<year>/<quarter>', methods=['POST'])
def process_standard_data(year, quarter):

    try:
        # 验证年份
        year = str(year)
        if not (2000 <= int(year) <= 2099):
            return jsonify({
                'status': 'error',
                'message': '年份必须在2000-2099之间'
            }), 400

        # 获取已完成基础数据处理的股票
        stocks = RnnTrainingRecords.query.filter(
            getattr(RnnTrainingRecords, f'processed_{year}') == RnnTrainingRecords.STATUS_SUCCESS
        ).all()

        if not stocks:
            return jsonify({
                'status': 'error',
                'message': f'没有找到{year}年已完成基础数据处理的股票'
            }), 400

        success_count = 0
        failed_count = 0

        # 处理全年数据
        if quarter == 'full':
            for stock in stocks:
                try:
                    result = process_full_year_data(year, stock.code)
                    if result['status'] == 'success':
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
                    logging.error(f"处理股票 {stock.code} 全年数据时出错: {str(e)}")
            
            message = f'{year}年全年数据标准化处理完成'
        else:
            # 验证季度
            quarter = int(quarter)
            if not (1 <= quarter <= 4):
                return jsonify({
                    'status': 'error',
                    'message': '季度必须在1-4之间'
                }), 400
            
            for stock in stocks:
                try:
                    result = process_quarter_data(year, quarter, stock.code)
                    if result['status'] == 'success':
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    failed_count += 1
                    logging.error(f"处理股票 {stock.code} 第{quarter}季度数据时出错: {str(e)}")
            
            message = f'{year}年第{quarter}季度数据标准化处理完成'

        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'year': year,
                'quarter': quarter,
                'success_count': success_count,
                'failed_count': failed_count,
                'processed_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        logging.error(f"处理标准化数据时出错: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'处理失败: {str(e)}'
        }), 500

def process_full_year_data(year, stock_code):
    """处理全年数据的具体实现"""
    try:
        # 这里添加处理全年数据的具体逻辑
        return {
            'status': 'success',
            'stock_code': stock_code,
            'year': year,
            'message': '全年数据处理成功'
        }
    except Exception as e:
        logging.error(f"处理全年数据时出错: {str(e)}")

        return {
            'status': 'failed',
            'stock_code': stock_code,
            'year': year,
            'message': str(e)
        }

def process_quarter_data(year, quarter, stock_code):
    """处理季度数据的具体实现"""
    try:
        # 这里添加处理季度数据的具体逻辑
        return {
            'status': 'success',
            'stock_code': stock_code,
            'year': year,
            'quarter': quarter,
            'message': '季度数据处理成功'
        }
    except Exception as e:
        logging.error(f"处理季度数据时出错: {str(e)}")
        return {
            'status': 'failed',
            'stock_code': stock_code,
            'year': year,
            'quarter': quarter,
            'message': str(e)
        }

# 生成及保存模型训练数据