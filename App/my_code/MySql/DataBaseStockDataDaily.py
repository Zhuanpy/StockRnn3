from DB_MySql import MysqlAlchemy as Alc
from DB_MySql import execute_sql


class StockDataDaily:

    db = 'datadaily'

    @classmethod
    def load_daily_data(cls, stock_code: str):
        df = Alc.pd_read(cls.db, stock_code)
        return df

    @classmethod
    def append_daily_data(cls, stock_code: str, data):
        Alc.pd_append(data, cls.db, stock_code)

    @classmethod
    def replace_daily_data(cls, stock_code: str, data):
        Alc.pd_replace(data, cls.db, stock_code)

    @classmethod
    def set_data_daily_data(cls, stock_code: str, sql: str, params: tuple):
        sql = f'UPDATE {cls.db}.{stock_code} SET {sql}'
        execute_sql(cls.db, sql, params)

    @classmethod
    def delete_data_from_daily_data(cls, stock_code: str, sql: str, params: tuple):
        sql = f'delete from {cls.db}.{stock_code} {sql};'
        execute_sql(cls.db, sql, params)

    @classmethod
    def get_data_daily_data_end_date(cls, stock_code: str):
        sql1 = f'SELECT MAX(date) FROM {cls.db}.`{stock_code}`;'
        parser = ()
        r = execute_sql(cls.db, sql1, parser)
        r = r[0][0]
        return r