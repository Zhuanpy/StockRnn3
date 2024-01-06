import pandas as pd
import numpy as np
from code.MySql.LoadMysql import StockData15m


def transfer_data(stock_list: list):

    """
    将 CSV 数据，整理进 MYSQL 中
    stock_list = ['600309', '002475']

    """
    month_list = ['2021-11', '2021-12', '2022-01']

    for stock_code in stock_list:

        try:
            path1 = month_list[0]
            data1 = pd.read_csv(f'data/{path1}/15m/{stock_code}.csv')
            end1 = data1.iloc[-1]['date']

        except FileNotFoundError:
            data1 = pd.DataFrame()
            end1 = None

        try:
            path2 = month_list[1]
            data2 = pd.read_csv(f'data/{path2}/15m/{stock_code}.csv')
            end2 = data2.iloc[-1]['date']

        except FileNotFoundError:
            data2 = pd.DataFrame()
            end2 = None

        try:
            path3 = month_list[2]
            data3 = pd.read_csv(f'data/{path3}/15m/{stock_code}.csv')

        except FileNotFoundError:
            data3 = pd.DataFrame()

        if len(data1):
            data2 = data2[data2['date'] > end1]

        if len(data2):
            data3 = data3[data3['date'] > end2]

        data = pd.concat([data1, data2, data3], ignore_index=True)

        data = data.replace([np.inf, -np.inf], np.nan)

        StockData15m.replace_15m(stock_code, data)

        return data
