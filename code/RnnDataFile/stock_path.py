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
        r = os.path.join(data_path, 'RnnData', month_parser, 'json', file_name)
        return r

    @classmethod
    def model_weight_path(cls, month_parser: str, file_name: str):
        r = os.path.join(data_path, 'RnnData', month_parser, 'weight', file_name)
