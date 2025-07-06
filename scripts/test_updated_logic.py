#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修改后的下载逻辑
"""

import pymysql
from datetime import date

def test_updated_logic():
    """测试修改后的下载逻辑"""
    try:
        print("🔍 测试修改后的下载逻辑...")
        
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
            # 1. 检查总记录数
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute")
            total = cursor.fetchone()['count']
            print(f"📊 总记录数: {total}")
            
            # 2. 检查被忽略的股票数量
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE end_date = %s OR record_date = %s
            """, (ignore_date, ignore_date))
            ignored_count = cursor.fetchone()['count']
            print(f"🚫 被忽略的股票数量: {ignored_count}")
            
            # 3. 检查符合新下载条件的记录
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success' 
                AND end_date <= %s 
                AND record_date <= %s
                AND end_date != %s
                AND record_date != %s
            """, (today, today, ignore_date, ignore_date))
            eligible_count = cursor.fetchone()['count']
            print(f"🎯 符合新下载条件的记录: {eligible_count}")
            
            # 4. 显示一些符合条件的记录
            if eligible_count > 0:
                cursor.execute("""
                    SELECT rsm.*, smd.code as stock_code
                    FROM record_stock_minute rsm
                    LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                    WHERE rsm.download_status != 'success' 
                    AND rsm.end_date <= %s 
                    AND rsm.record_date <= %s
                    AND rsm.end_date != %s
                    AND rsm.record_date != %s
                    LIMIT 10
                """, (today, today, ignore_date, ignore_date))
                eligible_records = cursor.fetchall()
                
                print("📋 符合条件的记录示例:")
                for record in eligible_records:
                    stock_code = record['stock_code'] or f"未知({record['stock_code_id']})"
                    print(f"  {stock_code}: {record['download_status']}, "
                          f"end_date: {record['end_date']}, record_date: {record['record_date']}")
            
            # 5. 显示被忽略的股票示例
            if ignored_count > 0:
                cursor.execute("""
                    SELECT rsm.*, smd.code as stock_code
                    FROM record_stock_minute rsm
                    LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                    WHERE rsm.end_date = %s OR rsm.record_date = %s
                    LIMIT 5
                """, (ignore_date, ignore_date))
                ignored_records = cursor.fetchall()
                
                print("🚫 被忽略的股票示例:")
                for record in ignored_records:
                    stock_code = record['stock_code'] or f"未知({record['stock_code_id']})"
                    print(f"  {stock_code}: {record['download_status']}, "
                          f"end_date: {record['end_date']}, record_date: {record['record_date']}")
        
        connection.close()
        print("✅ 测试完成")
        
        if eligible_count > 0:
            print(f"🎉 现在有 {eligible_count} 条记录符合下载条件！")
        else:
            print("⚠️ 仍然没有符合下载条件的记录")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_updated_logic() 