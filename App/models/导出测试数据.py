# "mysql://root:651748264Zz@localhost/mystockrecord"
import multiprocessing

import pymysql
import pandas as pd
import os

# MySQL 连接信息
MYSQL_HOST = 'localhost'  # MySQL 服务器地址
MYSQL_USER = 'root'  # MySQL 用户名
MYSQL_PASSWORD = '651748264Zz'  # MySQL 密码
MYSQL_PORT = 3306  # MySQL 端口
SAVE_PATH = "E:\MyProject\MyStock\MyStock\Stock_RNN\App\static\data\years"  # CSV 保存路径


def export_stock_data(year):
    """
    多进程方式导出指定年份的所有股票数据到 CSV 文件。

    参数：
        year (str): 需要导出的年份，例如 "2023"。
    """
    # 连接 MySQL 数据库
    conn = pymysql.connect(host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, port=MYSQL_PORT)
    cursor = conn.cursor()

    database = f"data1m{year}"

    try:
        conn.select_db(database)
    except pymysql.err.OperationalError:
        print(f"❌ 数据库 {database} 不存在，跳过该年份")
        return

    # 获取当前年份数据库下的所有表（股票代码）
    cursor.execute("SHOW TABLES")
    tables = [t[0] for t in cursor.fetchall()]

    # 创建该年份的 CSV 目录
    year_path = os.path.join(SAVE_PATH, year, "1m")
    os.makedirs(year_path, exist_ok=True)

    print(f"✅ 开始导出 {year} 年的数据，共 {len(tables)} 只股票")

    # 遍历每个股票表
    for stock_code in tables:
        query = f"SELECT * FROM `{stock_code}`"
        df = pd.read_sql(query, conn)
        # 保存 CSV 文件
        csv_path = os.path.join(year_path, f"{stock_code}.csv")
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"📁 {year} - {stock_code}.csv 已保存！")

    # 关闭数据库连接
    cursor.close()
    conn.close()

    print(f"✅ {year} 年的所有数据导出完成！")


if __name__ == "__main__":
    # 需要导出的年份列表
    years = ["2021","2022", "2023", "2024"]

    # 设置进程池数量（根据 CPU 核心数调整，建议 4-8）
    num_workers = min(len(years), os.cpu_count())  # 不超过 CPU 核心数

    print(f"🚀 使用 {num_workers} 个进程并行导出数据...")

    with multiprocessing.Pool(processes=num_workers) as pool:
        pool.map(export_stock_data, years)

    print("🎉 所有年份数据导出完成！")