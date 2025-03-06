import time
from DlEastMoney import DownloadData as My_dle
import pandas as pd
from App.my_code.MySql.LoadMysql import LoadBasicInform, LoadNortFunds, RecordStock
from App.my_code.RnnDataFile.save_download import save_1m_to_csv, save_1m_to_daily, save_1m_to_mysql
import datetime
import logging

logging.basicConfig(level=logging.INFO)  # 设置 logging 提醒级别

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 5000)


class StockType:
    STOCK_1M = 'stock_1m'
    BOARD_1M = 'board_1m'


def download_1m_by_type(code: str, days: int, stock_type: str):
    """
    download stock data 1m data , return download data & data end date ;
    Download stock 1m data from Eastmoney.

    Parameters:
    - code (str): Stock code.
    - days (int): Number of days to retrieve, 小于5天.
    - stock_type (str): Type of data to download, should be 'stock_1m' or 'board_1m'.

    Returns:
    - data (pd.DataFrame): Downloaded stock data.
    - date_end (datetime.date or None): End date of the downloaded data, None if an error occurs.
    """

    try:
        if stock_type == StockType.STOCK_1M:
            data = My_dle.stock_1m_days(code, days=days)

        elif stock_type == StockType.BOARD_1M:
            data = My_dle.board_1m_multiple(code, days=days)

        else:
            raise ValueError(f"Invalid stock_type: {stock_type}")

        if data.empty:
            return data, None

        date_end = data.iloc[-1]['date'].date()

        return data, date_end

    except Exception as ex:
        logging.error(f"Error in download_1m_by_type for {code} ({stock_type}): {ex}")
        return pd.DataFrame(), None


class DataDailyRenew:
    """
    每日数据更新

    """

    @classmethod
    def download_1m_data(cls):
        """
        download 1m data ;
        every day running method;
        """
        # todo 判断公共假期，周六补充下载数据
        today = datetime.date.today()
        current = pd.Timestamp(today)  # 2024-01-09 00:00:00

        while True:

            record = RecordStock.load_record_download_1m_data()  # alc.pd_read(database=db_basic, table=tb_basic)

            record['EndDate'] = pd.to_datetime(record['EndDate'])
            record['RecordDate'] = pd.to_datetime(record['RecordDate'])
            record = record[(record['EndDate'] < current)].reset_index(drop=True)

            if record.empty:
                logging.info('已是最新数据')
                break

            shapes = record.shape[0]

            for (i, row) in record.iterrows():
                logging.info(f'\n下载进度：\n总股票数: {shapes}个; 剩余股票: {(shapes - i)}个;')

                id_, stock_name, stock_code, escode, classification, record_ending = (
                    row['id'], row['name'], row['code'], row['EsCode'], row['Classification'], row['EndDate'])

                days = (current - record_ending).days  # 距当前的天数， 判断下载几天的数据

                if days <= 0:
                    logging.info(f'无最新1m数据: {stock_name}, {stock_code};')
                    continue

                days = min(5, days)

                stock_type = StockType.BOARD_1M if classification == '行业板块' else StockType.STOCK_1M  # 判断是行业板块还是个股
                data, ending = download_1m_by_type(escode, days, stock_type)

                if data.empty:  # 判断下载数据是否为空
                    logging.info(f'无最新1m数据: {stock_name}, {stock_code};')
                    continue

                select = pd.to_datetime(record_ending + pd.Timedelta(days=1))
                data = data[data['date'] > select]  # 筛选出重复数据；

                # 判断是否保存数据 及 更新记录表格
                if data.empty:
                    logging.info(f'无最新1m数据: {stock_name}, {stock_code};')
                    continue

                ending = pd.to_datetime(ending)

                if ending > record_ending:
                    year_ = str(ending.year)

                    save_1m_to_mysql(stock_code, year_, data)  # 将下载的1分钟数据，保存至 sql 数据库

                    save_1m_to_csv(data, stock_code)  # 将下载的1分钟数据，同时保存至 data 1m 文件夹中

                    if classification != '行业板块':
                        save_1m_to_daily(data, stock_code)  # 将下载的1分钟数据，同时保存至 daily sql table

                    # 更新参数
                    sql = f'''EndDate= %s, RecordDate = %s, EsDownload = 'success' where id= '%s'; '''
                    params = (ending, current, id_)
                    RecordStock.set_table_record_download_1m_data(sql, params)

                if ending == record_ending:
                    sql = f''' EndDate = %s, RecordDate = %s where id = '%s'; '''
                    params = (ending, current, id_)
                    RecordStock.set_table_record_download_1m_data(sql, params)

                    info_text = f'{RecordStock.table_record_download_1m_data} 数据更新成功: {stock_name}, {stock_code}'
                    logging.info(info_text)

                time.sleep(2)


class RMDownloadData(DataDailyRenew):
    """
    daily running
    """

    def __init__(self):
        super().__init__()

    def daily_renew_data(self):

        current_time = pd.Timestamp('today')
        market_open = pd.to_datetime('09:30')
        market_close = pd.to_datetime('15:30')

        if current_time > market_close:
            self.download_1m_data()  # 更新股票当天1m信息；


def stock_name_data():
    """
    download 1m data ;
    every day running method;
    """
    # todo 判断公共假期，周六补充下载数据
    today = datetime.date.today()
    current = pd.Timestamp(today)  # 2024-01-09 00:00:00

    record = RecordStock.load_record_download_1m_data()  # alc.pd_read(database=db_basic, table=tb_basic)

    record['EndDate'] = pd.to_datetime(record['EndDate'])
    record['RecordDate'] = pd.to_datetime(record['RecordDate'])
    record = record[(record['EndDate'] < current)].reset_index(drop=True)
    record = record[record['Classification'] != '行业板块']
    record = record["code"]
    print(record)
    path = r"C:\Users\User\Desktop\临时文件"
    record.to_csv(f'{path}/stock_name.txt', index=False)
    # 更新股票当天1m信息；


if __name__ == '__main__':
    # rn = DataDailyRenew()
    # rn.download_1mData()
    # rn.download_1m_data()
    stock_name_data()
