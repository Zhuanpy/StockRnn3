from stock_path import StockDataPath
import json
import os
from root_ import file_root


class LoadJsonData:

    @classmethod
    def loadJsonData(cls, month: str, stock_code: str):
        # 读取json文件
        path = StockDataPath.json_data_path(month, stock_code)

        with open(path, 'r', encoding='utf-8') as f:
            jsons = json.load(f)
        return jsons

    @classmethod
    def pre_month_json_folder_list(cls, month: str, ) -> tuple:
        """
        获取以前月份列表
        :param month: 月份
        :class_file: 文件夹类型 ， 如 weigh , train_data ;
        :return: 上个月份列表

        获取RNN 文件夹名， 大到小并且排序；
        能用到的地方， 训练模型读取历史数据时，例如权重数据，例如训练数据；

        """

        root_path = os.path.join(file_root(), 'data', 'RnnData')

        # 获取RnnData文件夹下全部月份文件夹名称
        folder_names = sorted(
            [folder for folder in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, folder))],
            reverse=True)

        # 删除CommonFile文件夹
        folder_names.remove('CommonFile')

        # 移除当前月份及以后月份的文件夹
        folder_names = folder_names[folder_names.index(month) + 1:]

        # 构建文件夹路径列表
        folder_path = [os.path.join(root_path, M, 'json') for M in folder_names]

        return folder_path, folder_names

    @classmethod
    def find_json_parser_by_month_folder(cls, month: str, stock_code: str):
        """ 找出输入月份的上一个历史数据文件夹名称及月份名称.
             Parameters:
                 month (str): 输入月份；
                 stock_code (str): 股票名称文件名称；

             Returns:
                 json data: json村出纳的参数.
                 json data month ： 文件所在文件夹月份名称.
           """

        folder_paths, month_list = cls.pre_month_json_folder_list(month)

        for folder_path, M in zip(folder_paths, month_list):

            folder_path = os.path.join(folder_path, f'{stock_code}.json')

            if os.path.exists(folder_path) and os.path.isfile(folder_path):
                jsons = cls.loadJsonData(M, stock_code)  # 如果找到第一个存在的路径，立即返回并结束循环

                return jsons, M

        return False, False


def save_json(new_data: dict, parser_month: str, stock_code: str):

    """ 保存新的json数据.
             Parameters:
                 new_data (dict): 新的json数据；
                 parser_month (str): 文件所在文件夹月份名称；
                 stock_code (str): 股票名称文件名称；
           """

    path = StockDataPath.json_data_path(parser_month, stock_code)
    with open(path, 'w') as f:
        json.dump(new_data, f)


if __name__ == '__main__':
    stock = '000001'
    parser_month = '2023-12'
    json_parser, parser_month = LoadJsonData.find_json_parser_by_month_folder(parser_month, stock)

    print(json_parser['DailyVolEma'])
    print(parser_month)
