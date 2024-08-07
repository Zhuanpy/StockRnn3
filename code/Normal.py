# -*- coding: utf-8 -*-
import os
import smtplib
import time
from email.message import Message
import pandas as pd
from scipy import stats
import numpy as np
import json
from code.RnnDataFile.stock_path import StockDataPath

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
    def resample_fun(cls, data, parameter):
        data['index_date'] = data['date']

        data = data.set_index('index_date')

        # 使用 resample 函数按指定的频率对数据进行重采样
        resampled = data.resample(parameter, closed='right', label='right').agg({
            'open': 'first',
            'close': 'last',
            'high': 'max',
            'low': 'min',
            'volume': 'sum',
            'money': 'sum'
        })

        return resampled[['date', 'open', 'close', 'high', 'low', 'volume', 'money']]

    @classmethod
    def _resample_60m_data(cls, data: pd.DataFrame) -> pd.DataFrame:
        # 增加 minute_time 列
        data['minute_time'] = data['date'].dt.time

        # 上午和下午分割数据
        morning_data = data[data['minute_time'] < pd.to_datetime('12:00:00').time()]
        afternoon_data = data[data['minute_time'] >= pd.to_datetime('12:00:00').time()]

        # 重新采样
        morning_data = cls.resample_fun(morning_data, parameter='90T')
        afternoon_data = cls.resample_fun(afternoon_data, parameter='60T')

        # 合并并排序
        resampled_data = pd.concat([morning_data, afternoon_data]).sort_values(by='date').reset_index(drop=True)
        return resampled_data

    @classmethod
    def resample_1m_data(cls, data: pd.DataFrame, freq: str) -> pd.DataFrame:
        # 定义时间映射
        time_mappings = {
            '15m': '15T',
            '30m': '30T',
            '120m': '360T',
            '60m': None,  # 特殊处理60分钟的频率
            'day': '1440T',
            'daily': '1440T',
            'd': '1440T',
            'D': '1440T'
        }

        if freq in time_mappings:

            # 处理常规时间频率
            if freq != '60m':
                data = cls.resample_fun(data=data, parameter=time_mappings[freq])

            else:
                # 特殊处理60分钟的频率
                data = cls._resample_60m_data(data)
        else:
            raise ValueError(f"Unsupported frequency: {freq}")

        return data


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


if __name__ == '__main__':
    count = ""
