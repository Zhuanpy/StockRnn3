import os
from code.MySql.DB_MySql import MysqlAlchemy as mysql
from root_ import file_root
import pandas as pd


def save_1m_to_csv(df, stock_code: str):
    _path = file_root()
    # 提取日期信息
    df['month'] = df['date'].dt.to_period('M')

    # 遍历每个月份
    for month in df['month'].unique():
        # 创建每个月份的文件夹
        month_folder = os.path.join(_path, 'data', 'RnnData', f'{month}', '1m')

        if not os.path.exists(month_folder):  # 如果月份不存在建立文件夹
            os.makedirs(month_folder)

        # 选择当前月份的数据
        month_data = df[df['month'] == month]
        month_data = month_data.drop(columns=['month'])

        # 保存数据
        file_name = f'{stock_code}.csv'
        file_path = os.path.join(month_folder, file_name)

        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            # 将新数据追加到原始数据中，并删除重复数据
            combined_data = pd.concat([existing_data, month_data]).drop_duplicates()
            combined_data.to_csv(file_path, index=False)

        else:
            month_data.to_csv(file_path, index=False)


if __name__ == '__main__':
    db = 'data1m2024'
    tb = '000001'
    data = mysql.pd_read(db, tb)
    save_1m_to_csv(data, tb)
