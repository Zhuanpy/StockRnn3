#!/usr/bin/env python3
"""
直接执行SQL语句
"""

import pymysql

def execute_migration():
    print("开始执行数据库迁移...")
    
    # 数据库配置
    config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': '651748264Zz',
        'charset': 'utf8mb4'
    }
    
    # SQL语句列表
    sql_statements = [
        "USE quanttradingsystem;",
        "CREATE TABLE quanttradingsystem.basic_info_others_code LIKE mystockrecord.basic_info_others_code;",
        "INSERT INTO quanttradingsystem.basic_info_others_code SELECT * FROM mystockrecord.basic_info_others_code;",
        "CREATE TABLE quanttradingsystem.count_board LIKE mystockrecord.count_board;",
        "INSERT INTO quanttradingsystem.count_board SELECT * FROM mystockrecord.count_board;",
        "CREATE TABLE quanttradingsystem.count_stock_pool LIKE mystockrecord.count_stock_pool;",
        "INSERT INTO quanttradingsystem.count_stock_pool SELECT * FROM mystockrecord.count_stock_pool;",
        "CREATE TABLE quanttradingsystem.download_1m_data LIKE mystockrecord.download_1m_data;",
        "INSERT INTO quanttradingsystem.download_1m_data SELECT * FROM mystockrecord.download_1m_data;",
        "CREATE TABLE quanttradingsystem.record_stock_pool LIKE mystockrecord.record_stock_pool;",
        "INSERT INTO quanttradingsystem.record_stock_pool SELECT * FROM mystockrecord.record_stock_pool;",
        "CREATE TABLE quanttradingsystem.record_trading LIKE mystockrecord.record_trading;",
        "INSERT INTO quanttradingsystem.record_trading SELECT * FROM mystockrecord.record_trading;",
        "CREATE TABLE quanttradingsystem.recordtopfunds500 LIKE mystockrecord.recordtopfunds500;",
        "INSERT INTO quanttradingsystem.recordtopfunds500 SELECT * FROM mystockrecord.recordtopfunds500;",
        "CREATE TABLE quanttradingsystem.rnn_running_records LIKE mystockrecord.rnn_running_records;",
        "INSERT INTO quanttradingsystem.rnn_running_records SELECT * FROM mystockrecord.rnn_running_records;",
        "CREATE TABLE quanttradingsystem.rnn_training_records LIKE mystockrecord.rnn_training_records;",
        "INSERT INTO quanttradingsystem.rnn_training_records SELECT * FROM mystockrecord.rnn_training_records;",
        "CREATE TABLE quanttradingsystem.stock_classification LIKE mystockrecord.stock_classification;",
        "INSERT INTO quanttradingsystem.stock_classification SELECT * FROM mystockrecord.stock_classification;",
        "CREATE TABLE quanttradingsystem.stock_issue LIKE mystockrecord.stock_issue;",
        "INSERT INTO quanttradingsystem.stock_issue SELECT * FROM mystockrecord.stock_issue;"
    ]
    
    try:
        # 连接数据库
        connection = pymysql.connect(**config)
        print("数据库连接成功")
        
        # 执行SQL语句
        with connection.cursor() as cursor:
            for i, sql in enumerate(sql_statements, 1):
                print(f"执行第 {i} 条SQL: {sql[:50]}...")
                cursor.execute(sql)
                print(f"第 {i} 条SQL执行成功")
        
        # 提交事务
        connection.commit()
        print("所有SQL执行完成，事务已提交")
        print("✅ 数据库迁移成功！")
        
    except Exception as e:
        print(f"执行失败: {str(e)}")
        if 'connection' in locals():
            connection.rollback()
            print("事务已回滚")
    finally:
        if 'connection' in locals():
            connection.close()
            print("数据库连接已关闭")

if __name__ == "__main__":
    execute_migration() 