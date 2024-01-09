import time
from DlEastMoney import DownloadData as dle
import pandas as pd
from code.MySql.LoadMysql import StockData1m, LoadBasicInform, LoadNortFunds
from code.Savedata.save_download import save_1m_to_csv
import datetime
import logging

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
            data = dle.stock_1m_days(code, days=days)

        elif stock_type == StockType.BOARD_1M:
            data = dle.board_1m_multiple(code, days=days)

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
    def download_1mData(cls):

        """
        download 1m data ;
        every day running method;
        """
        # todo 判断公共假期，周六补充下载数据
        today = datetime.date.today()

        shapes = 1
        current = pd.to_datetime(today)  # .date()

        while shapes:

            record = LoadBasicInform.load_minute()  # alc.pd_read(database=db_basic, table=tb_basic)

            record['StartDate'] = pd.to_datetime(record['StartDate'])
            record['EndDate'] = pd.to_datetime(record['EndDate'])
            record['RecordDate'] = pd.to_datetime(record['RecordDate'])

            dl1 = record[(record['Classification'] == '行业板块') &
                         (record['EndDate'] < current)]

            dl2 = record[(record['Classification'] != '行业板块') &
                         (record['StartDate'] < pd.to_datetime('2020-01-01')) &
                         (record['EndDate'] < current)]

            dl = pd.concat([dl1, dl2], ignore_index=True).sort_values(by=['EndDate']).reset_index(drop=True)

            if dl.empty:
                logging.info('已是最新数据')
                break

            shapes = dl.shape[0]

            for (i, row) in dl.iterrows():
                print(f'\n下载进度：\n总股票数: {shapes}个; 剩余股票: {(shapes - i)}个;')
                id_ = row['id']
                stock_name = row['name']
                stock_code = row['code']

                escode = row['EsCode']
                classification = row['Classification']

                record_ending = row['EndDate']
                days = (current - record_ending).days  # 距当前的天数， 判断下载几天的数据

                if days <= 0:
                    logging.info(f'无最新1m数据: {stock_name}, {stock_code};')
                    continue

                days = min(5, days)

                stock_type = StockType.BOARD_1M if classification == '行业板块' else StockType.STOCK_1M  # 判断是行业板块还是个股
                data, ending = download_1m_by_type(escode, days, stock_type)

                if data.empty:  # 判断下载数据是否为空
                    logging.warning(f'无最新1m数据: {stock_name}, {stock_code};')
                    continue

                select = pd.to_datetime(record_ending + pd.Timedelta(days=1))
                data = data[data['date'] > select]  # 筛选出重复数据；

                # 判断是否保存数据 及 更新记录表格
                if data.empty:
                    logging.info(f'无最新1m数据: {stock_name}, {stock_code};')
                    continue

                ending = pd.to_datetime(ending)

                if ending > record_ending:

                    try:
                        # 保存 1m数据;
                        year_ = ending.year
                        StockData1m.append_1m(code_=stock_code, year_=str(year_), data=data)

                        sql = f'''update {LoadBasicInform.db_basic}.{LoadBasicInform.tb_minute} 
                        set EndDate='{ending}', RecordDate = '{current}', 
                        EsDownload = 'success' where id={id_}; '''
                        LoadBasicInform.basic_execute_sql(sql)

                        save_1m_to_csv(data, stock_code)  # 将下载的1分钟数据，同时保存至 data 1m 文件夹中

                    except Exception as ex:
                        sql = f'''update {LoadBasicInform.db_basic}.{LoadBasicInform.tb_minute} 
                        set RecordDate = '{current}', EsDownload = 'failed' where id={id_}; '''
                        LoadBasicInform.basic_execute_sql(sql)
                        print(f'股票：{stock_name}, {stock_code}存储数据异常: {ex}')
                        # todo 加载日志

                if ending == record_ending:
                    # data record date equal download end date ,just renew record date
                    sql = f'''update {LoadBasicInform.db_basic}.{LoadBasicInform.tb_minute} set 
                    EndDate = '{ending}', RecordDate = '{current}' where id = {id_}; '''
                    LoadBasicInform.basic_execute_sql(sql)

                    print(f'{LoadBasicInform.tb_minute} 数据更新成功: {stock_name}, {stock_code}')

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
        print(record)

        for index in record.index:

            table = record.loc[index, 'name']
            id_ = record.loc[index, 'id']

            _ending = record.loc[index, 'ending_date']
            _current = record.loc[index, 'renew_date']

            ending = None

            if current <= _current:
                print(f'无新数据:{table}')
                continue

            try:

                if table == tables[0]:  # 北向资金流入个股数据；

                    data = dle.funds_to_stock()  # 下载数据

                    if not data.shape[0]:
                        break

                    ending = data.iloc[-1]['trade_date']
                    LoadNortFunds.append_funds2stock(data)

                if table == tables[1]:  # 北向资金日常数据

                    data = dle.funds_daily_data()  # 下载数据

                    if not data.shape[0]:
                        break

                    ending = data.iloc[-1]['trade_date']
                    LoadNortFunds.append_amount(data)

                if table == tables[2]:  # 北向资金流入板块数据
                    days = current - _ending
                    days = days.days
                    print(days)

                    data = pd.DataFrame()

                    for i in range(int(days)):
                        i = i + 1
                        date_ = _ending + pd.Timedelta(days=i)
                        date_ = date_.strftime('%Y-%m-%d')
                        dl = dle.funds_to_sectors(date_)  # 下载无最新数据时

                        if not dl.shape[0]:
                            continue

                        data = pd.concat([data, dl], ignore_index=True)

                    # 判断是否有下载数据，无下载数据跳出循环，有下载数据继续更新
                    if not data.shape[0]:
                        break

                    ending = data.iloc[-1]['TRADE_DATE']
                    LoadNortFunds.append_funds2board(data)

                # 更新 保存 record 数据
                if not ending or ending <= _ending:
                    print(f'{table}无最新数据;')
                    continue

                sql = f'''update {LoadBasicInform.db_basic}.{LoadBasicInform.tb_record_north_funds} set 
                ending_date = '{ending}', renew_date='{current}' where id={id_}; '''
                LoadBasicInform.basic_execute_sql(sql=sql)
                print(f'{table}数据更新成功;')

            except Exception as ex:
                print(f'{table} 数据更新异常:\n{ex}')


class RMDownloadData(DataDailyRenew):
    """
    daily running
    """

    def __init__(self):
        super().__init__()
        # DataDailyRenew.__init__(self)

    def daily_renew_data(self):

        current_time = pd.Timestamp('today')
        market_open = pd.to_datetime('09:30')
        market_close = pd.to_datetime('15:30')

        if current_time < market_open:
            self.renew_NorthFunds()  # 北向资金信息

        elif current_time > market_close:
            self.download_1mData()  # 更新股票当天1m信息；
            self.renew_NorthFunds()  # 北向资金信息


if __name__ == '__main__':
    rn = DataDailyRenew()
    # rn.download_1mData()
    rn.download_1mData()
