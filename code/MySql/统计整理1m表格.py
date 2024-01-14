import pandas as pd
from LoadMysql import LoadFundsAwkward
from LoadMysql import StockData1m as s1
from LoadMysql import LoadBasicInform as lm


def correction_date_1m_table():
    """
    1分钟数据，日期记录有误时，通过遍历每个表格，再次记录
    """

    # 读取1m数据
    # 获取最后一天的数据
    # 更新1m表格

    table1m = lm.load_minute()
    table1m['EndDate'] = pd.to_datetime(table1m['EndDate'])
    table1m = table1m[table1m['EndDate'] > pd.to_datetime('2022-01-01')]
    table1m = table1m[table1m['EndDate'] < pd.to_datetime('2050-01-01')]

    table1m = table1m.sort_values(by=['EndDate'])

    i = 0

    for _, row in table1m.iterrows():  # table1m.index:
        id_ = row['id']
        code = row['code']
        name = row['name']
        record_end = row['EndDate'].date()

        if i % 10 == 0:
            print(i)

        # 读取1m表格
        data_1m = s1.load_1m(code_=code, _year='2022')

        data_1m['date'] = pd.to_datetime(data_1m['date'])
        data_1m = data_1m.sort_values(by='date')
        _shape = data_1m.shape

        data_1m = data_1m.drop_duplicates(subset=['date'])

        shape_ = data_1m.shape
        end_date = data_1m.iloc[-1]['date'].date()

        if end_date != record_end:
            sql1 = f'EndDate = %s where id = %s;'
            params = (end_date, id_)
            lm.set_table_minute_record(sql1, params)
            print(f'{name}, {code}: {sql1}')

        if _shape != shape_:
            # 替换表格
            s1.replace_1m(code_=code, year_='2022', data=data_1m)
            print(f'{name}, {code}: 更新了数据')

        i = i + 1


def awkward_data():
    df = LoadFundsAwkward.load_awkwardNormalization()
    return df


# SELECT * FROM stock_basic_information.record_stock_minute;

if __name__ == "__main__":
    data = lm.load_minute()
    # data = awkward_data()
    # data = data.sort_values(by=['Date', 'count']).tail(50)
    # print(data)
    # correction_date_1m_table()
