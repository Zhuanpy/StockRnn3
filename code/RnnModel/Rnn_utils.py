import pandas as pd
from code.MySql.LoadMysql import LoadRnnModel, StockData1m
from code.Normal import ResampleData
import os
from root_ import file_root


def reset_record_time(_date):
    time_ = (pd.to_datetime(_date) + pd.Timedelta(days=-150)).date()
    ids = LoadRnnModel.load_run_record()
    ids = tuple(ids['id'])

    sql = f'''update %s.%s
    set SignalStartTime = '%s', 
    Time15m = '%s' where id in %s;'''

    params = (LoadRnnModel.db_rnn, LoadRnnModel.tb_run_record, time_, time_, ids)
    LoadRnnModel.rnn_execute_sql(sql, params)


def reset_id_time(id_, _date):
    time_ = (pd.to_datetime(_date) + pd.Timedelta(days=-150)).date()

    sql = f'''update %s.%s set 
    SignalStartTime = '%s', 
    Time15m = '%s' where id = %s;'''

    params = (LoadRnnModel.db_rnn, LoadRnnModel.tb_run_record, time_, time_, id_)
    LoadRnnModel.rnn_execute_sql(sql, params)


def date_range(_date, date_, code_='bk0424') -> list:
    if _date == date_:
        _date = pd.to_datetime(_date).date()
        date_ = pd.to_datetime(date_) + pd.Timedelta(days=1)  # .date()
        date_ = date_.date()

    else:
        _date = pd.to_datetime(_date).date()
        date_ = pd.to_datetime(date_).date()

    data = StockData1m.load_1m(code_, _year=str(_date.year))
    data = ResampleData.resample_1m_data(data=data, freq='day').drop_duplicates(subset=['date'])
    data = data[(data['date'] >= _date) & (data['date'] <= date_)]
    data = list(data['date'])

    return data


def rnn_data_path(month: str):
    """
    获取RNN数据路径
    :param month: 月份
    :return: 数据路径
    """
    return os.path.join(file_root(), 'data', 'RnnData', month)


def pre_month_data_list(month: str, classification: str) -> list:
    """
    获取以前月份列表
    :param month: 月份
    :classification: 类型 ， 如 weigh , train_data ;
    :return: 上个月份列表

    获取RNN 文件夹名， 大到小并且排序；
    能用到的地方， 训练模型读取历史数据时，例如权重数据，例如训练数据；

    """

    root_path = os.path.join(file_root(), 'data', 'RnnData')

    folder_names = [folder for folder in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, folder))]

    folder_names.remove('CommonFile')
    folder_names.sort()
    folder_names.reverse()

    index_to_remove = folder_names.index(month)
    folder_names = folder_names[index_to_remove + 1:]

    # 再添加路径
    for m in folder_names:

        try:
            folder_names[folder_names.index(m)] = os.path.join(root_path, m, classification)

        except ValueError:
            pass  # 月份不存在于列表中，不进行任何操作

    return folder_names


def find_file_in_paths(month: str, classification: str, file_name: str):
    folder_paths = pre_month_data_list(month, classification)

    for folder_path in folder_paths:
        file_path = os.path.join(folder_path, file_name)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            return folder_path
            # 如果找到第一个存在的路径，立即返回并结束循环

    return False


if __name__ == '__main__':
    m = '2023-12'
    c = 'weight'
    f = 'weight_bar_volume_000651.h5'
    p = find_file_in_paths(m, c, f)
    print(p)
