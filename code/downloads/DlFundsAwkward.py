import multiprocessing
import time
import pandas as pd
from code.MySql.LoadMysql import LoadFundsAwkward as aw
from code.MySql.LoadMysql import RecordStock
from code.MySql.LoadMysql import StockPoolData as pl
from DlEastMoney import DownloadData as dle
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class DownloadFundsAwkward:
    """
    # 函数说明
    # 下载数据 DownloadFundsAwkwardData
    # 1.下载排名前近3年收益排名前600的基金数据。
    # 2.下载此基金数据重仓前10的股票数据。
    """

    def __init__(self, download_date):

        self.download_date = pd.to_datetime(download_date).date()
        self.pending = None

    def pending_data(self):

        record = RecordStock.load_record_download_top500fundspositionstock()

        record['Date'] = pd.to_datetime(record['Date'])  # .date
        record_date = record.loc[0, 'Date'].date()

        if record_date != self.download_date:
            record['Date'] = self.download_date
            record['Status'] = 'pending'
            sql = f" `Status` = 'pending', `Date` = %s;"
            # 更新表格数据
            params = (self.download_date,)
            RecordStock.set_table_record_download_top500fundspositionstock(sql, params)

        record = record[(record['Status'] == 'pending')].reset_index(drop=True)
        return record

    def awkward_top10(self, start: int, end: int):

        num = 0

        for index in range(start, end):

            funds_name = self.pending.loc[index, 'Name']
            funds_code = self.pending.loc[index, 'Code']
            id_ = self.pending.loc[index, 'id']

            info_text = f'回测进度：\n总股票数:{end - start}个; ' \
                        f'剩余股票: {end - start - num}个;\n当前股票：{funds_name},{funds_code};'

            logging.info(info_text)

            try:
                data = dle.funds_awkward(funds_code)

            except Exception as ex:

                info_text = f'Download Funds awkward error: {ex}'
                logging.info(info_text)

                try:
                    data = dle.funds_awkward_by_driver(funds_code)

                except Exception as ex:
                    info_text = f'Download Funds awkward error: {ex}'
                    logging.info(info_text)

                    # 更新参数
                    sql = f''' `Status` = 'failed' where id = %s;'''
                    params = (id_,)
                    RecordStock.set_table_record_download_top500fundspositionstock(sql, params)

                    continue

            if data.empty:
                # 更新参数
                sql = f''' `Status` = 'failed' where id = %s;'''
                params = (id_,)
                RecordStock.set_table_record_download_top500fundspositionstock(sql, params)
                continue

            data['funds_name'] = funds_name
            data['funds_code'] = funds_code
            data['Date'] = self.download_date

            data = data[['stock_name', 'funds_name', 'funds_code', 'Date']]
            aw.append_fundsAwkward(data)

            sql = f''' `Status` = 'success' where id = %s;'''
            params = (id_,)
            RecordStock.set_table_record_download_top500fundspositionstock(sql, params)

            info_text = f'{funds_name} data download success;\n'
            logging.info(info_text)

            num += 1
            time.sleep(5)

    def multi_processing(self):

        self.pending = self.pending_data()

        if self.pending.empty:
            info_text = f'funds awkward top 10 stock data no more data;\n'
            logging.info(info_text)
            return True

        indexes = self.pending.shape[0]

        if indexes < 3:
            p1 = multiprocessing.Process(target=self.awkward_top10, args=(0, indexes,))
            p1.start()
            return True

        index1 = indexes // 3
        index2 = indexes // 3 * 2

        p1 = multiprocessing.Process(target=self.awkward_top10, args=(0, index1,))
        p2 = multiprocessing.Process(target=self.awkward_top10, args=(index1, index2,))
        p3 = multiprocessing.Process(target=self.awkward_top10, args=(index2, indexes,))

        p1.start()
        p2.start()
        p3.start()

        return True


class AnalysisFundsAwkward:
    """
    # 函数说明
    # 分析统计数据 Analysis Funds Awkward Data
    # 1.统计出股票池；
    # 2.找出基金增持股票；
    # 3.找出基金减持股票；
    # 4.找出板块变动数据；
    """

    def __init__(self, dl_date):

        self.DlDate = pd.to_datetime(dl_date)
        self.pool = pl.load_StockPool()

        self.awkward = aw.load_fundsAwkward()
        self.awkward = self.awkward[self.awkward['Selection'] == 1]

        self.num_max = 200
        self.num_min = 1

        self.count_dic = {}

    def normalization_all_data(self):

        for _, row in self.pool.iterrows():

            stock_name = row['name']
            id_ = row['id']
            data_ = self.awkward[self.awkward['stock_name'] == stock_name].groupby('Date').count().reset_index()

            data_['stock_name'] = stock_name

            data_ = data_.rename(columns={'Selection': 'count'})
            data_['TrendCount'] = data_['count'] - data_['count'].shift(1)
            data_['score'] = round((data_['count'] - self.num_min) / (self.num_max - self.num_min), 4)
            data_ = data_[['stock_name', 'count', 'TrendCount', 'score', 'Date']]

            if data_.shape[0]:
                score = data_.iloc[0]['score']
                aw.append_awkwardNormalization(data_)

            else:
                score = 0

            # 更新股票池基金得分
            sql = f'''FundsAwkward = %s where id = '%s' ;'''
            parser = (score, id_)
            pl.set_table_to_pool(sql, params=parser)
            self.count_dic[stock_name] = score

        print(f'Success count: {self.count_dic}')

    def normalization_select_date(self):

        awkward = self.awkward[self.awkward['Date'] == self.DlDate]
        print(awkward.head())
        print(self.pool.head())
        # exit()
        # todo 此函数和用法有问题，需要改进
        if awkward.empty:
            return False

        for _, row in self.pool.iterrows():

            stock_name = row['name']
            stock_id = row['id']

            data_ = self.awkward[self.awkward['stock_name'] == stock_name].groupby('Date').count().tail(3).reset_index()

            # print(data_)

            # data_awkward = awkward[awkward['stock_name'] == stock_name].groupby('Date').count()
            # print(data_awkward)
            # exit()
            data_['stock_name'] = stock_name
            data_ = data_.rename(columns={'Selection': 'count'})
            data_['TrendCount'] = data_['count'] - data_['count'].shift(1)
            data_['score'] = round((data_['count'] - self.num_min) / (self.num_max - self.num_min), 4)
            data_ = data_[['stock_name', 'count', 'TrendCount', 'score', 'Date']].tail(1)

            if data_.shape[0]:
                score = data_.iloc[0]['score']
                aw.append_awkwardNormalization(data_)

            else:
                score = 0

            # 更新股票池基金得分
            sql = f'''FundsAwkward= %s where id='%s';'''
            parser = (score, stock_id)
            pl.set_table_to_pool(sql, parser)
            self.count_dic[stock_name] = score

        print(f'Success count: {self.count_dic}')


if __name__ == '__main__':
    DlDate = '2024-01-14'
    analysis = AnalysisFundsAwkward(DlDate)
    analysis.normalization_select_date()
    # download = DownloadFundsAwkward(DlDate)
    # download.multi_processing()
