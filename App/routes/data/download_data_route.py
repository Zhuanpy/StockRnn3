from App.codes.downloads.DlStockData import RMDownloadData, StockType, download_1m_by_type
import threading
from App.codes.utils.Normal import ResampleData
from flask import render_template, current_app, jsonify, Blueprint, copy_current_request_context, request, flash
from App.models.data.Stock1m import RecordStockMinute as dlr
from App.models.data.basic_info import StockCodes
from App.codes.RnnDataFile.stock_path import StockDataPath
from App.exts import db
import pandas as pd
from datetime import date, datetime
import logging
# import time

from App.codes.RnnDataFile.save_download import save_1m_to_csv

# 创建蓝图
download_data_bp = Blueprint('download_data_bp', __name__)

# 下载状态和进度的存储
download_status = "未开始"
download_progress = 0
download_thread = None
stop_download = False  # 用于控制下载停止
download_lock = threading.Lock()  # 用于保护全局变量的锁

# 股票代码缓存
stock_code_cache = {}


def get_stock_code_by_id(stock_code_id):
    """
    根据股票代码ID获取股票代码
    
    Args:
        stock_code_id: 股票代码ID
        
    Returns:
        str: 股票代码，如果未找到返回None
    """
    if stock_code_id in stock_code_cache:
        return stock_code_cache[stock_code_id]
    
    try:
        stock = StockCodes.query.get(stock_code_id)
        if stock:
            stock_code_cache[stock_code_id] = stock.code
            return stock.code
        else:
            logging.warning(f"未找到股票代码ID {stock_code_id} 对应的股票信息")
            return None
    except Exception as e:
        logging.error(f"获取股票代码时发生错误: {e}")
        return None


def download_file():
    # 声明使用全局变量，记录下载状态、进度和停止下载标志
    global download_status, download_progress, stop_download

    # 使用下载锁，初始化下载状态和进度
    with download_lock:
        download_status = "进行中"  # 下载状态为进行中
        download_progress = 0  # 进度初始化为 0
        stop_download = False  # 重置停止下载的标志

    """启动下载任务"""
    today = date.today()  # 获取今天的日期
    current = datetime.now().date()  # 获取当前日期（不含时间部分）

    # 使用应用上下文以便于访问数据库和其他应用资源
    with current_app.app_context():

        # 计算符合条件的数据条数（需要下载且日期在今天之前）
        total_count = dlr.query.filter(
            dlr.download_status != 'success',  # 排除已下载成功的记录
            dlr.end_date < today,  # 下载日期在今天之前
            dlr.record_date < today  # 记录日期在今天之前
        ).count()

        if total_count == 0:
            logging.info("没有需要下载的数据。")  # 若无数据，记录日志
            with download_lock:
                download_status = "无数据下载"  # 更新状态为无数据
            return

        print(f'需要下载 {total_count} 个股票数据...')  # 输出需要下载的数据条数

        # 遍历需要下载的数据记录
        for i in range(total_count):
            # 检查是否需要停止下载
            with download_lock:
                if stop_download:
                    download_status = "已停止"  # 更新状态为已停止
                    download_progress = 0  # 进度清零
                    return  # 终止下载

            # 查询符合条件的第一条记录
            first_record = dlr.query.filter(
                dlr.download_status != 'success',
                dlr.end_date < today,
                dlr.record_date < today
            ).first()

            if not first_record:
                logging.info("没有符合条件的记录。")  # 若无记录，记录日志
                return

            # 获取股票代码
            stock_code = get_stock_code_by_id(first_record.stock_code_id)
            if not stock_code:
                logging.error(f'无法获取股票代码ID {first_record.stock_code_id} 对应的股票代码')
                # 标记为失败并继续下一个
                first_record.update_download_status(
                    status='failed',
                    error_msg=f'无法获取股票代码ID {first_record.stock_code_id} 对应的股票代码'
                )
                db.session.commit()
                continue

            # 获取记录的结束日期并计算需要下载的天数
            record_ending = first_record.end_date
            days = (current - record_ending).days  # 计算自结束日期到当前日期的天数差

            if days <= 0:
                logging.info(f'无最新1M数据: {stock_code}')  # 无更新数据，记录日志
                continue  # 跳过当前记录

            days = min(5, days)  # 限制下载天数最大值为5天
            
            # 更新下载状态为进行中
            first_record.update_download_status(status='processing')
            db.session.commit()

            try:
                # 下载数据，根据股票类型和指定的天数
                data, ending = download_1m_by_type(stock_code, days, StockType.STOCK_1M)

                if data.empty:
                    logging.info(f'无最新1M数据: {stock_code}')
                    # 更新状态为无数据
                    first_record.update_download_status(
                        status='failed',
                        error_msg='无最新数据（原状态为 no_data）'
                    )
                    db.session.commit()
                    continue  # 若无数据，跳过当前记录

                if ending > record_ending:  # 若结束日期更新
                    year_ = str(ending.year)

                    try:
                        # 保存数据至本地 CSV 文件
                        save_1m_to_csv(data, stock_code)
                        logging.info(f'成功保存 {stock_code} 数据到CSV文件')

                    except Exception as e:
                        logging.error(f'保存至CSV失败: {stock_code}, {e}')
                        # 标记为失败并继续下一个
                        first_record.update_download_status(
                            status='failed',
                            error_msg=f'保存至CSV失败: {str(e)}'
                        )
                        db.session.commit()
                        continue

                    # 更新数据库记录，标记下载成功
                    first_record.update_download_status(
                        status='success',
                        progress=100.0
                    )
                    first_record.end_date = ending
                    first_record.record_date = current
                    first_record.last_download_time = datetime.now()
                    first_record.downloaded_records = len(data)
                    db.session.commit()
                    
                    logging.info(f'成功下载 {stock_code} 的1分钟数据，共 {len(data)} 条记录')
                else:
                    # 若无数据更新，仅更新记录日期
                    first_record.record_date = current
                    first_record.last_download_time = datetime.now()
                    db.session.commit()

            except Exception as e:
                logging.error(f'下载 {stock_code} 数据时发生错误: {e}')
                # 标记为失败
                first_record.update_download_status(
                    status='failed',
                    error_msg=str(e)
                )
                db.session.commit()

            # 更新下载进度
            with download_lock:
                download_progress = round((i + 1) * (100 / total_count), 1)

        # 下载任务完成，更新下载状态和进度
        with download_lock:
            download_status = "已完成"  # 状态设为已完成
            download_progress = 100  # 进度设为 100%


@download_data_bp.route('/start-download', methods=['GET', 'POST'])
def start_download():
    global download_thread

    if download_thread is None or not download_thread.is_alive():
        @copy_current_request_context
        def run_download():
            download_file()

        download_thread = threading.Thread(target=run_download)
        download_thread.start()
        return jsonify({"message": "下载已开始"}), 200
    else:
        return jsonify({"message": "下载正在进行中"}), 400


@download_data_bp.route('/download-status', methods=['GET'])
def get_download_status():
    return jsonify({"status": download_status, "progress": download_progress}), 200


@download_data_bp.route('/stop-download', methods=['GET', 'POST'])
def stop_download_request():
    global stop_download

    with download_lock:
        stop_download = True  # 设置标志为 True，要求下载停止
        download_status = "请求停止中"  # 更新状态
    return jsonify({"message": "下载已请求停止"}), 200


# def load_progress():
@download_data_bp.route('/load_progress', methods=['GET'])
def load_progress():
    return render_template('download/progress.html')


@download_data_bp.route('/download_index_page')
def download_index_page():
    return render_template('download/股票下载.html')


@download_data_bp.route('/daily_renew_data', methods=['GET', 'POST'])
def daily_renew_data():
    # 下载股票每天的1M 数据
    rdd = RMDownloadData()
    rdd.daily_renew_data()
    return render_template('index.html')


@download_data_bp.route('/resample_to_daily_data', methods=['GET', 'POST'])
def resample_to_daily_data():
    month = None
    stock_code = None
    data_daily = None  # 默认情况下数据为空

    if request.method == 'POST':
        # 从表单获取参数
        stock_code = request.form.get('stock_code')
        month = request.form.get('month')

        if month and stock_code:
            file_name = f'{stock_code}.csv'

            data_path = StockDataPath.month_1m_data_path(month)

            data_1m = pd.read_csv(data_path)
            data_daily = ResampleData.resample_1m_data(data_1m, 'd')

            try:
                # 假设 ResampleData 和 pd.read_csv 是正确配置的

                flash("文件转换成功！", "success")
            except Exception as e:
                flash(f"文件转换失败: {e}", "danger")

    return render_template('download/resample_to_daily_data.html', stock_code=stock_code, month=month, data_daily=data_daily)


@download_data_bp.route('/download_stock_1m_close_data_today', methods=['GET', 'POST'])
def download_stock_1m_close_data_today():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        if stock_code:
            try:
                # 下载今日1分钟收盘数据
                data, _ = download_1m_by_type(stock_code, 1, StockType.STOCK_1M)
                if not data.empty:
                    # 保存数据
                    save_1m_to_csv(data, stock_code)
                    flash(f"成功下载 {stock_code} 的今日1分钟收盘数据", "success")
                else:
                    flash(f"未找到 {stock_code} 的今日数据", "warning")
            except Exception as e:
                flash(f"下载失败: {str(e)}", "danger")
    return render_template('download/success.html')


@download_data_bp.route('/download_stock_1m_close_data', methods=['GET', 'POST'])
def download_stock_1m_close_data():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        days = int(request.form.get('days', 5))
        if stock_code:
            try:
                # 下载历史1分钟收盘数据
                data, _ = download_1m_by_type(stock_code, days, StockType.STOCK_1M)
                if not data.empty:
                    # 保存数据
                    save_1m_to_csv(data, stock_code)
                    flash(f"成功下载 {stock_code} 的历史1分钟收盘数据", "success")
                else:
                    flash(f"未找到 {stock_code} 的历史数据", "warning")
            except Exception as e:
                flash(f"下载失败: {str(e)}", "danger")
    return render_template('download/success.html')


# @download_data_bp.route('/download_stock_daily_data', methods=['GET', 'POST'])
# def download_stock_daily_data():
#     if request.method == 'POST':
#         stock_code = request.form.get('stock_code')
#         if stock_code:
#             try:
#                 # 下载日线数据
#                 data, _ = download_1m_by_type(stock_code, 1, StockType.STOCK_1M)
#                 if not data.empty:
#                     # 转换为日线数据
#                     daily_data = ResampleData.resample_1m_data(data, 'd')
#                     daily_data = daily_data.fillna({'open': 0.0, 'close': 0.0,
#                                                   'high': 0.0, 'low': 0.0,
#                                                   'volume': 0, 'money': 0})
#                     # 保存数据
#                     save_daily_stock_data_to_sql(stock_code, daily_data)
#                     flash(f"成功下载 {stock_code} 的日线数据", "success")
#                 else:
#                     flash(f"未找到 {stock_code} 的数据", "warning")
#             except Exception as e:
#                 flash(f"下载失败: {str(e)}", "danger")
#     return render_template('download/success.html')


@download_data_bp.route('/download_fund_holdings', methods=['GET', 'POST'])
def download_fund_holdings():
    if request.method == 'POST':
        try:
            # 下载基金持仓数据
            rdd = RMDownloadData()
            rdd.download_fund_holdings()
            flash("成功下载基金持仓数据", "success")
        except Exception as e:
            flash(f"下载失败: {str(e)}", "danger")
    return render_template('download/success.html')


@download_data_bp.route('/download_minute_data_page')
def download_minute_data_page():
    return render_template('data/download_minute_data.html')
