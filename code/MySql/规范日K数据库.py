from DataBaseAction import load_tables
import pymysql
from code.RnnDataFile.password import sql_password


def rename_daily_table_name():

    # 获取所有表格名称
    # cursor.execute("SHOW TABLES")
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
                print(statement)
                cursor.execute(statement)

    finally:
        cur.close()


if __name__ == "__main__":
    rename_daily_table_name()
