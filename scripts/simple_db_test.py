#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的数据库测试脚本
"""

import pymysql
from datetime import date

def test_db():
    try:
        print("🔍 测试数据库连接...")
        
        # 连接数据库
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='651748264Zz',
            database='quanttradingsystem',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("✅ 数据库连接成功")
        
        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'record_stock_minute'")
            if cursor.fetchone():
                print("✅ record_stock_minute 表存在")
            else:
                print("❌ record_stock_minute 表不存在")
                return
            
            # 检查记录数
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute")
            total = cursor.fetchone()['count']
            print(f"📊 总记录数: {total}")
            
            if total == 0:
                print("❌ 表中没有记录")
                return
            
            # 检查状态分布
            cursor.execute("SELECT download_status, COUNT(*) as count FROM record_stock_minute GROUP BY download_status")
            statuses = cursor.fetchall()
            print("📈 状态分布:")
            for status in statuses:
                print(f"  {status['download_status']}: {status['count']}")
            
            # 检查日期
            today = date.today()
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute WHERE end_date >= %s", (today,))
            end_date_issue = cursor.fetchone()['count']
            print(f"📅 end_date >= 今天: {end_date_issue}")
            
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute WHERE record_date >= %s", (today,))
            record_date_issue = cursor.fetchone()['count']
            print(f"📅 record_date >= 今天: {record_date_issue}")
            
            # 检查符合下载条件的记录
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success' 
                AND end_date < %s 
                AND record_date < %s
            """, (today, today))
            eligible = cursor.fetchone()['count']
            print(f"🎯 符合下载条件的记录: {eligible}")
            
            # 显示前5条记录
            cursor.execute("SELECT * FROM record_stock_minute LIMIT 5")
            records = cursor.fetchall()
            print("\n📋 前5条记录:")
            for record in records:
                print(f"  ID: {record['id']}, 状态: {record['download_status']}, "
                      f"end_date: {record['end_date']}, record_date: {record['record_date']}")
        
        connection.close()
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db() 