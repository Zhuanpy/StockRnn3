import pandas as pd
from DB_MySql import MysqlAlchemy as Alc
from DB_MySql import execute_sql

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


class TableStockPool:
    db_pool = 'stockpool'
    tb_pool = 'stockpool'

    @classmethod
    def load_StockPool(cls):
        df = Alc.pd_read(cls.db_pool, cls.tb_pool)
        df['RecordDate'] = pd.to_datetime(df['RecordDate'])
        return df

    @classmethod
    def set_table_to_pool(cls, sql, params: tuple):
        sql = f'UPDATE {cls.db_pool}.{cls.tb_pool} SET {sql}'
        execute_sql(cls.db_pool, sql, params)

    @classmethod
    def replace_stock_pool(cls, data):
        Alc.pd_replace(data=data, database=cls.db_pool, table=cls.tb_pool)


class TableStockPoolCount:
    db_pool = 'stockpool'
    tb_poolCount = 'poolcount'

    @classmethod
    def load_poolCount(cls):
        df = Alc.pd_read(cls.db_pool, cls.tb_poolCount)
        df['date'] = pd.to_datetime(df['date'])
        return df

    @classmethod
    def append_poolCount(cls, data):
        Alc.pd_append(data, cls.db_pool, cls.tb_poolCount)

    @classmethod
    def set_table_poolCount(cls, sql, params: tuple):
        sql = f'UPDATE {cls.db_pool}.{cls.tb_poolCount} SET {sql}'
        execute_sql(cls.db_pool, sql, params)


class TableTradeRecord:
    db_pool = 'stockpool'
    tb_trade_record = 'traderecord'

    @classmethod
    def set_table_trade_record(cls, sql, params: tuple):
        sql = f'UPDATE {cls.db_pool}.{cls.tb_trade_record} SET {sql}'
        execute_sql(cls.db_pool, sql, params)

    @classmethod
    def load_tradeRecord(cls):
        df = Alc.pd_read(cls.db_pool, cls.tb_trade_record)
        return df

    @classmethod
    def append_tradeRecord(cls, data):
        Alc.pd_append(data, cls.db_pool, cls.tb_trade_record)


class TableStockBoard:

    db_pool = 'stockpool'
    tb_board = 'board'

    @classmethod
    def load_board(cls):
        df = Alc.pd_read(cls.db_pool, cls.tb_board)
        df['RecordDate'] = pd.to_datetime(df['RecordDate'])
        return df

    @classmethod
    def set_table_to_board(cls, sql, params: tuple):
        sql = f'UPDATE {cls.db_pool}.{cls.tb_board} SET {sql}'
        execute_sql(cls.db_pool, sql, params)

    @classmethod
    def replace_board(cls, data):
        Alc.pd_replace(data=data, database=cls.db_pool, table=cls.tb_board)
