# -*- coding: utf-8 -*-
import os
import smtplib
import time
from email.message import Message
import pandas as pd
from scipy import stats
import numpy as np
import json
from App.my_code.RnnDataFile.stock_path import StockDataPath

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 5000)


def count_times(func):
    def wrapper(*args):
        start = time.process_time()
        results = func(*args)
        end = time.process_time()
        print(f'运行时间：{int(end - start)}秒\n')
        return results

    return wrapper


class MathematicalFormula:

    @classmethod
    def normal_get_p(cls, x, mean=0, std=1):
        z = (x - mean) / std
        p = stats.norm.cdf(z)
        return p

    @classmethod
    def normal_get_x(cls, p, mean=0, std=1):
        z = stats.norm.ppf(p)
        x = z * std + mean
        return x

    @classmethod
    def filter_median(cls, data, column):
        med = data[column].median()
        mad = abs(data[column] - med).median()

        high = med + (3 * 1.4826 * mad)
        low = med - (3 * 1.4826 * mad)

        data.loc[(data[column] > high), column] = high
        data.loc[(data[column] < low), column] = low

        return data

    @classmethod
    def filter_3sigma(cls, data, column: str, n=3):  # 3 sigma
        mean_ = data[column].mean()
        std_ = data[column].std()

        max_ = mean_ + n * std_
        min_ = mean_ - n * std_

        data.loc[(data[column] > max_), column] = max_
        data.loc[(data[column] < min_), column] = min_
        return data

    @classmethod
    def data2normalization(cls, column):
        num_max = column.max()
        num_min = column.min()
        column = (column - num_min) / (num_max - num_min)
        return column

    @classmethod
    def normal2value(cls, data, parser_month: str, stock_code: str, match_column: str):
        parser_data = ReadSaveFile.read_json(parser_month, stock_code)
        parser_data = parser_data[stock_code][match_column]

        high = parser_data['num_max']
        low = parser_data['num_min']

        num_normal = data * (high - low) + low
        return num_normal

    @classmethod
    def normal2Y(cls, x, mu, sigma):
        pdf = np.exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / (sigma * np.sqrt(2 * np.pi))
        return pdf


class StockCode:

    @classmethod
    def stand_code(cls, code):
        code = str(code)
        len_ = len(code)
        if len_ < 6:
            _code = '000000'
            code = f'{_code[:(6 - len_)]}{code}'
        else:
            code = code[:6]
        return code

    @classmethod
    def code2market(cls, code):
        if code[0] == '6':
            market = 'SH'

        elif code[0] == '0' or code[0] == '3':
            market = 'SZ'

        else:
            market = 'None'
            print(f'股票: {code}未区分市场类；')

        return market

    @classmethod
    def code_with_market(cls, code):

        if code[0] == '6':
            code = f'{code}.SH'

        elif code[0] == '0' or code[0] == '3':
            code = f'{code}.SZ'

        else:
            print(f'股票: {code}无市场分类;')

        return code

    @classmethod
    def code2classification(cls, code):
        classification = None
        if code[:3] == '600' or code[:3] == '601' or \
                code[:3] == '602' or code[:3] == '603' or \
                code[:3] == '605' or code[:3] == '000':
            classification = '主板'

        if code[:3] == '002':
            classification = '中小板'

        if code[:3] == '003':
            classification = '深股峙'

        if code[:3] == '688' or code[:3] == '689':
            classification = '科创板'

        if code[:3] == '300':
            classification = '创业板'

        if code[:3] == '900' or code[:3] == '200':
            classification = 'B股'

        if code[:3] == '880':
            classification = '指数'

        if code[:2] == '12' or code[:2] == '13' or code[:2] == '11':
            classification = '转债'

        if code[:2] == '20':
            classification = '债券'

        if code[:2] == '15' or code[:2] == '16' \
                or code[:2] == '50' or code[:2] == '51' \
                or code[:2] == '56' or code[:2] == '58':
            classification = '基金'

        return classification


class ReadSaveFile:

    @classmethod
    def read_json(cls, months: str, code: str):
        path = StockDataPath.json_data_path(months, code)

        try:
            with open(path, 'r') as lf:
                j = json.load(lf)

            return j

        except ValueError:
            return None

    @classmethod
    def read_json_by_path(cls, path):

        try:
            with open(path, 'r') as lf:
                j = json.load(lf)

        except FileNotFoundError:
            return None

        return j

    @classmethod
    def save_json(cls, dic: dict, months: str, code: str):
        path = StockDataPath.json_data_path(months, code)
        with open(path, 'w') as f:
            json.dump(dic, f)

    @classmethod
    def read_all_file(cls, path, ends):
        fl = []
        for root, dirs, files in os.walk(path):
            for f in files:
                if f.endswith(ends):
                    fl.append(f)
        return fl

    @classmethod
    def find_all_file(cls, path):
        fl = []
        for p, dir_list, files in os.walk(path):
            fl.append(files)
        return fl


class ResampleData:

    @classmethod
    def resample_fun(cls, data: pd.DataFrame, parameter: str) -> pd.DataFrame:
        """
        通用数据重采样函数。
        """
        # 转换索引为 datetime
        data['index_date'] = pd.to_datetime(data['date'])
        data = data.set_index('index_date')

        # 按指定频率重采样
        resampled = data.resample(parameter, closed='right', label='right').agg({
            'open': 'first',
            'close': 'last',
            'high': 'max',
            'low': 'min',
            'volume': 'sum',
            'money': 'sum'
        }).reset_index()

        # 重命名列并返回
        resampled = resampled.rename(columns={'index_date': 'date'}).dropna(how='any')
        return resampled[['date', 'open', 'close', 'high', 'low', 'volume', 'money']]

    @classmethod
    def _split_and_resample_60m(cls, data: pd.DataFrame) -> pd.DataFrame:
        """
        将股票的1分钟数据转换为60分钟数据，考虑上午和下午的交易时间段。
        上午：从09:31到11:30，采样时间点为10:31和11:30。
        下午：从13:00到15:00，按整点采样。

        参数：
            data (pd.DataFrame): 包含股票1分钟数据的DataFrame，需包含以下列：
                - ' date': 时间戳列 (datetime 类型或字符串时间，需可转换)
                - 'open', 'close', 'high', 'low', 'volume', 'money'

        返回：
            pd.DataFrame: 重采样后的60分钟数据。
        """
        # 确保日期为 datetime 类型，并设置为索引
        data["date"] = pd.to_datetime(data["date"])
        data["index_date"] = data["date"]

        data = data.set_index("index_date")

        # 分别提取上午和下午数据
        morning_data = data.between_time("09:31", "11:30")
        afternoon_data = data.between_time("13:00", "15:00")

        # 上午按 "90T" 采样
        morning_resampled = morning_data.resample("90T", closed="right", label="right").agg({
            "date": "last",
            "open": "first",
            "close": "last",
            "high": "max",
            "low": "min",
            "volume": "sum",
            "money": "sum"

        }).dropna()

        # 下午按 "60T" 采样，保留原始索引列
        afternoon_resampled = afternoon_data.resample("60T", closed="right", label="right").agg({
            "date": "last",  # 保留每组最后一个时间作为采样的 date
            "open": "first",
            "close": "last",
            "high": "max",
            "low": "min",
            "volume": "sum",
            "money": "sum"
        }).dropna()

        # 合并上午和下午数据
        resampled = pd.concat([morning_resampled, afternoon_resampled]).sort_values("date").reset_index(drop=True)

        return resampled

    @classmethod
    def _split_and_resample_120m(cls, data: pd.DataFrame) -> pd.DataFrame:
        # 确保日期为 datetime 类型，并设置为索引
        data["date"] = pd.to_datetime(data["date"])
        data["index_date"] = data["date"]

        data = data.set_index("index_date")

        resampled = data.resample("360T", closed="right", label="right").agg({
            "date": "last",  # 保留每组最后一个时间作为采样的 date
            "open": "first",
            "close": "last",
            "high": "max",
            "low": "min",
            "volume": "sum",
            "money": "sum"
        }).dropna().reset_index(drop=True)

        return resampled

    @classmethod
    def _resample_to_daily(cls, data: pd.DataFrame) -> pd.DataFrame:
        """
        将 1 分钟数据聚合为日 K 数据。
        """
        data["date"] = pd.to_datetime(data["date"])
        day_k = data.groupby(data["date"].dt.date).agg(
            open=("open", "first"),
            close=("close", "last"),
            high=("high", "max"),
            low=("low", "min"),
            volume=("volume", "sum"),
            money=("money", "sum")
        ).reset_index()

        day_k = day_k.rename(columns={"index": "date"})
        return day_k

    @classmethod
    def resample_1m_data(cls, data: pd.DataFrame, freq: str) -> pd.DataFrame:
        """
        根据指定频率重采样 1 分钟数据。
        """
        # 时间映射字典
        time_mappings = {
            '15m': '15T',
            '30m': '30T',
            '120m': '360T',
            'day': '1440T',
            'daily': '1440T',
            'd': '1440T',
            'D': '1440T'
        }

        if freq == '60m':
            return cls._split_and_resample_60m(data)

        if freq == '120m':
            return cls._split_and_resample_120m(data)

        elif freq in {'day', 'daily', 'd', 'D'}:
            return cls._resample_to_daily(data)

        elif freq in time_mappings:
            return cls.resample_fun(data, parameter=time_mappings[freq])

        else:
            raise ValueError(f"Unsupported frequency: {freq}")


class Useful:

    @classmethod
    def sent_emails(cls, message_title, mail_content):
        smtpserver = 'smtp.gmail.com'
        username = 'legendtravel004@gmail.com'
        password = 'duooevejgywtaoka'
        from_addr = 'legendtravel004@gmail.com'
        to_addr = ['zhangzhuan516@gmail.com']
        cc_addr = ['651748264@qq.com']

        message = Message()
        message['Subject'] = message_title  # 邮件标题
        message['From'] = from_addr
        message['To'] = ','.join(to_addr)
        message['Cc'] = ','.join(cc_addr)

        message.set_payload(mail_content)  # 邮件正文
        msg = message.as_string().encode('utf-8')

        sm = smtplib.SMTP(smtpserver, port=587, timeout=20)
        sm.set_debuglevel(1)  # 开启debug模式
        sm.ehlo()
        sm.starttls()  # 使用安全连接
        sm.ehlo()
        sm.login(username, password)
        sm.sendmail(from_addr, (to_addr + cc_addr), msg)
        time.sleep(2)  # 避免邮件没有发送完成就调用了quit()
        sm.quit()

    @classmethod
    def dashed_line(cls, num):
        return '=' * num, '-' * num

    @classmethod
    def stock_columns(cls):
        # 定义各类股票列名的字典
        par_dic = {
            'Basic': {
                1: 'date', 2: 'open', 3: 'close', 4: 'high', 5: 'low', 6: 'volume', 7: 'money'
            },
            'Macd': {
                1: 'EmaShort', 2: 'EmaMid', 3: 'EmaLong', 4: 'DIF', 5: 'DIFSm', 6: 'DIFMl', 7: 'DEA', 8: 'MACD'
            },
            'Boll': {
                1: 'BollMid', 2: 'BollStd', 3: 'BollUp', 4: 'BollDn', 5: 'StopLoss'
            },
            'Signal': {
                1: 'Signal', 2: 'SignalTimes', 3: 'SignalChoice', 4: 'SignalStartIndex'
            },
            'cycle': {
                1: 'EndPrice', 2: 'EndPriceIndex', 3: 'StartPrice', 4: 'StartPriceIndex',
                5: 'Cycle1mVolMax1', 6: 'Cycle1mVolMax5', 7: 'Bar1mVolMax1', 8: 'Bar1mVolMax5',
                9: 'CycleLengthMax', 10: 'CycleLengthPerBar', 11: 'CycleAmplitudePerBar', 12: 'CycleAmplitudeMax'
            },
            'Signal30m': {
                1: '30mSignal', 2: '30mSignalChoice', 3: '30mSignalTimes'
            },
            'Signal120m': {
                1: '120mSignal', 2: '120mSignalChoice', 3: '120mSignalTimes'
            },
            'SignalDaily': {
                1: 'Daily1mVolMax1', 2: 'Daily1mVolMax5', 3: 'Daily1mVolMax15', 4: 'VolDailyEmaParser'
            }
        }

        # 获取保存路径并保存为JSON文件
        columns_path = StockDataPath.columns_name_path()
        with open(f'{columns_path}/StockColumns.json', 'w') as f:
            json.dump(par_dic, f, indent=4)  # 加入缩进以便于阅读

        print(par_dic)
        return par_dic


def rename_and_merge_csv_files(folder_path: str):
    """
    遍历指定目录及其子目录，将所有 .csv.csv 文件重命名为 .csv。
    如果目标文件已存在，则将两个文件内容合并（基于去重）。

    参数:
        folder_path (str): 根目录路径。
    """
    for root, _, files in os.walk(folder_path):
        for file in files:
            # 检查文件是否以 '.csv.csv' 结尾
            if file.endswith('.csv.csv'):
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, file.replace('.csv.csv', '.csv'))

                if os.path.exists(new_path):
                    # 合并两个文件的内容
                    print(f"Merging: {old_path} -> {new_path}")

                    # 读取两个文件
                    old_data = pd.read_csv(old_path)
                    existing_data = pd.read_csv(new_path)

                    # 合并数据并去重
                    combined_data = pd.concat([existing_data, old_data]).drop_duplicates()

                    # 保存合并后的文件
                    combined_data.to_csv(new_path, index=False)

                    # 删除旧文件
                    os.remove(old_path)
                else:
                    # 重命名文件
                    os.rename(old_path, new_path)
                    print(f"Renamed: {old_path} -> {new_path}")


if __name__ == '__main__':
    count = ""
