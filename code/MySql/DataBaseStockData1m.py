# -*- coding: utf-8 -*-
import pandas as pd
from DB_MySql import MysqlAlchemy as Alc


class StockData1m:
    """
    _year: data start year ;
    year_: data end year;
    """

    @classmethod
    def load_1m(cls, code_: str, start_year: str, end_year=None) -> pd.DataFrame:
        """
         Parameters:
             code_: stock code;
             start_year: data start year; 要求导入数据的开始年； 可以是 四位数年份， 或者带年份的日期；
             end_year : data end year; 要求导入数据的结束年份；2020, 2020/01/01

         Returns:
        """
        if end_year:
            if len(end_year) == 4:
                end_year = f'{end_year}-01-01'

            end_year = pd.to_datetime(end_year).year

        else:
            end_year = pd.Timestamp('today').year

        end_year = int(end_year)

        if len(start_year) == 4:
            start_year = f'{start_year}-01-01'

        start_year = int(pd.to_datetime(start_year).year)

        df = pd.DataFrame()

        # Loop through each year in the range and concatenate data
        for year in range(start_year, end_year + 1):
            db = f'data1m{year}'
            tb = code_.lower()
            data = Alc.pd_read(db, tb)
            df = pd.concat([df, data], ignore_index=True)

        return df

    @classmethod
    def append_1m(cls, code_: str, year_: str, data: pd.DataFrame):
        """
        将数据追加到特定股票代码和年份的数据库中。

        参数:
            code_: 股票代码;
            year_: 数据要追加的年份;
            data: 包含要追加数据的 DataFrame
        """

        db = f'data1m{year_}'
        tb = code_.lower()
        Alc.pd_append(data, db, tb)

    @classmethod
    def replace_1m(cls, code_: str, year_: str, data: pd.DataFrame):
        db = f'data1m{year_}'
        tb = code_.lower()
        Alc.pd_replace(data, db, tb)
