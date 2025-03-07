# -*- coding: utf-8 -*-
from DlJuQuan import DownloadData as Download_juquan
from DlEastMoney import DownloadData as Download_east
from App.code.MySql.LoadMysql import LoadFundsAwkward, LoadBasicInform, LoadNortFunds
from App.code.MySql.DataBaseStockData1m import StockData1m
import pandas as pd
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 5000)


def download_1m(stock, code, days):

    try:
        df = Download_east.stock_1m_days(code, days=days)

    except Exception as ex:
        # todo 引入日志
        print(f'东方财富下载{stock}1m数据异常：{ex};')
        df = pd.DataFrame()

    return df


def collect_all_1m_data():  # 补充 完整的 1m_data 数据库;

    """
    通过 聚宽 下载 1m 数据
    """
    awkward = LoadFundsAwkward.load_fundsAwkward()
    awkward = awkward.groupby('stock_name').count().sort_values(by=['funds_name']).reset_index().tail(300)
    awkward = list(awkward['stock_name'])

    # 确定哪些股票需下载；
    basic = LoadBasicInform.load_minute()
    basic = basic[(basic['name'].isin(awkward)) &
                  (basic['StartDate'] > pd.to_datetime('2018-06-01')) &
                  (basic['EndDate'] < pd.Timestamp('today')) &
                  (~basic['Classification'].isin(['科创板', '创业板']))].reset_index(drop=True)

    print(basic)
    over_ = ''
    over = '您的1000万条体验期已结束'

    if basic.empty:
        print('无历史分时数据需下载;')

    if not basic.empty:

        years = [2018 + i for i in range(pd.Timestamp('today').year - 2018 + 1)]
        years = sorted(years, reverse=True)  # [2022, 2021, 2020, 2019, 2018]

        for year_ in years:

            for row in basic.iterrows():

                if over_ == over:
                    print(over_)
                    break

                name = row['name']
                code = row['code']
                id_ = row['id']
                record_start = row['StartDate']

                record_year = pd.to_datetime(record_start).year

                if year_ > record_year:  # example: record_year: 2021 , year_: 2022 or 2021 or 2020
                    continue

                end_ = (pd.to_datetime(record_start) + pd.Timedelta(days=-1)).date()
                start_ = pd.to_datetime(f'{year_}-01-01').date()

                print(f'下载： {name}, {code},时间段 {start_} 至 {end_}；')

                if start_ > end_:
                    continue

                try:
                    data1m = Download_juquan.download_history_data(code, frequency='1m', fq_value='不复权',
                                                                   start_date=str(start_), end_date=str(end_))

                    if not data1m.shape[0]:
                        continue

                    start_new = data1m.iloc[0]['date'].date()

                    try:  # 保存数据
                        _data = StockData1m.load_1m(code, start_year=str(year_))
                        data1m = pd.concat([data1m, _data], ignore_index=True)

                        data1m = data1m.drop_duplicates(subset=['date']).sort_values(by=['date']).reset_index(drop=True)

                        StockData1m.replace_1m(code_=code, year_=str(year_), data=data1m)

                    except pd.errors.DatabaseError:
                        StockData1m.replace_1m(code_=code, year_=str(year_), data=data1m)

                    # 更新参数
                    sql = f''' StartDate = '%s.' where id = %s.;'''
                    params = (start_new, id_)
                    LoadBasicInform.set_table_minute_record(sql=sql, params=params)

                    print(f'下载成功: {name}, {code} 1m 数据;')
                    time.sleep(10)

                except Exception as ex:

                    print(f'下载 {stock_name}, {stock_code} 1m数据异常;\n{ex}')

                    if str(ex) == 'Cannot convert non-finite values (NA or inf) to integer':  # 数据下载错误时

                        sql = f''' StartDate = '1990-01-01', EndDate = '2050-01-01', 
                        RecordDate = '2050-01-01' where id = %s;'''
                        params = (id_,)
                        LoadBasicInform.set_table_minute_record(sql=sql, params=params)

                    over_ = str(ex).split('，')[0]


def collect_all_funds_to_sectors():

    """
    北向基金流入板块数据
    :return:
    """

    funds_board = LoadNortFunds()
    data = funds_board.load_funds2board()
    data = data.sort_values(by=['TRADE_DATE'])
    data['TRADE_DATE'] = data['TRADE_DATE'].dt.date
    last_date = data.iloc[-1]['TRADE_DATE']

    board = StockData1m.load_1m(code_='BK0475', start_year='2022')
    board['date'] = board['date'].dt.date
    board = board.drop_duplicates(subset=['date'])
    board = board[board['date'] > last_date]
    board = list(board['date'])

    for d in board:
        d = d.strftime('%Y-%m-%d')
        dl = Download_east.funds_to_sectors(d)  # 下载数据

        if dl.empty:
            continue

        LoadNortFunds.append_funds2board(dl)
        time.sleep(5)


if __name__ == '__main__':
    collect_all_funds_to_sectors()
    stock_name = ''
    stock_code = ''
