import os
from code.MySql.DB_MySql import MysqlAlchemy as mysql
from code.Normal import ResampleData
from code.MySql.DB_MySql import MysqlAlchemy
import pandas as pd
from code.RnnDataFile.stock_path import StockDataPath


def save_1m_to_csv(df, stock_code: str):
    # 提取日期信息
    df['month'] = df['date'].dt.to_period('M')

    # 遍历每个月份
    for month in df['month'].unique():
        # 选择当前月份的数据
        month_data = df[df['month'] == month]
        month_data = month_data.drop(columns=['month'])

        # 保存数据
        file_name = f'{stock_code}.csv'
        file_path = StockDataPath.month_1m_data_path(f'{month}', file_name)

        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            # 将新数据追加到原始数据中，并删除重复数据
            combined_data = pd.concat([existing_data, month_data]).drop_duplicates()
            combined_data.to_csv(file_path, index=False)

        else:
            month_data.to_csv(file_path, index=False)

def save_1m_to_daily(df, stock_code: str):
    df_daily = ResampleData.resample_1m_data(df, 'd')
    database = 'stock_daily_data'
    table = stock_code
    MysqlAlchemy.pd_append(df_daily, database, table)
    return True


if __name__ == '__main__':
    db = 'data1m2024'
    tb = '000001'
    data = mysql.pd_read(db, tb)
    save_1m_to_csv(data, tb)
