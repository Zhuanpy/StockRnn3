import time
from DlEastMoney import DownloadData as My_dle
import pandas as pd
from code.MySql.LoadMysql import LoadBasicInform, LoadNortFunds, RecordStock
from code.RnnDataFile.save_download import save_1m_to_csv, save_1m_to_daily, save_1m_to_mysql
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
            record = record[(record['EndDate'] < current)]

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

                    save_1m_to_daily(data, stock_code)  # 将下载的1分钟数据，同时保存至 daily sql table

                    # 更新参数
                    sql = f'''EndDate='%s', RecordDate = '%s', EsDownload = 'success' where id= %s; '''
                    params = (RecordStock.db, RecordStock.table_record_download_1m_data, ending, current, id_)
                    RecordStock.set_table_record_download_1m_data(sql, params)

                if ending == record_ending:
                    sql = f''' EndDate = '%s', RecordDate = '%s' where id = %s; '''
                    params = (RecordStock.db, RecordStock.table_record_download_1m_data, ending, current, id_)
                    RecordStock.set_table_record_download_1m_data(sql, params)

                    logging.info(f'{RecordStock.table_record_download_1m_data} 数据更新成功: {stock_name}, {stock_code}')

                time.sleep(2)

    @classmethod
    def renew_NorthFunds(cls):
        """
        更新北向资金数据
        renew North funds data;
        """

        current = pd.Timestamp('today').date()
        tables = ['tostock', 'amount', 'toboard']

        record = LoadBasicInform.load_record_north_funds()

        for index in record.index:

            table = record.loc[index, 'name']
            id_ = record.loc[index, 'id']

            _ending = record.loc[index, 'ending_date']
            _current = record.loc[index, 'renew_date']

            ending = None

            if current <= _current:
                logging.info(f'{table}无最新数据;')
                continue

            try:

                if table == tables[0]:  # 北向资金流入个股数据；

                    data = My_dle.funds_to_stock()  # 下载数据

                    if not data.shape[0]:
                        break

                    ending = data.iloc[-1]['trade_date']
                    LoadNortFunds.append_funds2stock(data)

                if table == tables[1]:  # 北向资金日常数据

                    data = My_dle.funds_daily_data()  # 下载数据

                    if not data.shape[0]:
                        break

                    ending = data.iloc[-1]['trade_date']
                    LoadNortFunds.append_amount(data)

                if table == tables[2]:  # 北向资金流入板块数据
                    days = current - _ending
                    days = days.days

                    data = pd.DataFrame()

                    for i in range(int(days)):
                        i = i + 1
                        date_ = _ending + pd.Timedelta(days=i)
                        date_ = date_.strftime('%Y-%m-%d')
                        dl = My_dle.funds_to_sectors(date_)  # 下载无最新数据时

                        if dl.empty:
                            continue

                        data = pd.concat([data, dl], ignore_index=True)

                    # 判断是否有下载数据，无下载数据跳出循环，有下载数据继续更新
                    if data.empty:
                        break

                    ending = data.iloc[-1]['TRADE_DATE']
                    LoadNortFunds.append_funds2board(data)

                # 更新 保存 record 数据
                if not ending or ending <= _ending:
                    logging.info(f'{table}无最新数据;')
                    continue

                sql = f''' ending_date = '%s', renew_date='%s' where id=%s; '''
                params = (ending, current, id_)
                LoadBasicInform.set_table_record_north_funds(sql=sql, params=params)

                logging.info(f'{table}数据更新成功;')

            except Exception as ex:
                logging.info(f'{table} 数据更新异常:\n{ex}')


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

        if current_time < market_open:
            self.renew_NorthFunds()  # 北向资金信息

        elif current_time > market_close:
            self.download_1m_data()  # 更新股票当天1m信息；

            self.renew_NorthFunds()  # 北向资金信息


if __name__ == '__main__':
    rn = DataDailyRenew()
    # rn.download_1mData()
    rn.download_1m_data()
