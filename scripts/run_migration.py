#!/usr/bin/env python3
"""
直接执行数据库迁移
"""

import pymysql
import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '651748264Zz',
    'charset': 'utf8mb4'
}

def main():
    print("开始执行数据库迁移...")
    
    # 连接数据库
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("数据库连接成功")
        
        # SQL文件路径
        sql_file = "scripts/database_migration_20250628_132936.sql"
        
        if not os.path.exists(sql_file):
            print(f"SQL文件不存在: {sql_file}")
            return
        
        # 读取SQL文件
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"读取SQL文件: {sql_file}")
        
        # 执行SQL
        with connection.cursor() as cursor:
            # 分割SQL语句
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip() and not stmt.strip().startswith('--')]
            
            print(f"共找到 {len(statements)} 条SQL语句")
            
            for i, sql in enumerate(statements, 1):
                if sql:
                    print(f"执行第 {i} 条SQL...")
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
    main() 