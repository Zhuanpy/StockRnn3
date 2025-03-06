import os
from App.static import file_root


class StockDataPath:
    data_path = os.path.join(file_root(), 'data')

    rnn_data_file = 'RnnData'

    @classmethod
    def monitor_1m_data_path(cls, stock_code):
        r = os.path.join(cls.data_path, 'input', 'monitor', f'{stock_code}.csv')
        return r

    @classmethod
    def json_data_path(cls, month_parser: str, stock_code: str):
        r = os.path.join(cls.data_path, cls.rnn_data_file, month_parser, 'json', f'{stock_code}.json')
        return r

    @classmethod
    def model_path(cls, month_parser: str, file_name: str):
        r = os.path.join(cls.data_path, cls.rnn_data_file, month_parser, 'model', file_name)
        return r

    @classmethod
    def model_weight_path(cls, month_parser: str, file_name: str):
        r = os.path.join(cls.data_path, cls.rnn_data_file, month_parser, 'weight', file_name)
        return r

    @classmethod
    def columns_name_path(cls):
        r = os.path.join(cls.data_path, 'columns')
        return r

    @classmethod
    def month_1m_data_path(cls, month_parser: str):
        r = os.path.join(cls.data_path, cls.rnn_data_file, month_parser, '1m')
        return r

    @classmethod
    def train_data_path(cls, month_parser: str, file_name: str):
        r = os.path.join(cls.data_path, cls.rnn_data_file, month_parser, 'train_data', file_name)
        return r

    @classmethod
    def rnnData_folder_path(cls):
        r = os.path.join(cls.data_path, cls.rnn_data_file)  # os.path.join(file_root(), 'data', 'RnnData')
        return r


class AnalysisDataPath:
    data_path = os.path.join(file_root(), 'data')

    @classmethod
    def analysis_industry_trend_jpg_path(cls, file_name):
        """ 行业趋势图片路径 """
        r = os.path.join(cls.data_path, 'output', 'analysis', file_name)
        return r

    @classmethod
    def macd_train_path(cls, signal_file: str, file_name: str):
        r = os.path.join(cls.data_path, 'output', 'MacdTrend', 'train', signal_file, file_name)
        return r

    @classmethod
    def macd_predict_path(cls, file_name: str):
        r = os.path.join(cls.data_path, 'output', 'MacdTrend', 'predict', file_name)
        return r

    @classmethod
    def macd_predict_trends_path(cls, file_name: str):
        r = os.path.join(cls.data_path, 'output', 'MacdTrend', 'predict', 'trends', file_name)
        return r

    @classmethod
    def macd_model_path(cls, file_h5: str):
        r = os.path.join(cls.data_path, 'output', 'MacdTrend', file_h5)
        return r


if __name__ == '__main__':
    p = StockDataPath()
    print(p.month_1m_data_path('2022-01'))
