from App.codes.downloads.DlStockData import RMDownloadData, StockType, download_1m_by_type
import threading
from App.codes.utils.Normal import ResampleData
from flask import render_template, current_app, jsonify, Blueprint, copy_current_request_context, request, flash
from ..models.DownloadModels import Download1MRecord as dlr
from ..models.StockData1M import save_1m_stock_data_to_sql
from ..models.StockDataDaily import save_daily_stock_data_to_sql
from App.codes.RnnDataFile.stock_path import StockDataPath
import pandas as pd
from datetime import date, datetime
import logging
# import time

from App.codes.RnnDataFile.save_download import save_1m_to_csv

# 创建蓝图
dl_bp = Blueprint('dl_bp', __name__)

# 下载状态和进度的存储
download_status = "未开始"
download_progress = 0
download_thread = None
stop_download = False  # 用于控制下载停止
download_lock = threading.Lock()  # 用于保护全局变量的锁


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
    status_success = f'success-{current}'  # 标记成功的状态，包含当前日期

    # 使用应用上下文以便于访问数据库和其他应用资源
    with current_app.app_context():

        # 计算符合条件的数据条数（需要下载且日期在今天之前）
        total_count = dlr.query.filter(
            dlr.es_download_status != status_success,  # 排除已下载成功的记录
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
            # time.sleep(2)

            first_record = dlr.query.filter(
                dlr.es_download_status != status_success,
                dlr.end_date < today,
                dlr.record_date < today
            ).first()

            if not first_record:
                logging.info("没有符合条件的记录。")  # 若无记录，记录日志
                return

            # 获取记录的结束日期并计算需要下载的天数
            record_ending = first_record.end_date
            days = (current - record_ending).days  # 计算自结束日期到当前日期的天数差

            if days <= 0:
                logging.info(f'无最新1M数据: {first_record.name}, {first_record.code}')  # 无更新数据，记录日志
                continue  # 跳过当前记录

            days = min(5, days)  # 限制下载天数最大值为5天
            stock_type = StockType.BOARD_1M if first_record.classification == '行业板块' else StockType.STOCK_1M

            # 下载数据，根据股票类型和指定的天数
            data, ending = download_1m_by_type(first_record.es_code, days, stock_type)

            if data.empty:
                logging.info(f'无最新1M数据: {first_record.name}, {first_record.code}')
                continue  # 若无数据，跳过当前记录

            if ending > record_ending:  # 若结束日期更新
                year_ = str(ending.year)

                try:
                    # 保存1m数据至 MySQL 数据库
                    save_1m_stock_data_to_sql(first_record.code, year_, data)

                except Exception as e:
                    logging.error(f'保存至 MySQL 失败: {first_record.name}, {first_record.code}, {e}')
                    # continue  # 保存失败时继续下一个记录

                # 保存数据至本地 CSV 文件
                save_1m_to_csv(data, first_record.code)

                # 若非行业板块数据，保存为每日数据
                if first_record.classification != '行业板块':
                    daily_data = ResampleData.resample_1m_data(data, 'd')
                    daily_data = daily_data.fillna({'open': 0.0, 'close': 0.0,
                                                    'high': 0.0, 'low': 0.0,
                                                    'volume': 0, 'money': 0})  # 填充缺失值
                    save_daily_stock_data_to_sql(first_record.code, daily_data)

                # 更新数据库记录，标记下载成功
                first_record.update_by_id(
                    first_record.id,
                    end_date=ending,
                    record_date=current,
                    es_download_status=status_success
                )
            else:
                # 若无数据更新，仅更新记录日期
                first_record.update_by_id(
                    first_record.id,
                    end_date=ending,
                    record_date=current
                )

            # 更新下载进度
            with download_lock:
                download_progress = round((i + 1) * (100 / total_count), 1)  # 计算进度百分比

        # 下载任务完成，更新下载状态和进度
        with download_lock:
            download_status = "已完成"  # 状态设为已完成
            download_progress = 100  # 进度设为 100%


@dl_bp.route('/start-download', methods=['GET', 'POST'])
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


@dl_bp.route('/download-status', methods=['GET'])
def get_download_status():
    return jsonify({"status": download_status, "progress": download_progress}), 200


@dl_bp.route('/stop-download', methods=['GET', 'POST'])
def stop_download_request():
    global stop_download

    with download_lock:
        stop_download = True  # 设置标志为 True，要求下载停止
        download_status = "请求停止中"  # 更新状态
    return jsonify({"message": "下载已请求停止"}), 200


# def load_progress():
@dl_bp.route('/load_progress', methods=['GET'])
def load_progress():
    return render_template('download/progress.html')


@dl_bp.route('/download_index_page')
def download_index_page():
    return render_template('download/股票下载.html')


@dl_bp.route('/daily_renew_data', methods=['GET', 'POST'])
def daily_renew_data():
    # 下载股票每天的1M 数据
    rdd = RMDownloadData()
    rdd.daily_renew_data()
    return render_template('index.html')


@dl_bp.route('/resample_to_daily_data', methods=['GET', 'POST'])
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
