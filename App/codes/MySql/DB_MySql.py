import pymysql
from sqlalchemy.orm import sessionmaker
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, DateTime, text
from sqlalchemy import inspect
from config import Config

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 5000)


def sql_cursor(database: str):
    w = Config.get_sql_password()
    connection = pymysql.connect(
        host=Config.DB_CONFIG['host'],
        user=Config.DB_CONFIG['user'],
        password=w,
        database=database,
        charset=Config.DB_CONFIG['charset'],
        autocommit=True
    )
    cursor = connection.cursor()
    return connection, cursor


def execute_sql(database: str, sql: str, params: tuple = None):
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
            if params is None:
                cursor.execute(sql)

            else:
                cursor.execute(sql, params)

            return cursor.fetchall()

    except Exception as e:
        print(f"Error updating record: {e}")
        return None


def execute_sql_return_value(database: str, sql: str, params: tuple):
    """
    执行SQL语句并返回执行结果。

    参数:
    database (str): 数据库名称或路径。
    sql (str): 要执行的SQL查询语句。
    params (tuple): SQL查询中的参数，使用元组传递。

    返回:
    code_data: SQL查询的执行结果，通常是受影响的行数或查询的结果集。

    示例:
    result = execute_sql_return_value('my_database.db', 'SELECT * FROM users WHERE id = ?', (user_id,))
    """

    connection, cursor = sql_cursor(database)
    data = cursor.execute(sql, params)
    return data


def pandas_conn(database: str):
    w = Config.get_sql_password()
    conn = f"mysql+pymysql://{Config.DB_CONFIG['user']}:{w}@{Config.DB_CONFIG['host']}:3306/{database}?charset={Config.DB_CONFIG['charset']}"
    return conn


def my_engine(database: str):
    conn = pandas_conn(database)
    engine = create_engine(conn)
    return engine


def pandas_create_session(database: str):
    conn = pandas_conn(database)
    engine = create_engine(conn)
    DbSession = sessionmaker(bind=engine)
    session = DbSession()
    return session


def create_stock_table(database: str, table_name: str):
    metadata = MetaData()
    conn = pandas_conn(database)
    engine = create_engine(conn)

    # 'date', 'open', 'close', 'high', 'low', 'volume', 'money'
    table = Table(
        table_name, metadata,
        Column('date', DateTime, primary_key=True),  # 列 "A" 作为主键，但不自动递增
        Column('open', Float),
        Column('close', Float),
        Column('high', Float),
        Column('low', Float),
        Column('volume', Integer),
        Column('money', Integer),
        # 你可以根据 DataFrame 的结构添加更多列
    )

    # 使用 inspect() 检查表格是否存在
    inspector = inspect(engine)
    # 检查表格是否存在
    if not inspector.has_table(table_name):
        # 如果表格不存在，则创建
        metadata.create_all(engine)
        print(f"表格 {table_name} 已创建。")

    else:
        print(f"表格 {table_name} 已存在，将数据写入表格。")

    return None


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


def upsert_dataframe_to_mysql(df: pd.DataFrame, database: str, table_name: str, primary_key: str):
    """
    将 DataFrame 数据插入到 MySQL 数据库中，如果主键冲突则更新相应的记录。

    参数:
    - df: 需要插入或更新的 DataFrame 对象
    - table_name: MySQL 中的目标表名
    - primary_key: 主键列的列名
    - db_config: 数据库连接配置字典，包含 'user', 'password', 'host', 'port', 'database' 键

    """

    # 创建数据库连接引擎
    engine = my_engine(database)

    # 获取 DataFrame 中的列名
    columns = df.columns.tolist()

    # 构建 INSERT 语句及 ON DUPLICATE KEY UPDATE 部分
    insert_stmt = text(f"""
        INSERT INTO `{table_name}` ({', '.join(columns)})
        VALUES ({', '.join([f':{col}' for col in columns])})
        ON DUPLICATE KEY UPDATE
        {', '.join([f'{col} = VALUES({col})' for col in columns if col != primary_key])};
    """)

    # 使用 SQLAlchemy 的连接执行语句
    with engine.connect() as conn:

        for index, row in df.iterrows():
            conn.execute(insert_stmt, {col: row[col] for col in columns})

    print("数据成功写入 MySQL 数据库，并在主键冲突时进行了更新。")


if __name__ == '__main__':
    # data1m2022.`000001`
    alc = MysqlAlchemy()
    data_ = alc.pd_read(database='data1m2022', table='000001')
    print(data_)
