# -*- coding: utf-8 -*-
import time
import json
import re
from selenium import webdriver
from bs4 import BeautifulSoup as soup
import pandas as pd
from download_utils import page_source, WebDriver
from download_utils import UrlCode
from App.my_code.RnnDataFile.parser import my_headers, my_url
import logging

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 5000)

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def show_download(freq: str, code: str) -> None:
    """
    使用 logging 显示下载成功的信息。

    参数:
        freq (str): 数据频率，如 '1m'。
        code (str): 股票代码。
    """
    logging.info(f'Success Download {freq} Data: {code}')


def return_FundsData(source: str, date_new: pd.Timestamp, table_index=1, relevant_columns=None) -> pd.DataFrame:
    """
    从网页源代码中提取并处理资金数据。

    参数: source (str): 包含HTML表格数据的网页源代码。 date_new (pd.Timestamp): 交易日期，会转换为datetime格式并添加到数据框中。 table_index (int,
    optional): 指定要读取的表格索引，默认值为1。 relevant_columns (list of str, optional): 返回的数据框中所需的列名，默认值为['trade_date',
    'stock_code', 'stock_name', 'industry']。

    返回:
        pd.DataFrame: 包含处理后的资金数据的数据框。
                       包括指定的列（默认为['trade_date', 'stock_code', 'stock_name', 'industry']）。
    """

    if relevant_columns is None:
        relevant_columns = ['trade_date', 'stock_code', 'stock_name', 'industry']

    # 读取指定索引的数据表
    df = pd.read_html(source)[table_index]

    # 定义所有列名
    columns = ['序号', 'stock_code', 'stock_name', '相关', '今日收盘价', '今日涨跌幅', '今日持股股数',
               '今日持股市值', '今日持股占流通股比', '今日持股占总股本比', '今日增持股数',
               '今日增持市值', '今日增持市值增幅', '今日增持占流通股比', '今日增持占总股本比', 'industry']

    # 为DataFrame赋予列名
    df.columns = columns

    # 添加交易日期列
    df['trade_date'] = pd.to_datetime(date_new)

    # 只选择需要的列并返回
    result_df = df[relevant_columns]

    # 确保stock_code为字符串类型
    result_df['stock_code'] = result_df['stock_code'].astype(str)

    return result_df


def convert_currency_unit(unit: str):
    """
    货币单位转换函数 (Unit conversion)

    参数:
        x (str): 货币单位，支持 '亿', '万', '百万', '千万' 等。

    返回:
        int: 对应货币单位的数值，如果输入单位不匹配，返回1。
    """

    # 使用字典映射单位与数值
    unit_mapping = {
        '亿': 100000000,
        '万': 10000,
        '百万': 1000000,
        '千万': 10000000}

    # 返回对应的数值，如果单位不匹配，返回1

    return unit_mapping.get(unit, 1)


def funds_data_clean(data):
    """
        清理并转换资金数据。

        参数:
            data (pd.DataFrame): 输入的数据框，包含原始资金数据。

        返回:
            pd.DataFrame: 清理并转换后的资金数据。
        """
    # 将数据转为DataFrame并选择所需的列
    data = pd.DataFrame(data.values).iloc[:, [1, 5, 6, 7, 9, 12]]

    # 重命名列
    data.columns = ['板块', 'NkPT市值', 'NkPT占板块比', 'NkPT占北向资金比', 'NRPT市值', 'NRPT占北向资金比']

    # 定义一个函数来处理单位转换和数值计算
    def convert_value(value):
        unit = value[-1]  # 提取单位
        number = float(value[:-1])  # 提取数字部分并转换为浮点数
        return number * convert_currency_unit(unit)

    # 应用转换函数到NkPT市值和NRPT市值列
    data['NkPT市值'] = data['NkPT市值'].apply(convert_value)
    data['NRPT市值'] = data['NRPT市值'].apply(convert_value)

    return data


def parse_json(source: str, match: bool) -> list:
    """
    解析 JSON 数据。

    参数:
        source (str): 原始数据字符串。
        match (bool): 是否进行正则匹配。

    返回:
        list: 解析后的数据列表。
    """
    if match:
        pattern = re.compile(r'\((.*?)\)', re.S)
        json_str = re.findall(pattern, source)[0]

    else:
        json_str = source

    return json.loads(json_str)['data']['trends']


def process_data(df: pd.DataFrame, multiple: bool) -> pd.DataFrame:
    """
    处理并清理数据。

    参数:
        df (pd.DataFrame): 原始数据框。
        multiple (bool): 是否将09:30数据合并为09:31数据。

    返回:
        pd.DataFrame: 清理后的数据框。
    """
    if df.empty:
        return df

    # 转换数据类型
    df['date'] = pd.to_datetime(df['date'])
    df[['open', 'close', 'high', 'low', 'volume', 'money']] = df[
        ['open', 'close', 'high', 'low', 'volume', 'money']].astype(float)
    df['volume'] = (df['volume'] * 100).astype('int64')
    df[['volume', 'money']] = df[['volume', 'money']].astype('int64')

    if multiple:
        # 添加日期部分用于分组
        df['day'] = df['date'].dt.date
        df['time'] = df['date'].dt.time

        # 合并09:30数据到09:31
        df.loc[df['time'] == pd.Timestamp('09:30:00').time(), 'time'] = pd.Timestamp('09:31:00').time()

        # 按日期和时间进行分组聚合
        grouped = df.groupby(['day', 'time']).agg({
            'date': 'last',
            'open': 'first',
            'close': 'last',
            'high': 'max',
            'low': 'min',
            'volume': 'sum',
            'money': 'sum'
        }).reset_index(drop=False)

        grouped = grouped.drop(columns=['day', 'time'])

        return grouped

    else:
        # 处理单日数据的情况
        # 合并09:30 数据 到09:31
        if df.iloc[0]['date'].time() == pd.Timestamp('09:30:00').time():

            df.loc[1, ['volume', 'money']] += df.loc[0, ['volume', 'money']]

            df = df.iloc[1:].reset_index(drop=True)

        return df


def get_1m_data(source: str, match: bool = False, multiple: bool = False) -> pd.DataFrame:
    """
    获取1分钟数据并进行清理。

    参数:
        source (str): 原始数据源。
        match (bool): 是否进行正则匹配。
        multiple (bool): 是否将09:30数据合并为09:31数据。

    返回:
        pd.DataFrame: 清理后的数据框。
    """
    trends = parse_json(source, match)
    columns = ['date', 'open', 'close', 'high', 'low', 'volume', 'money']
    df = pd.DataFrame([x.split(',') for x in trends], columns=columns)

    data = process_data(df, multiple)

    return data

class DownloadData:
    """
    从东方财富下载数据
    """

    @staticmethod
    def _get_source(url: str, headers: dict) -> str:

        """
        获取页面源代码。

        参数:
            url (str): 请求的URL。
            headers (dict): 请求头信息。

        返回:
            str: 页面源代码。
        """
        try:
            return page_source(url, headers=headers)

        except Exception as e:
            logging.error(f"Error retrieving source from {url}: {e}")
            return ""

    @staticmethod
    def _handle_empty_source(code: str):
        """
        处理空数据源的情况并记录警告信息。

        参数:
            code (str): 股票代码。
        """
        info_text = f"Failed to retrieve data for {code}. Source is empty."
        logging.warning(info_text)
        return pd.DataFrame()

    @classmethod
    def stock_1m_1day(cls, code: str) -> pd.DataFrame:
        """
        从东方财富网下载 1 day , 1分钟股票数据。

        参数:
            code (str): 股票代码。

        返回:
            pd.DataFrame: 下载的股票数据。
        """
        headers = my_headers('stock_1m_data')
        url = my_url('stock_1m_data').format(UrlCode(code))
        source = cls._get_source(url, headers)
        if not source:
            return cls._handle_empty_source(code)

        dl = get_1m_data(source, match=True)

        show_download('1m', code)

        return dl

    @classmethod
    def stock_1m_days(cls, code: str, days: int = 5) -> pd.DataFrame:
        """
        从东方财富网下载 N days , 1分钟股票数据。

        参数:
            code (str): 股票代码。
            days (int): 需要下载的天数，默认为5天。

        返回:
            pd.DataFrame: 下载的股票数据。
        """
        headers = my_headers('stock_1m_multiple_days')
        url = my_url('stock_1m_multiple_days').format(days, UrlCode(code))
        source = cls._get_source(url, headers)

        if not source:
            return cls._handle_empty_source(code)

        dl = get_1m_data(source, match=True, multiple=True)

        show_download('1m', code)

        return dl

    @classmethod
    def board_1m_data(cls, code: str):
        headers = my_headers('board_1m_data')
        url = my_url('board_1m_data').format(code)
        source = page_source(url=url, headers=headers)
        dl = get_1m_data(source, match=True, multiple=False)

        show_download('1m', code)  # 打印下载
        return dl

    @classmethod
    def board_1m_multiple(cls, code: str, days=5):
        headers = my_headers('board_1m_multiple_days')
        url = my_url('board_1m_multiple_days').format(code, days)
        source = page_source(url=url, headers=headers)

        if not source:
            # todo 保存下这个日志
            # error downloading {code} data from 东方财富: {ex}'
            logging.warning(f"Failed to retrieve data for {code}. Source is empty.")
            return pd.DataFrame()

        dl = get_1m_data(source, match=False, multiple=True)
        show_download('1m', code)
        return dl

    @classmethod
    def funds_to_stock(cls):

        """
        从东方财富网下载北向资金流入个股数据：
        下载北向资金每日流向数据，通过北向资金流入，选择自己的股票池;
        北向资金已经下载数据；
        """

        # 北向资金个股流入个股网址
        page1 = 'http://data.eastmoney.com/hsgtcg/list.html'
        page2 = '/html/body/div[1]/div[8]/div[2]/div[2]/div[2]/div[3]/div[3]/div[1]/a[2]'
        page3 = '/html/body/div[1]/div[8]/div[2]/div[2]/div[2]/div[3]/div[3]/div[1]/a[4]'

        path_date = '/html/body/div[1]/div[8]/div[2]/div[2]/div[1]/div[1]/div/span'

        driver = webdriver.Chrome()
        driver.get(page1)

        new_date = driver.find_element('xpath', path_date).text[1:-1]
        new_date = pd.to_datetime(new_date)

        # 获取第1页50条数据
        source01 = driver.page_source
        dl01 = return_FundsData(source01, new_date)

        # 获取第2页50条数据
        driver.find_element('xpath', page2).click()
        time.sleep(6)
        source02 = driver.page_source
        dl02 = return_FundsData(source02, new_date)

        # 获取第3页50条数据
        driver.find_element('xpath', page3).click()
        time.sleep(6)
        source03 = driver.page_source
        dl03 = return_FundsData(source03, new_date)
        driver.close()

        # 合并数据：
        data = pd.concat([dl01, dl02, dl03], ignore_index=True).reset_index(drop=True)

        print(f'东方财富下载{new_date}日北向资金流入个股据成功;')

        return data

    @classmethod
    def funds_to_stock2(cls):
        """
        ideal:
        try to use the web link download data;
        # http://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery112309232266440254648_1657933725762&sortColumns=
        ADD_MARKET_CAP&sortTypes=-1&pageSize=50&pageNumber=1&reportName=RPT_MUTUAL_STOCK_NORTHSTA&columns=
        ALL&source=WEB&client=WEB&filter=(TRADE_DATE%3D%272022-07-15%27)(INTERVAL_TYPE%3D%221%22)

        target:
        last function:
        1. page size = 200;
        2. down full data
        """

        page_size = 50
        # date_ = pd.to
        w1 = 'http://datacenter-web.eastmoney.com/api/data/v1/get?callback=jQuery112309232266440254648_1657933725762' \
             '&sortColumns= '
        w2 = f'ADD_MARKET_CAP&sortTypes=-1&pageSize={page_size}&pageNumber=1&reportName=RPT_MUTUAL_STOCK_NORTHSTA' \
             f'&columns= '
        w3 = 'ALL&source=WEB&client=WEB&filter=(TRADE_DATE%3D%272022-07-16%27)(INTERVAL_TYPE%3D%221%22)'
        web = f'{w1}{w2}{w3}'
        print(web)
        pass

    @classmethod
    def funds_month_history(cls):  # 北向资金近1个月流入

        headers = my_headers('funds_month_history')

        url = my_url('funds_month_history')

        source = page_source(url=url, headers=headers)

        p1 = re.compile(r'[(](.*?)[)]', re.S)  # 最小匹配
        dl = re.findall(p1, source)[0]
        dl = pd.DataFrame(data=json.loads(dl)['result']['data'])
        dl = dl[['TRADE_DATE', 'NET_INFLOW_SH', 'NET_INFLOW_SZ', 'NET_INFLOW_BOTH']]
        dl.loc[:, 'TRADE_DATE'] = pd.to_datetime(dl['TRADE_DATE']).dt.date
        dl = dl.rename(columns={'TRADE_DATE': 'trade_date'})
        print('东方财富下载近一个月北向资金数据成功;')
        return dl

    @classmethod
    def funds_daily_data(cls):
        web_01 = 'https://data.eastmoney.com/hsgt/'
        driver = webdriver.Chrome()
        driver.set_page_load_timeout(60)
        driver.set_script_timeout(60)
        driver.get(web_01)

        # 更新时间 07-30
        update_xpath = '/html/body/div[1]/div[8]/div[2]/div[2]/div[3]/div[1]/div[3]/span'

        # 沪股通 净流入: SH money xpath， 深股通 净流入: SZ money xpath ， 北向 净流入: North_sum_xpath
        hmx = '/html/body/div[1]/div[8]/div[2]/div[2]/div[3]/div[6]/ul[1]/li[1]/span[2]/span/span'
        zmx = '/html/body/div[1]/div[8]/div[2]/div[2]/div[3]/div[6]/ul[1]/li[2]/span[2]/span/span'
        nsx = '/html/body/div[1]/div[8]/div[2]/div[2]/div[3]/div[6]/ul[1]/li[3]/span[2]/span/span'

        update = driver.find_element('xpath', update_xpath).text
        money_sh = float(driver.find_element('xpath', hmx).text[:-2]) * 100
        money_sz = float(driver.find_element('xpath', zmx).text[:-2]) * 100
        sum_north = float(driver.find_element('xpath', nsx).text[:-2]) * 100

        driver.close()

        dic_ = {'trade_date': [pd.to_datetime(update)],
                'NET_INFLOW_SH': [money_sh],
                'NET_INFLOW_SZ': [money_sz],
                'NET_INFLOW_BOTH': [sum_north]}

        df = pd.DataFrame(data=dic_)

        print(f'东方财富下载{update}日北向资金成功;')
        return df

    @classmethod
    def funds_to_sectors(cls, date_: str):

        """
        north funds to sectors data
        """

        headers = my_headers('funds_to_sectors')

        url = my_url('funds_to_sectors').format(date_)
        # print(url)
        # exit()
        source_ = page_source(url=url, headers=headers)

        try:
            p1 = re.compile(r'[(](.*?)[)]', re.S)

            page_data = re.findall(p1, source_)
            json_data = json.loads(page_data[0])
            json_data = json_data['result']['data']
            # print(json_data)
            value_list = []
            for i in range(len(json_data)):
                values = list(json_data[i].values())
                value_list.append(values)

            key_list = list(json_data[0])

            df = pd.DataFrame(data=value_list, columns=key_list)

            columns = ['SECURITY_CODE', 'BOARD_CODE', 'BOARD_NAME', 'TRADE_DATE', 'COMPOSITION_QUANTITY',
                       'ADD_MARKET_CAP', 'BOARD_VALUE', 'HK_VALUE', 'HK_BOARD_RATIO', 'MAXADD_SECURITY_CODE',
                       'MAXADD_SECURITY_NAME', 'MINADD_SECURITY_CODE', 'MINADD_SECURITY_NAME',
                       'MAXADD_RATIO_SECURITY_NAME', 'MAXADD_RATIO_SECURITY_CODE',
                       'MINADD_RATIO_SECURITY_NAME', 'MINADD_RATIO_SECURITY_CODE']

            df = df[columns]

            df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE']).dt.date

        except TypeError:
            print(f'东方财富下载 Funds to Sectors 数据异常;')
            df = pd.DataFrame(data=None)

        return df

    @classmethod
    def industry_list(cls):  # 下载板块组成
        web = 'http://quote.eastmoney.com/center/boardlist.html#industry_board'
        driver = webdriver.Chrome()
        driver.get(web)

        source = driver.page_source
        bs_data = soup(source, 'html.parser')
        board_data = bs_data.find('li', class_='sub-items menu-industry_board-wrapper')
        board_data = board_data.find_all('li')
        data = pd.DataFrame(data=None)

        for i in range(len(board_data)):
            board_name = board_data[i].find(class_='text').text
            board_code = str(board_data[i].find('a')['href']).strip()[-6:]
            data.loc[i, 'board_name'] = board_name
            data.loc[i, 'board_code'] = board_code

        driver.close()
        data['stock_name'] = None
        data['stock_code'] = None
        return data

    @classmethod
    def industry_ind_stock(cls, name, code, num=300):  # 下载板块成份股
        url = my_url('industry_ind_stock').format(num, code)
        headers = my_headers('industry_ind_stock')
        source = page_source(url=url, headers=headers)

        dl = None
        if source:
            p1 = re.compile(r'[(](.*?)[)]', re.S)
            page_data = re.findall(p1, source)
            json_data = json.loads(page_data[0])['data']['diff']

            values_list = []
            for i in range(len(json_data)):
                values = list(json_data[i].values())
                values_list.append(values)

            key_list = list(json_data[0])
            dl = pd.DataFrame(data=values_list, columns=key_list)

            rename_ = {'f3': '涨跌幅', 'f4': '涨跌额', 'f5': '成交量', 'f6': '成交额',
                       'f7': '振幅', 'f8': '换手率', 'f9': '市盈率动', 'f10': '量比',
                       'f12': 'stock_code', 'f14': 'stock_name', 'f15': 'close',
                       'f16': 'low', 'f17': 'open', 'f18': 'preclose', 'f20': '总市值',
                       'f21': '流通市值', 'f23': '市净率', 'f115': '市盈率'}

            dl = dl.rename(columns=rename_)

            dl = dl.drop(columns=['f1', 'f2', 'f11', 'f13', 'f22', 'f24', 'f25', 'f45',
                                  'f62', 'f128', 'f140', 'f141', 'f136', 'f152'])

            dl['board_name'] = name
            dl['board_code'] = code
            dl['date'] = pd.Timestamp('today').date()

            dl = dl[['board_name', 'board_code', 'stock_code', 'stock_name', 'date']]

        return dl

    @classmethod
    def funds_awkward(cls, code):
        url = my_url('funds_awkward').format(code)
        headers = my_headers('funds_awkward')
        source = page_source(url=url, headers=headers)
        source = soup(source, 'lxml')
        source = source.find("tbody")
        stocks = source.find_all("tr")
        li_name = []
        li_code = []
        for i in stocks:
            name = i.find(class_="tol").text.replace(' ', '')
            code = i.find_all('td')[1].text.replace(' ', '')
            li_name.append(name)
            li_code.append(code)
        dic = {'stock_name': li_name, 'stock_code': li_code}
        data = pd.DataFrame(dic)
        return data

    @classmethod
    def funds_awkward_by_driver(cls, code):

        try:
            url = f'http://fund.eastmoney.com/{code}.html'
            driver = WebDriver()
            driver.get(url)
            source = driver.page_source
            source = soup(source, 'html.parser')
            source = source.find_all('li', class_='position_shares')[0].find_all('td', class_='alignLeft')
            driver.close()

            li = []
            for i in source:
                name = i.text.replace(' ', '')
                li.append(name)

            dic = {'stock_name': li}
            data = pd.DataFrame(dic)

        except ValueError:
            return pd.DataFrame()

        return data


if __name__ == '__main__':
    download = DownloadData.stock_1m_1day('000001')
    print(download)
