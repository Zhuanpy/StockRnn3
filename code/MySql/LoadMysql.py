# -*- coding: utf-8 -*-
import pandas as pd
from DB_MySql import MysqlAlchemy as Alc
from DB_MySql import execute_sql

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


class LoadNortFunds:
    db_funds = 'northfunds'
    tb_amount = 'amount'
    tb_toboard = 'toboard'
    tb_tostock = 'tostock'

    @classmethod
    def load_funds2board(cls):
        df = Alc.pd_read(cls.db_funds, cls.tb_toboard)
        df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE'])
        return df

    @classmethod
    def load_amount(cls):
        df = Alc.pd_read(cls.db_funds, cls.tb_amount)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df

    @classmethod
    def load_funds2stock(cls):
        df = Alc.pd_read(cls.db_funds, cls.tb_tostock)
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        return df

    @classmethod
    def append_funds2board(cls, data):
        Alc.pd_append(data, cls.db_funds, cls.tb_toboard)

    @classmethod
    def append_amount(cls, data):
        Alc.pd_append(data, cls.db_funds, cls.tb_amount)

    @classmethod
    def append_funds2stock(cls, data):
        Alc.pd_append(data, cls.db_funds, cls.tb_tostock)

    @classmethod
    def replace_funds2board(cls, data):
        Alc.pd_replace(data, cls.db_funds, cls.tb_toboard)


class LoadRnnModel:

    db_rnn = 'rnn_model'

    tb_train_record = 'trainrecord'
    tb_run_record = 'runrecord'

    @classmethod
    def load_train_record(cls):
        data = Alc.pd_read(cls.db_rnn, cls.tb_train_record)
        return data

    @classmethod
    def load_run_record(cls):
        data = Alc.pd_read(cls.db_rnn, cls.tb_run_record)
        return data

    @classmethod
    def set_table_train_record(cls, sql: str, params: tuple):
        sql = f'UPDATE {cls.db_rnn}.{cls.tb_train_record} SET {sql}'
        execute_sql(cls.db_rnn, sql, params)

    @classmethod
    def set_table_run_record(cls, sql: str, params: tuple):
        sql = f'UPDATE {cls.db_rnn}.{cls.tb_run_record} SET {sql}'
        execute_sql(cls.db_rnn, sql, params)


class LoadFundsAwkward:
    db_funds_awkward = 'funds_awkward_stock'

    tb_funds_500 = 'topfunds500'
    tb_awkwardNormalization = 'awkward_normalization'
    tb_fundsAwkward = 'fundsawkward'

    @classmethod
    def load_awkwardNormalization(cls):
        df = Alc.pd_read(cls.db_funds_awkward, cls.tb_awkwardNormalization)
        df['Date'] = pd.to_datetime(df['Date'])
        return df

    @classmethod
    def append_awkwardNormalization(cls, data):
        Alc.pd_append(data, cls.db_funds_awkward, cls.tb_awkwardNormalization)

    @classmethod
    def load_fundsAwkward(cls):
        df = Alc.pd_read(cls.db_funds_awkward, cls.tb_fundsAwkward)
        df['Date'] = pd.to_datetime(df['Date'])
        return df

    @classmethod
    def append_fundsAwkward(cls, data):
        Alc.pd_append(data, cls.db_funds_awkward, cls.tb_fundsAwkward)

    @classmethod
    def set_tabel_fundsAwkwardl(cls, sql, params: tuple):
        sql = f'UPDATE {cls.db_funds_awkward}.{cls.tb_fundsAwkward} SET {sql}'
        execute_sql(cls.db_funds_awkward, sql, params)


class LoadBasicInform:
    db_basic = 'stock_basic_information'

    tb_minute = 'record_stock_minute'
    tb_record_north_funds = 'recordnorthfunds'

    @classmethod
    def load_minute(cls):
        data = Alc.pd_read(cls.db_basic, cls.tb_minute)
        return data

    @classmethod
    def load_record_north_funds(cls):
        data = Alc.pd_read(cls.db_basic, cls.tb_record_north_funds)
        return data

    @classmethod
    def append_record_north_funds(cls, data):
        Alc.pd_append(data, cls.db_basic, cls.tb_record_north_funds)

    @classmethod
    def set_table_record_north_funds(cls, sql, params: tuple):
        sql = f'UPDATE {cls.db_basic}.{cls.tb_record_north_funds} SET {sql}'
        execute_sql(cls.db_basic, sql, params)

    @classmethod
    def set_table_minute_record(cls, sql, params: tuple):
        sql = f'UPDATE {cls.db_basic}.{cls.tb_minute} SET {sql}'
        execute_sql(cls.db_basic, sql, params)


class LoadBasic:
    db = 'stockbasic'

    tb_basic = 'basic'

    @classmethod
    def load_basic(cls):
        df = Alc.pd_read(cls.db, cls.tb_basic)
        return df


class RecordStock:
    db = 'stockrecord'

    table_record_download_1m_data = 'recorddownload1mdata'
    table_record_download_top500 = 'record_download_top500fundspositionstock'

    @classmethod
    def load_record_download_1m_data(cls):
        df = Alc.pd_read(cls.db, cls.table_record_download_1m_data)
        return df

    @classmethod
    def set_table_record_download_1m_data(cls, sql: str, params: tuple):
        sql = f'UPDATE {cls.db}.{cls.table_record_download_1m_data} SET {sql}'
        execute_sql(cls.db, sql, params)

    @classmethod
    def load_record_download_top500fundspositionstock(cls):
        df = Alc.pd_read(cls.db, cls.table_record_download_top500)
        return df

    @classmethod
    def set_table_record_download_top500fundspositionstock(cls, sql: str, params: tuple):
        sql = f'UPDATE {cls.db}.{cls.table_record_download_top500} SET {sql}'
        execute_sql(cls.db, sql, params)


if __name__ == '__main__':
    data_ = LoadBasicInform.load_record_north_funds()
    print(data_)
