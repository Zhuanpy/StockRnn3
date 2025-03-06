from DB_MySql import MysqlAlchemy as Alc
from DB_MySql import execute_sql


class StockData15m:

    db_15m = 'stock_15m_data'

    @classmethod
    def load_15m(cls, stock_code: str):
        df = Alc.pd_read(cls.db_15m, stock_code)
        return df

    @classmethod
    def append_15m(cls, stock_code: str, data):
        Alc.pd_append(data, cls.db_15m, stock_code)

    @classmethod
    def replace_15m(cls, stock_code: str, data):
        Alc.pd_replace(data, cls.db_15m, stock_code)

    @classmethod
    def set_data_15m_data(cls, stock_code: str, sql: str, params: tuple):
        sql = f'UPDATE {cls.db_15m}.{stock_code} SET {sql}'
        execute_sql(cls.db_15m, sql, params)

    @classmethod
    def delete_data_from_15m_data(cls, stock_code: str, sql: str, params: tuple):
        sql = f'delete from {cls.db_15m}.{stock_code} {sql};'
        execute_sql(cls.db_15m, sql, params)

    @classmethod
    def get_data_15m_data_end_date(cls, stock_code: str):
        # SELECT MAX(C) FROM A.B; sql1 = f'''select * from {cls.db_15m}.`{stock_code}` where date in (select max(
        # date) from {cls.db_15m}.`{stock_code}`);'''
        sql1 = f'SELECT MAX(date) FROM {cls.db_15m}.`{stock_code}`;'
        parser = ()
        r = execute_sql(cls.db_15m, sql1, parser)
        r = r[0][0]
        return r