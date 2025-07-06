from flask import render_template, request, redirect, url_for, flash, Blueprint
from App.codes.downloads.DlEastMoney import DownloadData
from App.utils.file_utils import get_stock_data_path, get_processed_data_path
import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

dl_eastmoney_bp = Blueprint('download_eastmoney_data', __name__)

def save_stock_data(data: pd.DataFrame, stock_code: str, data_type: str = '1m') -> None:
    """
    保存股票数据到文件
    
    Args:
        data: 股票数据DataFrame
        stock_code: 股票代码
        data_type: 数据类型，默认为'1m'
    """
    try:
        # 获取保存路径
        file_path = get_stock_data_path(stock_code, data_type=data_type)
        
        # 如果文件存在，读取并合并数据
        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            existing_data['date'] = pd.to_datetime(existing_data['date'])
            data['date'] = pd.to_datetime(data['date'])
            combined_data = pd.concat([existing_data, data]).drop_duplicates(subset=['date'])
            combined_data = combined_data.sort_values('date')
        else:
            combined_data = data
        
        # 保存数据
        combined_data.to_csv(file_path, index=False)
        logger.info(f"成功保存数据: {stock_code}, 类型: {data_type}")
        
    except Exception as e:
        logger.error(f"保存数据失败: {stock_code}, 类型: {data_type}, 错误: {str(e)}")
        raise

@dl_eastmoney_bp.route('/download_stock_1m_close_data_today_eastmoney', methods=['GET', 'POST'])
def download_stock_1m_close_data_today_eastmoney():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        logger.info(f"开始下载股票数据: {stock_code}")

        if not stock_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_stock_1m_close_data_today_eastmoney'))
        
        try:
            # 下载数据
            data = DownloadData.stock_1m_1day(stock_code)
            
            # 保存数据
            save_stock_data(data, stock_code, '1m')
            
            flash('数据获取并保存成功！')
            data_html = data.to_html(classes='table table-striped', index=False)
            return render_template('data/success.html', data_html=data_html)
            
        except Exception as e:
            logger.error(f"下载数据失败: {stock_code}, 错误: {str(e)}")
            flash(f'下载失败: {str(e)}')
            return redirect(url_for('download_eastmoney_data.download_stock_1m_close_data_today_eastmoney'))
    
    # 处理 GET 请求
    return render_template('data/股票下载.html')

@dl_eastmoney_bp.route('/download_stock_1m_5days_data', methods=['GET', 'POST'])
def download_stock_1m_5days_data():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        logger.info(f"开始下载5天股票数据: {stock_code}")

        if not stock_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_stock_1m_close_data_today_eastmoney'))
        
        try:
            # 下载数据
            data = DownloadData.stock_1m_days(stock_code)
            
            # 保存数据
            save_stock_data(data, stock_code, '1m')
            
            flash('数据获取并保存成功！')
            data_html = data.to_html(classes='table table-striped', index=False)
            return render_template('data/success.html', data_html=data_html)
            
        except Exception as e:
            logger.error(f"下载数据失败: {stock_code}, 错误: {str(e)}")
            flash(f'下载失败: {str(e)}')
            return redirect(url_for('download_eastmoney_data.download_stock_1m_5days_data'))

@dl_eastmoney_bp.route('/download_board_1m_close_data_today', methods=['GET', 'POST'])
def download_board_1m_close_data_today():
    if request.method == 'POST':
        board_code = request.form.get('stock_code')
        logger.info(f"开始下载板块数据: {board_code}")

        if not board_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))
        
        try:
            # 下载数据
            data = DownloadData.board_1m_data(board_code)
            
            # 保存数据
            save_stock_data(data, board_code, 'board_1m')
            
            flash('数据获取并保存成功！')
            data_html = data.to_html(classes='table table-striped', index=False)
            return render_template('data/success.html', data_html=data_html)
            
        except Exception as e:
            logger.error(f"下载数据失败: {board_code}, 错误: {str(e)}")
            flash(f'下载失败: {str(e)}')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))

@dl_eastmoney_bp.route('/download_board_1m_close_data_multiple_days', methods=['GET', 'POST'])
def download_board_1m_close_data_multiple_days():
    if request.method == 'POST':
        board_code = request.form.get('stock_code')
        logger.info(f"开始下载多日板块数据: {board_code}")

        if not board_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))
        
        try:
            # 下载数据
            data = DownloadData.board_1m_multiple(board_code)
            
            # 保存数据
            save_stock_data(data, board_code, 'board_1m')
            
            flash('数据获取并保存成功！')
            data_html = data.to_html(classes='table table-striped', index=False)
            return render_template('data/success.html', data_html=data_html)
            
        except Exception as e:
            logger.error(f"下载数据失败: {board_code}, 错误: {str(e)}")
            flash(f'下载失败: {str(e)}')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_multiple_days'))

@dl_eastmoney_bp.route('/download_funds_awkward_data', methods=['GET', 'POST'])
def download_funds_awkward_data():
    if request.method == 'POST':
        fund_code = request.form.get('stock_code')
        logger.info(f"开始下载基金数据: {fund_code}")

        if not fund_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))
        
        try:
            # 下载数据
            data = DownloadData.funds_awkward(fund_code)
            
            # 保存数据
            file_path = get_stock_data_path(fund_code, data_type='funds')
            data.to_csv(file_path, index=False)
            
            flash('数据获取并保存成功！')
            data_html = data.to_html(classes='table table-striped', index=False)
            return render_template('data/success.html', data_html=data_html)
            
        except Exception as e:
            logger.error(f"下载数据失败: {fund_code}, 错误: {str(e)}")
            flash(f'下载失败: {str(e)}')
            return redirect(url_for('download_eastmoney_data.download_funds_awkward_data'))

@dl_eastmoney_bp.route('/download_funds_awkward_data_by_driver', methods=['GET', 'POST'])
def download_funds_awkward_data_by_driver():
    if request.method == 'POST':
        fund_code = request.form.get('stock_code')
        logger.info(f"开始下载基金数据(driver): {fund_code}")

        if not fund_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))
        
        try:
            # 下载数据
            data = DownloadData.funds_awkward_by_driver(fund_code)
            
            # 保存数据
            file_path = get_stock_data_path(fund_code, data_type='funds')
            data.to_csv(file_path, index=False)
            
            flash('数据获取并保存成功！')
            data_html = data.to_html(classes='table table-striped', index=False)
            return render_template('data/success.html', data_html=data_html)
            
        except Exception as e:
            logger.error(f"下载数据失败: {fund_code}, 错误: {str(e)}")
            flash(f'下载失败: {str(e)}')
            return redirect(url_for('download_eastmoney_data.download_funds_awkward_data_by_driver'))
