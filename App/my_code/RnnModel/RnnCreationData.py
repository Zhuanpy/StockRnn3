# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from ..MySql.DataBaseStockData1m import StockData1m
from ..MySql.DataBaseStockData15m import StockData15m
from ..MySql.sql_utils import Stocks
from ..parsers.RnnParser import *
from App.my_code.utils.Normal import ReadSaveFile, ResampleData
from ..Signals.StatisticsMacd import SignalMethod
from ..RnnDataFile.stock_path import StockDataPath

from App.static import file_root
from Rnn_utils import find_file_in_paths

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 5000)


class ModelData:
    """
    1. 处理模型数据
    2. 模型数据准备
    """

    def __init__(self):

        self.root = file_root()
        self.month = None
        self.stock_code = None
        self.data_15m = None

        self.x_columns = XColumn()
        self.y_column = YColumn()
        self.model_name = ModelName

    def load_pre_month_existing_train_data(self, model_name: str) -> tuple:

        """
        导入以前的数据，尝试读取前数据文件夹。

        :param model_name: 模型名字
        :return: 前数据文件夹内容，格式为 (data_x, data_y, pre_month)
        """

        file_x = f'{model_name}_{self.stock_code}_x.npy'
        file_y = f'{model_name}_{self.stock_code}_y.npy'

        try:
            # 前数据读取
            file_path_x, pre_month = find_file_in_paths(self.month, 'train_data', file_x)
            file_path_y, pre_month = find_file_in_paths(self.month, 'train_data', file_y)
            data_x = np.load(file_path_x, allow_pickle=True)
            data_y = np.load(file_path_y, allow_pickle=True)
            return data_x, data_y, pre_month

        except FileNotFoundError:
            return np.zeros([0]), np.empty([0]), None

    def _save_data(self, model_name: str, data_x: np.ndarray, data_y: np.ndarray) -> None:
        """
        保存数据至指定路径。

        :param model_name: 模型名字
        :param data_x: 训练数据集 X
        :param data_y: 训练数据集 Y
        """
        file_x = f'{model_name}_{self.stock_code}_x.npy'
        file_y = f'{model_name}_{self.stock_code}_y.npy'

        file_path_x = StockDataPath.train_data_path(self.month, file_x)
        file_path_y = StockDataPath.train_data_path(self.month, file_y)

        np.save(file_path_x, data_x)
        np.save(file_path_y, data_y)

    def data_common(self, model_name: str, column_x: list, column_y: list, height: int = 30, width: int = 30):  # width=w2, height=h1
        """
        处理通用数据。

        :param model_name: 模型名字
        :param column_x: X 数据列名称集
        :param column_y: Y 数据列名称集
        :param height: 数据矩阵的高度（默认为30）
        :param width: 数据矩阵的宽度（默认为30）
        """

        data_x, data_y, pre_month = self.load_pre_month_existing_train_data(model_name)  # 加载以前数据

        # 整理数据
        data_ = self.data_15m.dropna(subset=[SignalChoice])

        for st in data_[SignalTimes]:
            x = self.data_15m[self.data_15m[SignalTimes] == st][column_x].dropna(how='any').tail(height)
            y = self.data_15m[self.data_15m[SignalTimes] == st][column_y].dropna(how='any').tail(1)

            if not x.shape[0] or not y.shape[0]:
                continue

            x = pd.concat([x[[Signal]], x], axis=1)
            x = x.to_numpy()

            # 填充数据为 30*30 矩阵，不足部分补0
            h = height - x.shape[0]
            w = width - x.shape[1]

            ht = h // 2  # height top
            hl = h - ht  # height bottom

            wl = w // 2  # width left
            wr = w - wl  # width right

            x = np.pad(x, ((ht, hl), (wr, wl)), 'constant', constant_values=(0, 0))
            x.shape = (1, height, width, 1)
            y = y.to_numpy()

            # 合并数据
            if data_x.shape[0]:
                data_x = np.append(data_x, x, axis=0)
                data_y = np.append(data_y, y, axis=0)

            else:
                data_x = x
                data_y = y

        # 新数据储存
        self._save_data(model_name, data_x, data_y)

        print(f'{model_name}, shape: {data_x.shape};')

    def data_cycle_length(self) -> None:
        x = self.x_columns[0]
        y = self.y_column[0]
        self.data_common(self.model_name[0], x, y)

    def data_cycle_change(self) -> None:
        x = self.x_columns[1]
        y = self.y_column[1]
        self.data_common(self.model_name[1], x, y)

    def data_bar_change(self) -> None:
        x = self.x_columns[2]
        y = self.y_column[2]
        self.data_common(self.model_name[2], x, y)

    def data_bar_volume(self) -> None:
        x = self.x_columns[3]
        y = self.y_column[3]
        self.data_common(self.model_name[3], x, y)


class TrainingDataCalculate(ModelData):
    """
    训练数据处理
    """

    def __init__(self, stock: str, month: str, start_date: str):  # _month

        ModelData.__init__(self)
        self.stock_name, self.stock_code, self.stock_id = Stocks(stock)

        self.month = month
        self.data_1m = None
        self.data_15m = None
        self.times_data = None

        self.RecordStartDate = None
        self.RecordEndDate = None

        self.freq = '15m'
        self.start_date = start_date
        self.start_date_1m = None

        self.daily_volume_max = None

    def rnn_parser_data(self):
        data = ReadSaveFile.read_json(self.month, self.stock_code)
        if self.stock_code not in data:
            data[self.stock_code] = {}
            ReadSaveFile.save_json(data, self.month, self.stock_code)

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
            file_name = f"{self.stock_code}.json"
            file_path, pre_month = find_file_in_paths(self.month, 'json', file_name)

            parser_data = ReadSaveFile.read_json_by_path(file_path)
            pre_high = parser_data[self.stock_code][column]['num_max']
            pre_low = parser_data[self.stock_code][column]['num_min']

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

        parser_data = ReadSaveFile.read_json(self.month, self.stock_code)
        parser_data[column] = {'num_max': high, 'num_min': low}
        ReadSaveFile.save_json(parser_data, self.month, self.stock_code)  # 更新参数

        return data

    def stand_read_parser(self, data: pd.DataFrame, column: str, match: str) -> pd.DataFrame:
        """
        读取标准化参数，并应用于指定列。

        :param data: 输入的 DataFrame
        :param column: 需要标准化的列名称
        :param match: 参数匹配的列名称
        :return: 标准化后的 DataFrame
        """
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

    def first_calculate(self):

        self.data_15m = ResampleData.resample_1m_data(data=self.data_1m, freq=self.freq)

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
            pre_daily_volume_max = parser_data[self.stock_code][DailyVolEma]

        except :

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

    def data_1m_calculate(self):

        self.rnn_parser_data()

        # 判断是否有指定的 RecordStartDate
        if self.RecordStartDate:
            start_date = self.RecordStartDate

        else:
            start_date = self.start_date

        # 加载1分钟数据并进行筛选
        self.data_1m = StockData1m.load_1m(self.stock_code, start_date)
        self.data_1m = self.data_1m.sort_values(by=['date'])

        # 提取数据起始日期
        self.start_date_1m = self.data_1m.iloc[0]['date']

        # 筛选数据时间范围
        self.data_1m = self.data_1m[(self.data_1m['date'] > (pd.to_datetime(start_date) + pd.Timedelta(days=-30))) &
                                    (self.data_1m['date'] < (pd.to_datetime(self.month) + pd.Timedelta(days=-30)))]

        # 去除重复值和缺失值
        self.data_1m = self.data_1m.dropna(subset=['date']).drop_duplicates(subset=['date']).reset_index(drop=True)

        return self.data_1m

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

    def data_15m_calculate(self):

        # # 1m 数据选择
        self.data_1m_calculate()

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

        self.data_15m = self.data_15m_calculate()

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


if __name__ == '__main__':
    month_ = '2023-01'
    start_d = '2018-01-01'
    # running = TrainingDataCalculate(month_, start_d)
    # running.all_stock()
