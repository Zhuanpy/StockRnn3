#!/usr/bin/env python3
"""
检查数据库表结构的脚本
"""
import pymysql
import sys

def check_table_structure():
    try:
        # 连接数据库
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='651748264Zz',
            database='quanttradingsystem'
        )
        cursor = conn.cursor()
        
        # 检查record_stock_minute表结构
        print("=== record_stock_minute 表结构 ===")
        cursor.execute("DESCRIBE record_stock_minute")
        result = cursor.fetchall()
        
        for row in result:
            field_name = row[0]
            field_type = row[1]
            null_allowed = row[2]
            key_type = row[3]
            default_value = row[4]
            extra = row[5]
            
            print(f"字段名: {field_name}")
            print(f"  类型: {field_type}")
            print(f"  允许NULL: {null_allowed}")
            print(f"  键类型: {key_type}")
            print(f"  默认值: {default_value}")
            print(f"  额外信息: {extra}")
            print("-" * 50)
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'record_stock_minute'")
        if cursor.fetchone():
            print("✅ record_stock_minute 表存在")
        else:
            print("❌ record_stock_minute 表不存在")
            
        conn.close()
        
    except Exception as e:
        print(f"检查表结构时发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_table_structure() 