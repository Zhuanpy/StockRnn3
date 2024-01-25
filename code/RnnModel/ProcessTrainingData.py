from code.MySql.LoadMysql import LoadRnnModel
import pandas as pd

"""
处理训练数据： 
一： 处理 1分钟数据
1. 考虑第一次训练， 日后继续训练; 这里得考虑数据第一次采用，日后怎么避免重复和漏用； 
2. 保存1分钟开始 结束参数， 保存 15分钟信号名；

二： 处理 15分钟数据

3. 保存15分钟数据参数，特别是极大 极小，中位数等 ；

三： 处理模型数据
4. 模型数据保存 及 记录； 从什么日期及信号名开始保存 ； 从什么日期 及 信号名开始结束保存


"""
from code.MySql.sql_utils import Stocks
from code.MySql.DataBaseStockData1m import StockData1m
from code.RnnDataFile.JsonData import LoadJsonData
from code.parsers.RnnParser import *
from code.Normal import ReadSaveFile, ResampleData

class TrainingDataCalculate():

    """
    训练数据处理
    """

    def __init__(self, stock: str, month: str, ):  # _month

        # ModelData.__init__(self)
        self.stock_start_year = '2018-01-01'
        self.stock_name, self.stock_code, self.stock_id = Stocks(stock)

        self.month = month
        self.pre_month = ''  # 前一个月数据

        self.data_1m = None
        self.data_15m = None
        self.times_data = None

        self.record_json_data = None
        self.RecordStartDate = None
        self.RecordEndDate = None

        self.freq = '15m'
        self.start_date_1m = None

        self.daily_volume_max = None

    def load_start_date(self):

        try:
            json_data, pre_json_parser_month = LoadJsonData.find_json_parser_by_month_folder(self.pre_month, self.stock_code)
            start_date = json_data['TrainingData']['EndSignal']['StartTime']  # 提取上次训练数据，截止日期
            return start_date

        except ValueError:
            return self.stock_start_year

    def load_1m_data(self):
        start_date = self.load_start_date()  # 要么从json 数据中读取 ；  要么就从股票池中读取第一个天

        # 导入数据从开始日期开始
        data_1m = StockData1m.load_1m(self.stock_code, start_date)

        return data_1m

    def stand_save_parser(self, data, column, drop_duplicates, drop_column):

        """
           Standardize and save the specified column data.

           Parameters:
               data (pd.DataFrame): Input DataFrame.
               column (str): Column to be standardized.
               drop_duplicates (bool): Flag indicating whether to drop duplicates.
               drop_column (str): Name of the column to be dropped if `drop_duplicates` is True.

           Returns:
               pd.DataFrame: DataFrame with standardized and saved column.
           """

        if drop_duplicates:

            if drop_column == SignalChoice:
                df = data.dropna(subset=[SignalChoice])

            else:
                df = data.drop_duplicates(subset=[column])

            med = df[column].median()
            mad = abs(df[column] - med).median()

        else:
            med = data[column].median()
            mad = abs(data[column] - med).median()

        high = round(med + (3 * 1.4826 * mad), 2)
        low = round(med - (3 * 1.4826 * mad), 2)

        # 查看参数
        try:
            """ 读取历史的参数json数据 """
            parser_data, pre_month = LoadJsonData.find_json_parser_by_month_folder(self.pre_month, self.stock_code)

            pre_high = parser_data['TrainingData']['dataDaily'][column]['num_max']
            pre_low = parser_data['TrainingData']['dataDaily'][column]['num_min']

        except ValueError:
            pre_high = high
            pre_low = low

        """ 新数据和历史的数据对比 """
        high = max([high, pre_high])
        low = min([low, pre_low])

        """ 去极值  """
        data.loc[(data[column] > high), column] = high
        data.loc[(data[column] < low), column] = low

        """ 数据归一化 """
        data[column] = (data[column] - low) / (high - low)

        current_parser_data = ReadSaveFile.read_json(self.month, self.stock_code)
        current_parser_data['TrainingData']['dataDaily'][column] = {'num_max': high, 'num_min': low}
        ReadSaveFile.save_json(current_parser_data, self.month, self.stock_code)  # 更新参数

        return data

    def stand_read_parser(self, data, column, match):
        parser_data = ReadSaveFile.read_json(self.month, self.stock_code)
        num_max = parser_data[self.stock_code][match]['num_max']
        num_min = parser_data[self.stock_code][match]['num_min']

        data.loc[data[column] > num_max, column] = num_max
        data.loc[data[column] < num_min, column] = num_min
        data[column] = (data[column] - num_min) / (num_max - num_min)
        return data

    def column_stand(self):
        # 保存 daily_volume_max

        if not self.daily_volume_max:
            _date = '2018-01-01'
            self.data_1m = StockData1m.load_1m(self.stock_code, _date)
            self.data_1m = self.data_1m[self.data_1m['date'] > pd.to_datetime(_date)]

            data_daily = ResampleData.resample_1m_data(data=self.data_1m, freq='daily')
            data_daily.loc[:, 'date'] = pd.to_datetime(data_daily['date']) + pd.Timedelta(minutes=585)
            data_daily.loc[:, DailyVolEma] = data_daily['volume'].rolling(90, min_periods=1).mean()

            self.daily_volume_max = round(data_daily[DailyVolEma].max(), 2)

        parser_data = ReadSaveFile.read_json(self.month, self.stock_code)
        parser_data[DailyVolEma] = self.daily_volume_max
        ReadSaveFile.save_json(parser_data, self.month, self.stock_code)

        save_list = [('volume', False, None),
                     (Daily1mVolMax1, True, Daily1mVolMax1),
                     (Daily1mVolMax5, True, Daily1mVolMax5),
                     (Daily1mVolMax15, True, Daily1mVolMax15),
                     (Bar1mVolMax1, False, None),
                     (Cycle1mVolMax1, True, SignalChoice),
                     (Cycle1mVolMax5, True, SignalChoice),
                     (Bar1mVolMax5, False, None),
                     (CycleLengthMax, True, SignalChoice),
                     (nextCycleLengthMax, True, SignalChoice),
                     (CycleLengthPerBar, False, None),
                     (CycleAmplitudeMax, True, SignalChoice),
                     (nextCycleAmplitudeMax, True, SignalChoice),
                     (CycleAmplitudePerBar, False, None),
                     ('EndDaily1mVolMax5', True, SignalChoice)]

        for i in save_list:
            column = i[0]
            drop_duplicates = i[1]
            drop_column = i[2]
            self.data_15m = self.stand_save_parser(self.data_15m, column, drop_duplicates, drop_column)

        read_dict = {preCycle1mVolMax1: Cycle1mVolMax1,
                     preCycle1mVolMax5: Cycle1mVolMax5,
                     preCycleLengthMax: CycleLengthMax,
                     preCycleAmplitudeMax: CycleAmplitudeMax}

        for key, value in read_dict.items():
            self.data_15m = self.stand_read_parser(self.data_15m, key, value)

        self.data_15m = self.data_15m.dropna(subset=[Signal])

        last_signal_times = self.data_15m.iloc[-1][SignalTimes]

        self.data_15m = self.data_15m[self.data_15m[SignalTimes] != last_signal_times]

        # 选择模型数据
        all_columns = ['date', Signal, SignalTimes, SignalChoice,
                       StartPriceIndex, EndPriceIndex, CycleAmplitudePerBar, CycleAmplitudeMax,
                       Cycle1mVolMax1, Cycle1mVolMax5,
                       CycleLengthMax, CycleLengthPerBar,
                       Daily1mVolMax1, Daily1mVolMax5, Daily1mVolMax15,
                       preCycle1mVolMax1, preCycleLengthMax, Bar1mVolMax1,
                       nextCycleLengthMax, preCycle1mVolMax5,
                       'volume', Bar1mVolMax5, preCycleAmplitudeMax,
                       'EndDaily1mVolMax5', nextCycleAmplitudeMax]

        self.data_15m = self.data_15m[all_columns]

        return self.data_15m

    def first_calculate(self, data_1m):

        self.data_15m = ResampleData.resample_1m_data(data=data_1m, freq=self.freq)

        self.data_15m = SignalMethod.signal_by_MACD_3ema(self.data_15m, self.data_1m).set_index('date', drop=True)

        data_daily = ResampleData.resample_1m_data(data=self.data_1m, freq='daily')
        data_daily['date'] = pd.to_datetime(data_daily['date']) + pd.Timedelta(minutes=585)
        data_daily[DailyVolEma] = data_daily['volume'].rolling(90, min_periods=1).mean()

        daily_volume_max = round(data_daily[DailyVolEma].max(), 2)

        # 读取旧参数
        try:
            file_name = f"{self.stock_code}.json"
            file_path = find_file_in_paths(self.month, 'json', file_name)

            parser_data = ReadSaveFile.read_json_by_path(file_path)
            pre_daily_volume_max = parser_data[DailyVolEma]

        except:
            pre_daily_volume_max = daily_volume_max

        # 使用 max 函数一行完成最大值的更新
        self.daily_volume_max = max(daily_volume_max, pre_daily_volume_max)

        # 简化日线数据处理
        data_daily[DailyVolEmaParser] = self.daily_volume_max / data_daily[DailyVolEma]
        data_daily = data_daily[['date', DailyVolEmaParser]].set_index('date', drop=True)

        self.data_15m = self.data_15m.join([data_daily]).reset_index()

        self.data_15m[DailyVolEmaParser] = self.data_15m[DailyVolEmaParser].fillna(method='ffill')

        # 排除最后 signal Times , 可能此周期并未走完整
        last_signal_times = self.data_15m.iloc[-1][SignalTimes]
        self.data_15m = self.data_15m[self.data_15m[SignalTimes] != last_signal_times]

        return self.data_15m

    def find_bar_max_1m(self, x, num):

        try:
            start_time = pd.to_datetime(x) + pd.Timedelta(minutes=-15)
            end_time = pd.to_datetime(x)

            max_vol = self.data_1m[(self.data_1m['date'] > start_time) & (self.data_1m['date'] < end_time)]
            max_vol = max_vol.sort_values(by=['volume'])['volume'].tail(num).mean()

            if pd.notna(max_vol):  # 如果 max_vol 不是 NaN
                max_vol = int(max_vol)  # volume 1m is 'nan'

            else:
                max_vol = None

        except Exception as ex:
            # 处理其他异常，并打印错误信息
            max_vol = None
            print(f'{self.stock_name} 函数： find_bar_max_1m 错误;\n{ex}')

        return max_vol

    def second_calculate(self):

        for index in self.data_15m.dropna(subset=[SignalChoice, EndPriceIndex]).index:
            signal_times = self.data_15m.loc[index, SignalTimes]
            end_price_time = self.data_15m.loc[index, EndPriceIndex]

            selects = self.data_15m[(self.data_15m[SignalTimes] == signal_times) &
                                    (self.data_15m[EndPriceIndex] <= end_price_time)].tail(35)

            # 优化索引获取
            st_index, ed_index = selects.index[0], selects.index[-1]

            self.data_15m.loc[st_index:ed_index, Bar1mVolMax1] = self.data_15m.loc[st_index:ed_index]['date'].apply(
                self.find_bar_max_1m, args=(1,))

            self.data_15m.loc[st_index:ed_index, Bar1mVolMax5] = self.data_15m.loc[st_index:ed_index]['date'].apply(
                self.find_bar_max_1m, args=(5,))

        # 替换无穷大和无穷小的值为 NaN
        self.data_15m = self.data_15m.replace([np.inf, -np.inf], np.nan)

        # 计算数据保存
        self.save_15m_data()

        return self.data_15m

    def third_calculate(self):

        self.data_15m[Signal] = self.data_15m[Signal].astype(float)

        # 成交量相关参数的处理
        vol_parser = ['volume', Cycle1mVolMax1, Cycle1mVolMax5,
                      Daily1mVolMax1, Daily1mVolMax5, Daily1mVolMax15,
                      Bar1mVolMax1, Bar1mVolMax5, 'EndDaily1mVolMax5']  # 成交量乘以参数，相似化

        for i in vol_parser:
            self.data_15m[i] = round(self.data_15m[i] * self.data_15m[DailyVolEmaParser])

        next_dic = {nextCycleAmplitudeMax: CycleAmplitudeMax,
                    nextCycleLengthMax: CycleLengthMax}

        condition = (~self.data_15m[SignalChoice].isnull())
        for keys, values in next_dic.items():
            self.data_15m.loc[condition, keys] = self.data_15m.loc[condition, values].shift(-1)

        # 提取前周期相关数据：
        condition = (~self.data_15m[SignalChoice].isnull())

        pre_dic = {preCycle1mVolMax1: Cycle1mVolMax1,
                   preCycle1mVolMax5: Cycle1mVolMax5,
                   preCycleAmplitudeMax: CycleAmplitudeMax,
                   preCycleLengthMax: CycleLengthMax}

        for key, values in pre_dic.items():
            self.data_15m.loc[condition, key] = self.data_15m.loc[condition, values].shift(1)

        fills = list(pre_dic.keys()) + list(next_dic.keys())

        self.data_15m[fills] = self.data_15m[fills].fillna(method='ffill')

        return self.data_15m

    def data_1m_calculate(self, ):

        """
        :param
        :record_stat: datatime, 输入datatime 类型， 参考日期 ；
        读取一分钟数据，如果历史训练数据有记录已经计算的数据，则从结束日期开始算，如果没有，则从保存历史数据开始算；
        """

        # 判断是否有指定的 RecordStartDate
        if self.record_json_data:
            start_date = self.record_json_data['model']['EndDate']

        else:
            start_date = ''  # todo 读取股票池数据，数据开始日期 ；

        # 加载1分钟数据, 从哪个日期开始加载 ？
        data_1m = StockData1m.load_1m(self.stock_code, start_date)
        data_1m = data_1m.sort_values(by=['date'])

        # 提取数据起始日期
        self.start_date_1m = data_1m.iloc[0]['date']

        # 筛选数据时间范围
        data_1m = data_1m[(data_1m['date'] > (pd.to_datetime(start_date) + pd.Timedelta(days=-30))) &
                          (data_1m['date'] < (pd.to_datetime(self.month) + pd.Timedelta(days=-30)))]

        # 去除重复值和缺失值
        data_1m = data_1m.dropna(subset=['date']).drop_duplicates(subset=['date']).reset_index(drop=True)

        return data_1m

    def save_15m_data(self):

        if self.RecordStartDate:

            # 筛选数据并加载旧数据
            self.data_15m = self.data_15m[self.data_15m['date'] > self.RecordEndDate]
            from sqlalchemy.exc import IntegrityError
            try:
                StockData15m.append_15m(self.stock_code, self.data_15m)

            except IntegrityError:
                old = StockData15m.load_15m(self.stock_code)
                last_date = old.iloc[-1]['date']
                new = self.data_15m[self.data_15m['date'] > last_date]
                old = pd.concat([old, new], ignore_index=True)
                StockData15m.replace_15m(self.stock_code, old)

        else:
            StockData15m.replace_15m(self.stock_code, self.data_15m)

        # 保存15m数据截止日期相关信息
        record_end_date = self.data_15m.iloc[-1]['date'].strftime('%Y-%m-%d %H:%M:%S')
        record_end_signal = self.data_15m.iloc[-1]['Signal']
        record_end_signal_times = self.data_15m.iloc[-1]['SignalTimes']
        record_end_signal_start_time = self.data_15m.iloc[-1]['SignalStartTime'].strftime('%Y-%m-%d %H:%M:%S')
        record_next_start = self.data_15m.drop_duplicates(subset=[SignalTimes]).tail(6).iloc[0]['date'].strftime(
            '%Y-%m-%d %H:%M:%S')

        # 读取旧参数并更新
        records = ReadSaveFile.read_json(self.month, self.stock_code)
        records.update({
            'RecordEndDate': record_end_date,
            'RecordEndSignal': record_end_signal,
            'RecordEndSignalTimes': record_end_signal_times,
            'RecordEndSignalStartTime': record_end_signal_start_time,
            'RecordNextStartDate': record_next_start})

        ReadSaveFile.save_json(records, self.month, self.stock_code)  # 更新参数

    def data_calculate(self):

        # 读取json参数
        self.record_json_data = self.rnn_parser_data()

        # 导入 1m 数据， 更具参数选择；  读取参考的日期
        self.data_1m = self.data_1m_calculate()

        self.data_15m = self.first_calculate()

        self.data_15m = self.second_calculate()

        self.data_15m = self.third_calculate()

        self.data_15m = self.column_stand()  # 标准化数据

        return self.data_15m

    def calculation_single(self):

        try:
            path = find_file_in_paths(self.month, 'json', f'{self.stock_code}.json')  # 返回 json 路径
            record = ReadSaveFile.read_json_by_path(path)
            self.RecordEndDate = record[self.stock_code]['RecordEndDate']
            self.RecordStartDate = record[self.stock_code]['NextStartDate']

        except ValueError:
            pass

        self.data_15m = self.data_calculate()

        for i in range(4):
            x = self.x_columns[i]
            y = self.y_column[i]
            model_name = self.model_name[i]
            self.data_common(model_name, x, y)

    def calculation_read_from_sql(self):

        self.data_15m = StockData15m.load_15m(self.stock_code)

        self.data_15m = self.third_calculate()
        self.data_15m = self.column_stand()  # 标准化数据

        for i in range(4):
            x = self.x_columns[i]
            y = self.y_column[i]
            model_name = self.model_name[i]
            self.data_common(model_name, x, y)


class RMTrainingData:

    def __init__(self, month: str):  # _month
        self.month = month

    def single_stock(self, stock: str):
        calculation = TrainingDataCalculate(stock, self.month)
        calculation.calculation_single()

    def update_train_records(self, records):
        """更新训练表格记录"""
        ids = tuple(records.id)

        sql = f'''ParserMonth = %s, ModelData = 'pending' where id in %s;'''

        params = (self.month, ids)
        LoadRnnModel.set_table_train_record(sql, params)

    def all_stock(self):

        load = LoadRnnModel.load_train_record()

        records = load[load['ParserMonth'] == self.month]

        # 更新训练记录中的状态
        if records.empty:
            records = load.copy()
            records['ParserMonth'] = self.month
            records['ModelData'] = 'pending'
            records['ModelCheck'] = 'pending'
            records['ModelError'] = 'pending'

            self.update_train_records(records)

        # 查看等待数据
        records = records[~records['ModelData'].isin(['success'])].reset_index(drop=True)

        if records.empty:
            print(f'{self.month}月训练数据创建完成')
            return False  # 结束运行，因为 records 为空

        for i, row in records.iterrows():
            stock_ = row['name']
            id_ = row['id']

            print(f'\n计算进度：'
                  f'\n剩余股票: {(records.shape[0] - i)} 个; 总股票数: {records.shape[0]}个;'
                  f'\n当前股票：{stock_};')

            try:
                run = TrainingDataCalculate(stock_, self.month)
                run.calculation_read_from_sql()

                sql = f'''ModelData = 'success', ModelDataTiming = %s where id = %s; '''

                params = (pd.Timestamp('now').date(), id_)
                LoadRnnModel.set_table_train_record(sql, params)

            except Exception as ex:
                print(f'Model Data Create Error: {ex}')
                sql = f'''ModelData = 'error', ModelDataTiming = NULL where id = %s; '''
                params = (LoadRnnModel.db_rnn, LoadRnnModel.tb_train_record, id_)
                LoadRnnModel.set_table_train_record(sql, params)

        return True


if __name__ == '__main__':
    month_ = '2023-01'
    start_d = '2018-01-01'
    running = RMTrainingData(month_)
    running.all_stock()
