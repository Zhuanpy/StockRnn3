import os
from App.my_code.MySql.DB_MySql import MysqlAlchemy as mysql
from App.my_code.utils.Normal import ResampleData
from App.my_code.MySql.DB_MySql import MysqlAlchemy
import pandas as pd
from App.my_code.RnnDataFile.stock_path import StockDataPath
from App.my_code.MySql.DataBaseStockData1m import StockData1m


def save_1m_to_mysql(stock_code: str, year: str, data):
    StockData1m.append_1m(stock_code, year, data)
    return True


def save_1m_to_csv(df, stock_code: str):

    """
    将按分钟级别的股票数据保存为每月单独的 CSV 文件。

    参数:
        df (pd.DataFrame): 包含股票数据的 DataFrame，需包含 'date' 列。
        stock_code (str): 股票代码，用于文件命名。
    """

    # 确保 'date' 列为 datetime 类型

    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])

    # 添加 'month' 列表示所属月份
    df['month'] = df['date'].dt.to_period('M')

    # 按月份分组并保存
    for month, month_data in df.groupby('month'):
        # 构造文件路径
        file_name = f'{stock_code}.csv'
        file_path = StockDataPath.month_1m_data_path(str(month))

        # 确保文件夹存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        if os.path.exists(file_path):
            # 如果文件存在，读取并合并数据
            existing_data = pd.read_csv(file_path+'/'+file_name)
            combined_data = pd.concat([existing_data, month_data.drop(columns=['month'])]).drop_duplicates()
        else:
            # 如果文件不存在，直接使用当前月数据
            combined_data = month_data.drop(columns=['month'])

        # 保存到文件
        combined_data.to_csv(file_path+'/'+file_name, index=False)


def save_1m_to_daily(df, stock_code: str):
    df_daily = ResampleData.resample_1m_data(df, 'd')
    database = 'datadaily'
    table = stock_code
    MysqlAlchemy.pd_append(df_daily, database, table)
    return True


if __name__ == '__main__':
    db = 'data1m2024'
    tb = '000001'
    data = mysql.pd_read(db, tb)
    save_1m_to_csv(data, tb)
