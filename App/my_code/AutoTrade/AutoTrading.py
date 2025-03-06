import sys
from ..MySql.DataBaseStockPool import TableStockPool  # StockPoolData
from pywinauto import Application
from pywinauto.keyboard import send_keys
import pyautogui as ag
from time import sleep
import cv2
from autotrading_utils import match_screenshot
import pandas as pd
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


def clic_location(screen: str, temp: str) -> tuple:
    """
    根据模板匹配点击位置，返回点击的坐标点。

    参数:
        screen (str): 当前屏幕截图的路径。
        temp (str): 模板图片的路径。

    返回:
        tuple: 点击位置的坐标点 (x, y)。
    """

    # 读取模板图片并获取其尺寸
    temp_size = cv2.imread(temp)
    temp_size = temp_size.shape[:2]

    # 计算模板图片中心点坐标
    temp_x = int(temp_size[1] / 2)
    temp_y = int(temp_size[0] / 2)

    # 匹配模板并获取匹配结果
    result = match_screenshot(screen, temp)

    # 计算点击位置的坐标
    x1 = result[3][0] + temp_x
    y1 = result[3][1] + temp_y
    return x1, y1


def get_screenshot():
    img = ag.screenshot()
    img.save('targetfile/screenshot.jpg')
    target = 'targetfile/screenshot.jpg'
    return target


def start_trading_app():
    """
    启动交易应用程序并判断是否成功打开交易界面。

    返回:
        app_ (Application): 启动的应用程序对象。
        win_ (WindowSpecification): 交易界面的窗口对象。
    """

    r = 0
    app_, win_ = None, None
    app_path = os.path.join('E:/', 'MyApp', 'FinancialSoftware', 'TonghuashunApp', 'xiadan.exe')

    while r < 0.9:
        app_ = Application(backend='uia').start(app_path)  # backend='uia'
        win_ = app_.window(class_name="网上股票交易系统5.0")
        sleep(1)

        # 截屏判断是否打开交易平台
        # 获取当前截屏
        target = get_screenshot()
        temp = 'targetfile/loginsuccess.jpg'
        result = match_screenshot(target, temp)

        r = result[1]

        # 如果匹配大于 0.9 就判断顺利打开了
        if r > 0.9:
            print('成功打开交易平台')

        else:
            print('未能成功打开交易平台，重试中...')

    return app_, win_


class TongHuaShunAutoTrade:

    def __init__(self):

        self.app, self.win = start_trading_app()

    def sleep2stop(self, s: float = 0.1) -> bool:
        """
        根据鼠标位置决定是否停止程序并等待指定时间。

        参数:
            s (float): 等待时间，默认为 0.1 秒。

        返回:
            bool: 如果程序继续运行则返回 True，如果程序停止则不会返回（系统退出）。
        """
        x, y = ag.position()

        # 判断鼠标位置是否超过设定的范围
        if x > 1800 or y > 665:
            sys.exit()  # 系统退出

        else:
            sleep(s)  # 等待指定时间

        return True

    def buy_action(self, code_: str, num_: str, price_: str = None):

        """
        执行买入操作。

        参数:
            code_ (str): 证券代码。
            num_ (str): 买入数量。
            price_ (str, optional): 买入价格。默认值为 None。
        """

        path = r'targetfile/buy/'
        screen = r'targetfile/screenshot.jpg'

        # 点击买入界面
        tmp = f'{path}f1.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        ag.click()
        self.sleep2stop()

        # 输入证券代码
        tmp = f'{path}code.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        self.sleep2stop()
        ag.doubleClick()
        self.sleep2stop()
        send_keys(code_)
        self.sleep2stop(0.5)

        # 输入买入价格（如果有提供）
        if price_:
            tmp = f'{path}price.jpg'
            x, y = clic_location(screen, tmp)
            ag.moveTo(x, y)
            self.sleep2stop()
            ag.doubleClick()
            self.sleep2stop(0.5)

            send_keys(price_)
            self.sleep2stop(0.5)

        # 输入买入数量
        tmp = f'{path}num.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        self.sleep2stop(0.5)
        ag.doubleClick()
        self.sleep2stop()
        send_keys(num_)
        self.sleep2stop()

        # 确认买入提示
        tmp = f'{path}buy.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        self.sleep2stop(0.5)
        ag.doubleClick()
        self.sleep2stop()
        send_keys(num_)
        self.sleep2stop()

        # 确认-买入-提示
        screen = get_screenshot()  # 获取新的截图
        self.sleep2stop()
        tmp = f'{path}yes.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        self.sleep2stop()
        ag.click()
        self.sleep2stop()

        return True

    def sell_action(self, code_: str, num_: str, price_: str = None):
        """
        执行卖出操作。

        参数:
            code_ (str): 证券代码。
            num_ (str): 卖出数量。
            price_ (str, optional): 卖出价格。默认值为 None。

        返回:
            bool: 操作是否成功。如果确认卖出提示匹配成功则返回 True，否则返回 False。
        """

        path = 'targetfile/sell/'

        screen = 'targetfile/screenshot.jpg'

        # 点击卖出界面
        tmp = f'{path}f2.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        ag.click()
        self.sleep2stop()

        # 找出证券代码位置，输入证券代码
        tmp = f'{path}sellcode.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        self.sleep2stop()
        ag.doubleClick()
        self.sleep2stop()
        send_keys(code_)
        self.sleep2stop(0.5)

        # 输入卖出价格（如果有提供）
        if price_:
            tmp = f'{path}sellprice.jpg'
            x, y = clic_location(screen, tmp)
            ag.moveTo(x, y)
            self.sleep2stop()
            ag.doubleClick()
            self.sleep2stop(0.5)

            send_keys(price_)
            self.sleep2stop(0.5)

        # 输入卖出数量
        tmp = f'{path}sellnum.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        self.sleep2stop(0.5)
        ag.doubleClick()
        self.sleep2stop()
        send_keys(num_)
        self.sleep2stop()

        # 确认-卖出
        tmp = f'{path}selling.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        self.sleep2stop(0.5)
        ag.click()
        self.sleep2stop(0.5)

        # 确认-卖出-提示
        screen = get_screenshot()  # 从新获取截屏 出现新的界面
        tmp = f'{path}yes.jpg'
        x, y = clic_location(screen, tmp)
        ag.moveTo(x, y)
        self.sleep2stop(0.5)
        ag.click()
        self.sleep2stop()

        return True


class TradePoolFaker:
    """ 买入数量计算， 持股金额约 5000， 大约5000只持有一手；"""

    @classmethod
    def buy_num(cls, close: float) -> int:
        """
        根据收盘价计算可以买入的股票数量，最小为 100 股。

        参数:
            close (float): 股票的收盘价。

        返回:
            int: 可以买入的股票数量，至少为 100 股，并且为 100 的倍数。
        """

        num_ = 5000 / close

        if num_ < 100:
            num_ = 100

        if num_ > 100:
            num_ = (num_ // 100) * 100 + 100

        return int(num_)

    @classmethod
    def buy_pool(cls, score: int = -5, show_pool: bool = False) -> None:
        """
        根据给定的评分筛选股票池中的股票并执行买入操作。

        参数:
            score (int): 筛选股票的评分阈值。默认值为 -5。
            show_pool (bool): 是否显示筛选后的股票池。默认值为 False。
        """

        pool = TableStockPool.load_StockPool()
        pool = pool[['id', 'name', 'code', 'Classification', 'Industry', 'RnnModel', 'close', 'Position', 'BoardBoll']]
        pool = pool[(pool['RnnModel'] < score) &
                    (~pool['Classification'].isin(['创业板', '科创板'])) &
                    (pool['close'] < 200) &
                    (~pool['Industry'].isin(['房地产', '煤炭采选'])) &
                    (pool['Position'] == 0)  # & (pool['BoardBoll'].isin([1, 2]))
                    ].sort_values(by=['RnnModel'])

        if show_pool:
            print(pool)
            sys.exit()

        trade_ = TongHuaShunAutoTrade()
        for i in pool.index:
            code_ = pool.loc[i, 'code']
            close = pool.loc[i, 'close']
            num_ = cls.buy_num(close)
            print(f'code_:{code_}, num_:{num_}')
            price_ = None  # 价格留空，按市场价买入
            trade_.buy_action(code_, str(num_), price_)

        print(f'Buy Succeed;')

    @classmethod
    def sell_pool(cls) -> None:
        """
       根据股票池中的持仓信息执行卖出操作。

       参数:
           无
       """
        position = TableStockPool.load_StockPool()
        position = position[(position['Position'] == 1) &
                            (position['TradeMethod'] == 1)]

        print(position.head())

        #  打开交易软件
        trade_ = TongHuaShunAutoTrade()

        for index in position.index:
            code_ = position.loc[index, 'code']
            num_ = str(position.loc[index, 'PositionNum'])
            price_ = None  # 价格留空，按市场价卖出
            trade_.sell_action(code_, num_, price_)

        print(f'Sell Succeed;')


class TradePoolReal:
    """ 买入数量计算， 持股金额约 5000， 大约5000只持有一手；"""
    def __init__(self, pool_loader):
        self.pool_loader = pool_loader

    def _load_stock_data(self):
        return self.pool_loader.load_StockPool()

    def buy_num(self, close: float) -> int:
        num_ = max(100, int(5000 / close))
        num_ = (num_ // 100) * 100 + 100 if num_ > 100 else num_
        return num_

    def bottom_down_data(self):
        data_ = self._load_stock_data()
        return data_[(data_['Trends'] == -1) & (data_['RnnModel'] < -4.5)]

    def bottom_up_data(self):
        data_ = self._load_stock_data()
        return data_[(data_['Trends'] == 1) & (data_['RnnModel'] <= 1.5)]

    def position_data(self):
        data_ = self._load_stock_data()
        return data_[(data_['Position'] == 1) & (data_['TradeMethod'] <= 1)]

    def buy_pool(self):
        print(f'Buy Succeed;')
        pass

    def sell_pool(self):
        print(f'Sell Succeed;')
        pass


if __name__ == '__main__':
    code = '002475'
    num = '300'
    price = '10'

    trade = TradePoolFaker()
    trade.buy_pool(score=-4, show_pool=True)

    # >py -3,10 -m pip install pyautogui
