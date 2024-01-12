from file_path import *


class StockDataPath:

    @classmethod
    def monitor_1m_data_path(cls, stock_code):
        r = os.path.join(data_path, 'input', 'monitor', f'{stock_code}.csv')
        return r

    @classmethod
    def json_data_path(cls, month_parser: str, stock_code: str):
        r = os.path.join(data_path, 'RnnData', month_parser, 'json', f'{stock_code}.json')
        return r

    @classmethod
    def model_path(cls, month_parser: str, file_name: str):
        r = os.path.join(data_path, 'RnnData', month_parser, 'model', file_name)
        return r

    @classmethod
    def model_weight_path(cls, month_parser: str, file_name: str):
        r = os.path.join(data_path, 'RnnData', month_parser, 'weight', file_name)
        return r

    @classmethod
    def columns_name_path(cls):
        r = os.path.join(data_path, 'columns')
        return r


class AnalysisDataPath:

    @classmethod
    def analysis_industry_trend_jpg_path(cls, file_name):
        r = os.path.join(data_path, 'output', 'analysis', file_name)
        return r

    @classmethod
    def macd_train_path(cls, signal_file: str, file_name: str):
        r = os.path.join(data_path, 'output', 'MacdTrend', 'train', signal_file, file_name)
        return r

    @classmethod
    def macd_predict_path(cls, file_name: str):
        r = os.path.join(data_path, 'output', 'MacdTrend', 'predict', file_name)
        return r

    @classmethod
    def macd_predict_trends_path(cls, file_name: str):
        r = os.path.join(data_path, 'output', 'MacdTrend', 'predict', 'trends', file_name)
        return r

    @classmethod
    def macd_model_path(cls, file_h5: str):
        r = os.path.join(data_path, 'output', 'MacdTrend', file_h5)
        return r
