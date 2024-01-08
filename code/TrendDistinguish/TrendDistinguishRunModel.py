import numpy as np
from keras.models import load_model
from keras import backend as k

from Distinguish_utils import array_data, calculate_distinguish_data
import imageio
from root_ import file_root
import os


class TrendDistinguishModel:
    """
    趋势识别模型
    变量： 下跌前期：_down， 下跌后期: down_， 上涨前期:_up，上涨后期: up_；
    """

    def __init__(self):

        self.root = file_root()

        self.trend_path = os.path.join(self.root, 'data', 'output', 'MacdTrend')

        self.values = {0: '_down', 1: 'down_', 2: '_up', 3: 'up_'}
        self.labels = {'_down': 0, 'down_': 1, '_up': 2, 'up_': 3}

    def predictive_value(self, stock_code):

        """
        模型预估，return value & label ;
        """
        load_path = os.path.join(self.trend_path, 'predict', f'{stock_code}.jpg')
        img = imageio.imread(load_path)
        img.shape = (1, img.shape[0], img.shape[1], img.shape[2])

        k.clear_session()
        model_path = os.path.join(self.trend_path, 'model.h5')
        model = load_model(model_path)

        value = model.predict(img)

        value_ = int(np.argmax(value[0]))
        label = self.values[value_]

        img = img.reshape(img.shape[1], img.shape[2], img.shape[3])

        save_path = os.path.join(self.trend_path, 'predict', 'trends', f'{label}_{stock_code}.jpg')
        imageio.imsave(save_path, img)

        result = (label, value_)

        return result

    def distinguish_1m(self, stock_code: str, freq: str, date_, returnFreq=False):

        """
        预估 1m 数据
        """
        data = calculate_distinguish_data(stock_code, freq, date_=date_)

        fig_name = f'{self.trend_path}/predict/{stock_code}.jpg'
        array_data(data=data, name_=fig_name)  # , showTicks=True)

        label_, value_ = self.predictive_value(stock_code)

        if returnFreq:
            result = data, (label_, value_)

        else:
            result = (label_, value_)

        return result

    def distinguish_freq(self, stock_code, data):
        data = data.tail(100).reset_index(drop=True)
        fig_name = f'{self.trend_path}/predict/{stock_code}.jpg'
        array_data(data=data, name_=fig_name)
        label_, value_ = self.predictive_value(stock_code)
        result = (label_, value_)
        return result


if __name__ == '__main__':

    stock = 'BK0465'

    for i in range(16):
        i = i + 1
        date_ = f'2022-11-{i}'
        dis = TrendDistinguishModel()
        l, v = dis.distinguish_1m(stock_code=stock, returnFreq=False, freq='120m', date_=date_)

        print(date_)
        print(l, v)
