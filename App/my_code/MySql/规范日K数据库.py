from DataBaseAction import load_tables
import pymysql
from DataBaseStockDataDaily import StockDataDaily


def my_cursor(database: str):
    # 数据库配置
    # w = sql_password()
    cur = pymysql.connect(host='localhost', user='root', password="651748264Zz", database=database, charset='utf8',
                          autocommit=True)
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

    cur = pymysql.connect(host='localhost', user='root', password="651748264Zz", database=database, charset='utf8',
                          autocommit=True)
    try:
        with cur.cursor() as cursor:
            for statement in rename_statements:
                cursor.execute(statement)

    finally:
        cur.close()


def return_sql_duplicates(db: str, tb: str):
    # 查询重复日期记录
    sql_ = f"""
    SELECT date, COUNT(*) AS count FROM `{db}`.`{tb}` GROUP BY date HAVING COUNT(*) > 1
            """
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


def complete_daily_data(stock: str):
    daily_sq = StockDataDaily.load_daily_data(stock)
    daily_sq = daily_sq[['date', 'open', 'close', 'high', 'low', 'volume', 'money']]
    print(daily_sq.head(5))


def return_connection(database="datadaily"):
    # 数据库配置
    db_config = {
        'host': 'localhost',  # 数据库地址
        'user': 'root',  # 用户名
        'password': '651748264Zz',  # 密码
        'database': database,  # 数据库名
        'charset': 'utf8mb4'
    }

    connection = pymysql.connect(**db_config)
    return connection


def rename_columns_in_tables( columns_to_rename: dict):

    """"
    parameters:
    columns_to_rename: dict, 格式如下：
        columns_to_rename = {
        'SignalTimes': {'new_name': 'signal_times', 'data_type': 'INT NULL'},
        'SignalStartTime': {'new_name': 'signal_start_time', 'data_type': 'TEXT NULL'},
        'ReTrend': {'new_name': 're_trend', 'data_type': 'INT DEFAULT 1'},
    }
    """
    # 连接到数据库
    connection = return_connection()

    try:
        with connection.cursor() as cursor:
            # 获取所有表名
            cursor.execute("SHOW TABLES;")
            tables = [row[0] for row in cursor.fetchall()]

            for table in tables:
                # 获取当前表的列名
                cursor.execute(f"SHOW COLUMNS FROM `{table}`;")
                columns = [row[0] for row in cursor.fetchall()]

                # 遍历映射关系，更新列名
                for old_column, details in columns_to_rename.items():
                    if old_column in columns:
                        new_column = details['new_name']
                        data_type = details['data_type']
                        sql = f"""
                            ALTER TABLE `{table}` 
                            CHANGE `{old_column}` `{new_column}` {data_type};
                            """
                        print(f"Executing: {sql}")
                        cursor.execute(sql)

            # 提交更改
            connection.commit()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()


if __name__ == "__main__":
    # 要更新的列名映射
    columns_to_rename = {
        'SignalTimes': {'new_name': 'signal_times', 'data_type': 'INT NULL'},
        'SignalStartTime': {'new_name': 'signal_start_time', 'data_type': 'TEXT NULL'},
        'ReTrend': {'new_name': 're_trend', 'data_type': 'INT DEFAULT 1'},
    }

    rename_columns_in_tables(columns_to_rename)
