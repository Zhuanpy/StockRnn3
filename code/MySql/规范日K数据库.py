from DataBaseAction import load_tables
import pymysql
from code.RnnDataFile.password import sql_password
from DataBaseStockDataDaily import StockDataDaily
from DataBaseStockData1m import StockData1m


def my_cursor(database: str):
    w = sql_password()
    cur = pymysql.connect(host='localhost', user='root', password=w, database=database, charset='utf8', autocommit=True)
    cursor = cur.cursor()

    return cur, cursor


def rename_daily_table_name():
    """ 重新命名 日K 数据表格名字 """

    database = 'stock_daily_data'
    tables = load_tables(database)

    # 生成重命名表格的SQL语句
    rename_statements = []

    for old_table_name in tables:

        if len(old_table_name) <= 6:
            continue

        if old_table_name[:2] == 'ZS':  # 去除大盘数据
            continue

        new_table_name = old_table_name[-6:]
        rename_statement = f"RENAME TABLE `{old_table_name}` TO `{new_table_name}`;"
        rename_statements.append(rename_statement)

    # 执行重命名语句
    w = sql_password()
    cur = pymysql.connect(host='localhost', user='root', password=w, database=database, charset='utf8', autocommit=True)
    try:
        with cur.cursor() as cursor:
            for statement in rename_statements:
                cursor.execute(statement)

    finally:
        cur.close()


def return_sql_duplicates(db: str, tb: str):
    # 查询重复日期记录
    sql_ = f'''
                   SELECT date, COUNT(*) AS count
                   FROM `{db}`.`{tb}` 
                   GROUP BY date
                   HAVING COUNT(*) > 1
               '''
    return sql_


def return_sql_add_model_run_colums(db: str, tb: str):
    sql_ = f""" ALTER TABLE {db}.{tb} 
            ADD COLUMN Trends INTEGER DEFAULT 1,
            ADD COLUMN SignalTimes TEXT,
            ADD COLUMN SignalStartTime TEXT,
            ADD COLUMN ReTrend INTEGER DEFAULT 1,

            ADD COLUMN CycleAmplitudePerBar REAL DEFAULT 0.0,
            ADD COLUMN CycleAmplitudeMax REAL DEFAULT 0.0,
            ADD COLUMN Cycle1mVolMax1 INTEGER DEFAULT 0,
            ADD COLUMN Cycle1mVolMax5 INTEGER DEFAULT 0,
            ADD COLUMN CycleLengthPerBar INTEGER DEFAULT 0,

            ADD COLUMN PredictCycleLength INTEGER DEFAULT 0,
            ADD COLUMN PredictCycleChange REAL DEFAULT 0.0,
            ADD COLUMN PredictCyclePrice REAL DEFAULT 0.0,
            ADD COLUMN PredictBarChange REAL DEFAULT 0.0,
            ADD COLUMN PredictBarPrice REAL DEFAULT 0.0,
            ADD COLUMN PredictBarVolume INTEGER DEFAULT 0,
            ADD COLUMN ScoreRnnModel REAL DEFAULT 0.0,
            ADD COLUMN ScoreBoardBoll REAL DEFAULT 0.0,
            ADD COLUMN ScoreBoardMoney REAL DEFAULT 0.0,
            ADD COLUMN ScoreBoardHot REAL DEFAULT 0.0,
            ADD COLUMN ScoreFundsAwkward REAL DEFAULT 0.0,
            ADD COLUMN TrendProbability REAL DEFAULT 0.0,
            ADD COLUMN RnnModelScore REAL DEFAULT 0.0,
            ADD COLUMN CycleAmplitude REAL DEFAULT 0.0,
            ADD COLUMN Position INTEGER DEFAULT 1,  
            ADD COLUMN PositionNum REAL DEFAULT 0.0,
            ADD COLUMN StopLoss REAL DEFAULT 0.0; """
    return sql_


def drop_duplicate_and_reset_date2id_():
    database = 'datadaily'
    table_names = load_tables(database)
    cur, cursor = my_cursor(database)

    # 遍历每个表格
    for table_name in table_names:
        table_name = table_name.lower()

        daily_data = StockDataDaily.load_daily_data(table_name)
        daily_data_shape = daily_data.shape[0]
        drop_duplicates_daily_data = daily_data.drop_duplicates(subset=['date']).reset_index(drop=True)
        drop_duplicates_shape = drop_duplicates_daily_data.shape[0]

        if daily_data_shape != drop_duplicates_shape:
            StockDataDaily.replace_daily_data(table_name, drop_duplicates_daily_data)
            print(f"Table {table_name} processed drop duplicates successfully\n")

        try:

            sql_ = f"""
                    ALTER TABLE `{database}`.`{table_name}` 
                    CHANGE COLUMN `date` `date` DATE NOT NULL ,
                    ADD PRIMARY KEY (`date`);
                    ;
                    """

            cursor.execute(sql_)
            cur.close()
            print(f"Table {table_name} processed successfully\n")

        except Exception as e:
            print(f"reset date to id {table_name} error: {str(e)}")


def add_model_run_colums():
    # TODO 将每天策略运行的数据保存到日K 数据，所有要给日K数据表格增加每日统计的列 ；

    # 1. 搞清楚，要添加哪些列 ；
    # 2. 给每个表格添加列；
    database = 'datadaily'
    table_names = load_tables(database)

    cur, cursor = my_cursor(database)

    # 遍历每个表格
    for table_name in table_names:
        sql_ = f"""
                ALTER TABLE `{database}`.`{table_name}` 
                CHANGE COLUMN `date` `date` DATE NOT NULL ,
                ADD PRIMARY KEY (`date`);
                ;
                """

        try:

            with cur.cursor() as cursor:
                cursor.execute(sql_)
            # 提交事务
            print(f"Columns added to {table_name}")

        except Exception as e:
            print(f"Error adding columns to {table_name}: {str(e)}")
            # break

    # 关闭连接
    cur.close()


""" 猜想及验证：
1. 猜想： 表格中，如果添加已经存在的date进去会怎样？ 报错 还是替换？
2. 场景1， 如果下载了一个月的数据，有的日期有，有的日期确实，此时保存数据会出现怎样的结果
验证：
拿一个数据来验证
"""

from code.Normal import ResampleData
import pandas as pd


def complete_daily_data(stock: str):
    data_1m = StockData1m.load_1m(stock, '2024')
    daily_data = ResampleData.resample_1m_data(data_1m, 'daily')
    date = '2024-01-30'
    daily_data = daily_data[daily_data['date'] == pd.to_datetime(date).date()]
    StockDataDaily.append_daily_data(stock, daily_data)

    # 保存一个数据试试结果
    print(daily_data)


if __name__ == "__main__":
    stock_code = "000001"
    complete_daily_data(stock_code)
