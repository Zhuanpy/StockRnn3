# -*- coding: utf-8 -*-
import pandas as pd
from RnnRunModel import PredictionCommon
from code.MySql.LoadMysql import LoadRnnModel
from code.MySql.DataBaseStockPool import TableStockPool
from code.MySql.sql_utils import Stocks
import matplotlib.pyplot as plt
import multiprocessing
from code.Evaluation.CountPool import PoolCount
from Rnn_utils import reset_id_time, reset_record_time, date_range
import logging

# logging.basicConfig(format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s', level=logging.info)
logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

plt.rcParams['font.sans-serif'] = ['FangSong']
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


class StockEvaluator:
    DB_RNN = LoadRnnModel.db_rnn
    TB_TRAIN_RECORD = LoadRnnModel.tb_train_record

    def __init__(self, day, start_index, end_index, data, month, check_model):

        self.day = day
        self.start_index = start_index
        self.end_index = end_index
        self.data = data
        self.month = month
        self.check_model = check_model

    def evaluate_stock(self, index):
        stock_code = self.data.loc[index, 'code']
        record_id = self.data.loc[index, 'id']
        check_date = pd.Timestamp('now').date()

        try:
            run = PredictionCommon(stock=stock_code, month_parsers=self.month, monitor=False, check_date=self.day)
            run.single_stock()

            if self.check_model:
                self.update_model_check_status(record_id, check_date, 'success')

        except Exception as ex:
            logging.error(f'Error: {ex}')

            if self.check_model:
                self.update_model_check_status(record_id, check_date, 'error')

    def update_model_check_status(self, record_id, check_date, status):
        sql = f''' ModelCheckTiming = %s, ModelCheck = %s, ModelError = %s, ModelCheckTiming = '%s' WHERE id = %s; '''
        parser = (pd.Timestamp.now(), status, status, check_date, record_id)
        LoadRnnModel.set_table_train_record(sql, parser)

    def run_evaluation(self):
        count = 0
        for index in range(self.start_index, self.end_index):
            print(f'当前进度，剩余{self.end_index - self.start_index - count}；')
            self.evaluate_stock(index)
            count += 1


def stock_evaluate(day_, _num, num_, data, month_parsers, check_model):
    count = 0

    for index in range(_num, num_):
        stock_ = data.loc[index, 'code']
        id_ = data.loc[index, 'id']
        check_date = pd.Timestamp('now').date()

        print(f'当前进度，剩余{num_ - _num - count}； 当前股票：{stock_}')
        try:

            run = PredictionCommon(stock=stock_, month_parsers=month_parsers, monitor=False, check_date=day_)
            run.single_stock()

            if check_model:
                sql2 = f''' 
                ModelCheckTiming = %s, 
                ModelCheck = 'success', 
                ModelError = 'success', 
                ModelCheckTiming = %s where id = %s; 
                '''

                parser = (pd.Timestamp.now(), check_date, id_)
                LoadRnnModel.set_table_train_record(sql2, parser)

        except Exception as ex:
            logging_test = f'stock code {stock_} Error: {ex}'
            # logging.info(logging_test)
            print(logging_test)
            logging.error("Error occurred: %s", str(ex))

            if check_model:
                sql2 = f'''
                ModelCheck = 'error',
                ModelError = 'error',
                ModelCheckTiming = %s where id = %s;
                '''

                parser = (check_date, id_)
                LoadRnnModel.set_table_train_record(sql2, parser)

        count += 1


def multiprocessing_count_pool(day_, month_parsers='2022-02', check_model=False):

    data = TableStockPool.load_StockPool()
    if not data.empty:
        shape_ = data.shape[0]

        print(f'处理日期{day_}， 处理个数：{shape_}')

        l1 = shape_ // 3
        l2 = shape_ // 3 * 2

        p1 = multiprocessing.Process(target=stock_evaluate, args=(day_, 0, l1, data, month_parsers, check_model,))
        p2 = multiprocessing.Process(target=stock_evaluate, args=(day_, l1, l2, data, month_parsers, check_model,))
        p3 = multiprocessing.Process(target=stock_evaluate, args=(day_, l2, shape_, data, month_parsers, check_model,))

        p1.start()
        p2.start()
        p3.start()

        p1.join()
        p2.join()
        p3.join()


class RMHistoryCheck:

    def __init__(self, _date=None, date_=None, month_parsers='2022-02'):

        self.month_parsers = month_parsers

        if not date_:
            self.date_ = pd.Timestamp.now().date()

        else:
            self.date_ = pd.to_datetime(date_).date()

        if not _date:
            self._date = self.date_

        else:
            self._date = pd.to_datetime(_date).date()

    def check1stock(self, stock, reset_record=False):

        name, code, id_ = Stocks(stock)

        if reset_record:
            reset_id_time(id_, self._date)

        dates = date_range(self._date, self.date_)
        for d_ in dates:
            run = PredictionCommon(stock=name, month_parsers=self.month_parsers, monitor=False, check_date=d_)
            run.single_stock()

    def loop_by_date(self):

        list_day = date_range(self._date, self.date_)
        # print(list_day)
        # exit()
        reset_record_time(list_day[0])

        for day_ in list_day:
            multiprocessing_count_pool(day_, check_model=False)

            my_pool_count = PoolCount()
            my_pool_count.count_trend()
            print(f'日期{day_}完成;')

    def loop_by_check_model(self):
        list_day = date_range(self._date, self.date_)
        reset_record_time(list_day[0])

        for day_ in list_day:
            multiprocessing_count_pool(day_, check_model=True)
            my_pool_count = PoolCount()
            my_pool_count.count_trend()
            print(f'日期{day_}完成;')


if __name__ == '__main__':
    start_ = '2024-01-15'
    rm = RMHistoryCheck(_date=start_)
    rm.loop_by_date()
