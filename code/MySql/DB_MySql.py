import pymysql
from code.RnnDataFile.password import sql_password
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 5000)


def sql_cursor(database: str):
    w = sql_password()
    connection = pymysql.connect(host='localhost', user='root', password=w, database=database, charset='utf8',
                                 autocommit=True)
    cursor = connection.cursor()
    return connection, cursor


def execute_sql(database: str, sql: str, params: tuple):
    """
    执行 SQL 查询或更新操作。

    参数:
    - database (str): 数据库名称，指定要在其中执行 SQL 查询的数据库。
    - sql (str): 包含 SQL 查询的字符串。这是你希望执行的 SQL 语句，可以是查询、更新、删除等。
    - params (tuple): 包含要传递给 SQL 查询中占位符的参数。占位符的数量和类型应与 params 中的元素相匹配。

    返回:
    - str: 操作成功的消息，或者在发生错误时返回相应的错误信息

    """

    try:
        connection, cursor = sql_cursor(database)

        with connection, cursor:
            cursor.execute(sql, params)

    except Exception as e:
        print(f"Error updating record: {e}")

    return "Update successful"


def execute_sql_return_value(database: str, sql: str, params: tuple):
    # sql1 = f'''select * from {db}.`{self.stock_code}`
    # where date in (select max(date) from {db}.`{self.stock_code}`);'''
    connection, cursor = sql_cursor(database)
    data = cursor.execute(sql, params)

    return data


def pandas_conn(database: str):
    w = sql_password()
    conn = f'mysql+pymysql://root:{w}@localhost:3306/{database}?charset=utf8'
    return conn


def pandas_create_session(database: str):
    conn = pandas_conn(database)
    engine = create_engine(conn)
    DbSession = sessionmaker(bind=engine)
    session = DbSession()
    return session


class MysqlAlchemy:

    @classmethod
    def pd_read(cls, database: str, table: str):
        conn = pandas_conn(database)
        sql = f'SELECT * FROM {database}.{table};'
        d = pd.read_sql(sql=sql, con=conn)  # 读取SQL数据库中数据;
        return d

    @classmethod
    def pd_append(cls, data, database: str, table: str):
        conn = pandas_conn(database)
        data.to_sql(table, con=conn, if_exists='append', index=False, chunksize=None, dtype=None)

    @classmethod
    def pd_replace(cls, data, database: str, table: str):
        conn = pandas_conn(database)
        data.to_sql(table, con=conn, if_exists='replace', index=False, chunksize=None, dtype=None)


if __name__ == '__main__':
    # MysqlAlchemy .;
    path = sql_password()
    print(path)
    alc = MysqlAlchemy()

    data_ = alc.pd_read(database='stock_basic_information', table='record_stock_minute')
    print(data_)
