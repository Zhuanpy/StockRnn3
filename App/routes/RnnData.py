from App.my_code.RnnModel.DataProcessing import process_stock_data_for_year
from flask import render_template, url_for, jsonify, Blueprint, copy_current_request_context, request, flash
from ..models.DownloadModels import Download1MRecord as dlr
from ..models.StockData1M import save_1m_stock_data_to_sql
from ..models.StockDataDaily import save_daily_stock_data_to_sql
from App.my_code.RnnDataFile.stock_path import StockDataPath
import pandas as pd
from datetime import date, datetime
import logging
import traceback
# import time

# 创建蓝图
RnnData = Blueprint('RnnData', __name__)


@RnnData.route('/RnnData/rnn_data_page', methods=['GET', 'POST'])
def rnn_data_page():
    return render_template('RNN模型/模型数据处理.html')

# 计算15分钟原始数据
@RnnData.route('/RnnData/original_15M/<year>', methods=['GET', 'POST'])
def original_15M(year):
    process_stock_data_for_year(year)
    return url_for('RnnData.rnn_data_page')

# 处理15分钟基础数据
@RnnData.route('/process_base_data/<year>', methods=['POST'])
def process_base_data(year):
    try:
        # 验证年份
        year = int(year)
        if not (2000 <= year <= 2099):
            return jsonify({
                'status': 'error',
                'message': '年份必须在2000-2099之间'
            }), 400

        # 处理基础数据
        process_stock_data_for_year(str(year))
        
        return jsonify({
            'status': 'success',
            'message': f'{year}年基础数据处理完成',
            'data': {
                'year': year,
                'processed_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        })

    except Exception as e:
        logging.error(f"处理基础数据时出错: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'处理失败: {str(e)}'
        }), 500


# 处理15分钟标准化数据
@RnnData.route('/process_standard_data/<year>/<quarter>', methods=['POST'])
def process_standard_data(year, quarter):
    try:
        # 验证年份
        year = int(year)
        if not (2000 <= year <= 2099):
            return jsonify({
                'status': 'error',
                'message': '年份必须在2000-2099之间'
            }), 400

        # 处理全年数据
        if quarter == 'full':
            # 这里添加处理全年数据的逻辑
            result = process_full_year_data(str(year))
            message = f'{year}年全年数据标准化处理完成'
        else:
            # 验证季度
            quarter = int(quarter)
            if not (1 <= quarter <= 4):
                return jsonify({
                    'status': 'error',
                    'message': '季度必须在1-4之间'
                }), 400
            
            # 这里添加处理单个季度数据的逻辑
            result = process_quarter_data(str(year), quarter)
            message = f'{year}年第{quarter}季度数据标准化处理完成'

        return jsonify({
            'status': 'success',
            'message': message,
            'data': {
                'year': year,
                'quarter': quarter,
                'processed_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result
            }
        })

    except Exception as e:
        logging.error(f"处理标准化数据时出错: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({
            'status': 'error',
            'message': f'处理失败: {str(e)}'
        }), 500


def process_full_year_data(year):
    """处理全年数据的具体实现"""
    try:
        # 这里添加处理全年数据的具体逻辑
        # 可以调用现有的处理函数或添加新的处理逻辑
        return {
            'status': 'success',
            'processed_files': [],  # 处理的文件列表
            'statistics': {}  # 处理的统计信息
        }
    except Exception as e:
        logging.error(f"处理全年数据时出错: {str(e)}")
        raise


def process_quarter_data(year, quarter):
    """处理季度数据的具体实现"""
    try:
        # 这里添加处理季度数据的具体逻辑
        # 可以调用现有的处理函数或添加新的处理逻辑
        return {
            'status': 'success',
            'processed_files': [],  # 处理的文件列表
            'statistics': {}  # 处理的统计信息
        }
    except Exception as e:
        logging.error(f"处理季度数据时出错: {str(e)}")
        raise


# 生成及保存模型训练数据