import time
import pandas as pd
from App.my_code.MySql.DataBaseStockPool import TableStockPoolCount


def get_times():

    """
    get time
    """
    str_time = time.strftime('%Y{}%m{}%d{} %X')
    str_time = str_time.format('年', '月', '日')
    return str_time


def get_trends_data(num=30):

    """
    get trends code_data;
    """

    data = TableStockPoolCount.load_poolCount()
    data = data.tail(num).reset_index(drop=True)
    data['date'] = pd.to_datetime(data['date']).dt.strftime('%d%b')
    # print(code_data)
    # exit()
    trends_stock = (list(data['date']),
                    list(data['Up']),
                    list(data['Down']))  # stock trends

    re_trends_stock = (list(data['date']),
                       list(data['Up']),
                       list(data['ReUp']),
                       list(data['Down']),
                       list(data['ReDown']))  # stock re trends

    # print(re_trends_stock)
    trends_position = (list(data['date']),
                       list(data['_up']),
                       list(data['up_']),
                       list(data['_down']),
                       list(data['down_']))

    trends_stock_count = (
        list(data['date']), list(data['Up1']), list(data['Up2']), list(data['Up3']), list(data['Down1']),
        list(data['Down2']), list(data['Down3']))

    board_trends_count = (list(data['date']), list(data['_BoardUp']), list(data['BoardUp_']), list(data['_BoardDown']),
                          list(data['BoardDown_']),)

    r = (trends_stock, re_trends_stock, trends_position, trends_stock_count, board_trends_count)

    return r


if __name__ == '__main__':

    data_ = get_trends_data()


    print(data_[0])
    print(data_[1])
    print(data_[2])
