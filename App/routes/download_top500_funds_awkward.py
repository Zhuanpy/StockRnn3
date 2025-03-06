import logging
import time

from flask import Blueprint, render_template, jsonify, copy_current_request_context, current_app
import threading
from datetime import date

from App.models.StockRecordModels import Top500FundRecord
from App.models.FundsAwkwardModels import funds_holdings_to_sql
from App.my_code.downloads.DlEastMoney import DownloadData

# 创建蓝图
dl_funds_awkward_bp = Blueprint('dl_funds_awkward_bp', __name__)


# 封装任务状态
class DownloadTaskState:
    def __init__(self):
        self.status = "未开始"
        self.progress = 0
        self.stop = False

    def reset(self):
        self.status = "未开始"
        self.progress = 0
        self.stop = False


task_state = DownloadTaskState()
download_thread = None
download_lock = threading.Lock()


def download_fund_data():
    """
    下载基金持仓数据任务。

    此函数用于从数据库中获取需要处理的基金记录，逐一下载数据并存储至数据库，
    并动态更新下载任务的状态和进度。
    """
    # 获取当前日期作为下载日期
    download_date = date.today()
    # 设置任务成功和失败的标志状态
    status_success = f'success-{download_date}'  # 成功状态标志
    status_failure = f'failure-{download_date}'  # 失败状态标志
    print(status_success)  # 打印成功状态（可选）

    # 初始化 Flask 应用的上下文，并获取下载任务的锁，确保多线程操作安全
    with current_app.app_context(), download_lock:
        task_state.reset()  # 重置任务状态
        task_state.status = "进行中"  # 设置初始状态为“进行中”

    # 从数据库查询所有未完成下载任务的基金记录
    records_to_process = Top500FundRecord.query.filter(Top500FundRecord.status != status_success).all()
    total_count = len(records_to_process)  # 记录总数

    # 如果没有需要处理的记录，记录日志并更新任务状态
    if not records_to_process:
        logging.info("没有需要下载的基金数据。")
        with download_lock:
            task_state.status = "无数据下载"  # 更新状态为“无数据下载”
        return

    # 记录需要处理的基金记录总数
    logging.info(f"需要下载 {total_count} 条基金数据...")

    # 遍历每条基金记录，逐一处理
    for i, record in enumerate(records_to_process):
        # 检查任务状态，如果被标记为停止，则中止任务
        time.sleep(5)  # 延时 0.1 秒，以避免频繁访问数据库
        with download_lock:
            if task_state.stop:
                task_state.status = "已停止"  # 更新状态为“已停止”
                logging.info("下载任务被用户中止。")
                return

        try:
            # 打印当前下载日期（调试用途）

            # 下载基金持仓数据（调用外部接口或函数）
            data = DownloadData.funds_awkward(record.code)
            data['fund_name'] = record.name
            data['fund_code'] = record.code
            print("当前下载日期：", download_date)
            print(data)
            # 将下载数据存入数据库
            # table_name, data
            table_name = f"awkward_{download_date}".replace("-", "")
            funds_holdings_to_sql(table_name, data)
            # 更新记录状态为成功，并记录下载日期
            record.update_by_id(record.id, status=status_success, date=download_date)
            logging.info(f"成功下载基金数据: {record.name} ({record.code})")

        except Exception as e:
            # 捕获下载或存储过程中发生的异常，记录日志并更新状态为失败
            logging.error(f"下载失败: {record.name}, {record.code}, 错误: {e}")
            record.update_by_id(record.id, status=status_failure, date=download_date)
            continue  # 跳过当前记录，继续处理下一个

        # 动态更新任务进度（以百分比形式）
        with download_lock:
            task_state.progress = min(round((i + 1) * (100 / total_count), 1), 100)
            logging.info(f"下载进度更新: {task_state.progress}%")

    # 下载完成后，更新任务状态为“已完成”并设置进度为 100%
    with download_lock:
        task_state.status = "已完成"  # 设置状态为“已完成”
        task_state.progress = 100  # 设置进度为 100%
        logging.info("所有基金数据下载任务已完成。")


@dl_funds_awkward_bp.route("/download_funds_awake_index")
def download_funds_awake_index():
    """显示下载任务的状态页面。"""
    return render_template("download/下载基金持仓数据.html", status=task_state.status, progress=task_state.progress)


@dl_funds_awkward_bp.route("/start_download", methods=["GET", "POST"])
def start_download():
    global download_thread

    if download_thread is None or not download_thread.is_alive():
        @copy_current_request_context
        def run_download():
            download_fund_data()

        download_thread = threading.Thread(target=run_download)
        download_thread.start()
        return jsonify({"message": "下载已开始"}), 200
    else:
        return jsonify({"message": "下载正在进行中"}), 400


@dl_funds_awkward_bp.route("/stop_download", methods=["GET", "POST"])
def stop_download_route():
    """终止下载任务的接口。"""
    with download_lock:
        task_state.stop = True
    logging.info("下载任务请求停止。")
    return jsonify({"message": "下载任务已停止。"})


@dl_funds_awkward_bp.route("/status", methods=["GET"])
def status():
    """获取当前下载任务的状态和进度。"""
    with download_lock:
        return jsonify({"status": task_state.status, "progress": task_state.progress})
