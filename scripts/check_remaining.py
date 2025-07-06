#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查剩余记录的状态
"""

import pymysql
from datetime import date

def check_remaining_records():
    """检查剩余记录的状态"""
    try:
        print("🔍 检查剩余记录状态...")
        
        # 连接数据库
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='651748264Zz',
            database='quanttradingsystem',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        today = date.today()
        ignore_date = date(2050, 1, 1)
        
        with connection.cursor() as cursor:
            # 检查非忽略记录的状态分布
            cursor.execute("""
                SELECT download_status, COUNT(*) as count 
                FROM record_stock_minute 
                WHERE end_date != %s AND record_date != %s
                GROUP BY download_status
            """, (ignore_date, ignore_date))
            statuses = cursor.fetchall()
            
            print("📈 非忽略记录的状态分布:")
            for status in statuses:
                print(f"  {status['download_status']}: {status['count']}")
            
            # 检查非忽略且非success的记录
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success'
                AND end_date != %s AND record_date != %s
            """, (ignore_date, ignore_date))
            non_success_count = cursor.fetchone()['count']
            print(f"📊 非忽略且非success的记录: {non_success_count}")
            
            if non_success_count > 0:
                # 显示这些记录的详细信息
                cursor.execute("""
                    SELECT rsm.*, smd.code as stock_code
                    FROM record_stock_minute rsm
                    LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                    WHERE rsm.download_status != 'success'
                    AND rsm.end_date != %s AND rsm.record_date != %s
                    LIMIT 10
                """, (ignore_date, ignore_date))
                records = cursor.fetchall()
                
                print("📋 非忽略且非success的记录示例:")
                for record in records:
                    stock_code = record['stock_code'] or f"未知({record['stock_code_id']})"
                    print(f"  {stock_code}: {record['download_status']}, "
                          f"end_date: {record['end_date']}, record_date: {record['record_date']}")
            
            # 检查所有非忽略记录的日期分布
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN end_date <= %s THEN '正常日期'
                        ELSE '异常日期'
                    END as date_category,
                    COUNT(*) as count
                FROM record_stock_minute 
                WHERE end_date != %s AND record_date != %s
                GROUP BY date_category
            """, (today, ignore_date, ignore_date))
            date_dist = cursor.fetchall()
            
            print("📅 非忽略记录的日期分布:")
            for dist in date_dist:
                print(f"  {dist['date_category']}: {dist['count']}")
        
        connection.close()
        print("✅ 检查完成")
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_remaining_records() 