from flask import render_template, request, redirect, url_for, flash, Blueprint
from App.my_code.downloads.DlEastMoney import DownloadData

dl_eastmoney_bp = Blueprint('download_eastmoney_data', __name__)


@dl_eastmoney_bp.route('/download_stock_1m_close_data_today', methods=['GET', 'POST'])
def download_stock_1m_close_data_today():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        print(f"股票代码：{stock_code}")

        if not stock_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_stock_1m_close_data_today'))
        else:
            # 假设 DownloadData.stock_1m_1day 返回 DataFrame
            data = DownloadData.stock_1m_1day(stock_code)
            print(data)
            flash('数据获取成功！')

            # 将 DataFrame 转换为 HTML 表格
            data_html = data.to_html(classes='table table-striped', index=False)  # 使用 Bootstrap 类增强样式
            return render_template('download/success.html', data_html=data_html)


@dl_eastmoney_bp.route('/download_stock_1m_5days_data', methods=['GET', 'POST'])
def download_stock_1m_5days_data():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        print(f"股票代码：{stock_code}")

        if not stock_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_stock_1m_close_data_today'))
        else:
            # 假设 DownloadData.stock_1m_1day 返回 DataFrame
            data = DownloadData.stock_1m_days(stock_code)
            print(data)
            flash('数据获取成功！')

            # 将 DataFrame 转换为 HTML 表格
            data_html = data.to_html(classes='table table-striped', index=False)  # 使用 Bootstrap 类增强样式
            return render_template('download/success.html', data_html=data_html)


@dl_eastmoney_bp.route('/download_board_1m_close_data_today', methods=['GET', 'POST'])
def download_board_1m_close_data_today():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        print(f"股票代码：{stock_code}")

        if not stock_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))
        else:
            # 假设 DownloadData.stock_1m_1day 返回 DataFrame
            data = DownloadData.board_1m_data(stock_code)
            flash('数据获取成功！')

            # 将 DataFrame 转换为 HTML 表格
            data_html = data.to_html(classes='table table-striped', index=False)  # 使用 Bootstrap 类增强样式
            return render_template('download/success.html', data_html=data_html)


@dl_eastmoney_bp.route('/download_board_1m_close_data_multiple_days', methods=['GET', 'POST'])
def download_board_1m_close_data_multiple_days():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        if not stock_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))
        else:
            # 假设 DownloadData.stock_1m_1day 返回 DataFrame
            data = DownloadData.board_1m_multiple(stock_code)
            flash('数据获取成功！')

            # 将 DataFrame 转换为 HTML 表格
            data_html = data.to_html(classes='table table-striped', index=False)  # 使用 Bootstrap 类增强样式
            return render_template('download/success.html', data_html=data_html)


@dl_eastmoney_bp.route('/download_funds_awkward_data', methods=['GET', 'POST'])
def download_funds_awkward_data():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        print(f"股票代码：{stock_code}")

        if not stock_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))

        else:
            # 假设 DownloadData.stock_1m_1day 返回 DataFrame
            data = DownloadData.funds_awkward(stock_code)
            flash('数据获取成功！')

            # 将 DataFrame 转换为 HTML 表格
            data_html = data.to_html(classes='table table-striped', index=False)  # 使用 Bootstrap 类增强样式
            return render_template('download/success.html', data_html=data_html)


@dl_eastmoney_bp.route('/download_funds_awkward_data_by_driver', methods=['GET', 'POST'])
def download_funds_awkward_data_by_driver():
    if request.method == 'POST':
        stock_code = request.form.get('stock_code')
        if not stock_code:
            flash('请填写完整信息！')
            return redirect(url_for('download_eastmoney_data.download_board_1m_close_data_today'))

        else:
            # 假设 DownloadData.stock_1m_1day 返回 DataFrame
            data = DownloadData.funds_awkward_by_driver(stock_code)
            flash('数据获取成功！')

            # 将 DataFrame 转换为 HTML 表格
            data_html = data.to_html(classes='table table-striped', index=False)  # 使用 Bootstrap 类增强样式
            return render_template('download/success.html', data_html=data_html)
