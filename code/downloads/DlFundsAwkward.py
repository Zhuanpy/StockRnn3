import multiprocessing
import time
import pandas as pd
from code.MySql.LoadMysql import LoadFundsAwkward as aw
from code.MySql.LoadMysql import RecordStock
from code.MySql.LoadMysql import StockPoolData as pl
from DlEastMoney import DownloadData as dle


class DownloadFundsAwkward:
    """
    # 函数说明
    # 下载数据 DownloadFundsAwkwardData
    # 1.下载排名前近3年收益排名前300的基金数据。
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

            print(f'回测进度：\n总股票数:{end - start}个; 剩余股票: {end - start - num}个;\n'
                  f'当前股票：{funds_name},{funds_code};')

            try:
                data = dle.funds_awkward(funds_code)

            except Exception as ex:
                print(f'Dl EastMoney funds_awkward error: {ex}')
                data = dle.funds_awkward_by_driver(funds_code)

            if data.empty:
                sql = f''' `Status` = 'failed' where id = %s;'''
                params = (id_,)
                RecordStock.set_table_record_download_top500fundspositionstock(sql, params)
                print(f'{funds_name} data download failed;\n')
                continue

            data['funds_name'] = funds_name
            data['funds_code'] = funds_code
            data['Date'] = self.download_date

            data = data[['stock_name', 'funds_name', 'funds_code', 'Date']]
            aw.append_fundsAwkward(data)

            sql = f''' `Status` = 'success' where id = %s;'''
            params = (id_,)
            RecordStock.set_table_record_download_top500fundspositionstock(sql, params)
            # print(data)
            print(f'{funds_name} data download success;\n')
            num += 1
            time.sleep(5)

    def multi_processing(self):
        self.pending = self.pending_data()
        print(self.pending.tail())
        indexes = self.pending.shape[0]
        # print(indexes)
        # exit()
        if indexes:
            if indexes > 3:

                index1 = indexes // 3
                index2 = indexes // 3 * 2

                p1 = multiprocessing.Process(target=self.awkward_top10, args=(0, index1,))
                p2 = multiprocessing.Process(target=self.awkward_top10, args=(index1, index2,))
                p3 = multiprocessing.Process(target=self.awkward_top10, args=(index2, indexes,))

                p1.start()
                p2.start()
                p3.start()

            else:
                p1 = multiprocessing.Process(target=self.awkward_top10, args=(0, indexes,))
                p1.start()


class AnalysisFundsAwkward:
    """
    # 函数说明
    # 分析统计数据 AnalysisFundsAwkwardData
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

    def normalization_last(self):

        awkward = self.awkward[self.awkward['Date'] == self.DlDate]
        print(self.pool.head())

        if awkward.shape[0]:
            for index in self.pool.index:
                stock_name = self.pool.loc[index, 'name']
                stock_id = self.pool.loc[index, 'id']

                data_ = self.awkward[self.awkward['stock_name'] == stock_name
                                     ].groupby('Date').count().tail(3).reset_index()

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
    # aly = AnalysisFundsAwkward(dl_date=DlDate)
    # aly.normalization_last()
    download = DownloadFundsAwkward(DlDate)
    download.multi_processing()
