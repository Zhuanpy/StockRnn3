
# -*- coding: utf-8 -*-
import pandas as pd
from DB_MySql import MysqlAlchemy as Alc


class StockData1m:
    """
    _year: data start year ;
    year_: data end year;
    """

    @classmethod
    def load_1m(cls, code_: str, _year):

        y = int(pd.Timestamp('today').year)

        if len(_year) == 4:
            _year = f'{_year}-01-01'

        _year = int(pd.to_datetime(_year).year)

        df = pd.DataFrame()

        for i in range(y - _year + 1):
            db = f'data1m{_year + i}'
            tb = code_.lower()
            data = Alc.pd_read(db, tb)
            df = pd.concat([df, data], ignore_index=True)

        return df

    @classmethod
    def append_1m(cls, code_: str, year_: str, data):
        db = f'data1m{year_}'
        tb = code_.lower()
        Alc.pd_append(data, db, tb)

    @classmethod
    def replace_1m(cls, code_: str, year_: str, data):
        db = f'data1m{year_}'
        tb = code_.lower()
        Alc.pd_replace(data, db, tb)
