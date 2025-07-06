#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复下载数据问题
"""

import pymysql
from datetime import date

def fix_download_data():
    try:
        print("🔧 开始修复下载数据...")
        
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
        yesterday = date(today.year, today.month, today.day - 1)
        
        with connection.cursor() as cursor:
            # 1. 修复end_date >= 今天的记录
            cursor.execute("""
                UPDATE record_stock_minute 
                SET end_date = %s 
                WHERE end_date >= %s
            """, (yesterday, today))
            end_fixed = cursor.rowcount
            print(f"✅ 修复了 {end_fixed} 条 end_date >= 今天的记录")
            
            # 2. 修复record_date >= 今天的记录
            cursor.execute("""
                UPDATE record_stock_minute 
                SET record_date = %s 
                WHERE record_date >= %s
            """, (yesterday, today))
            record_fixed = cursor.rowcount
            print(f"✅ 修复了 {record_fixed} 条 record_date >= 今天的记录")
            
            # 3. 将所有状态改为pending
            cursor.execute("""
                UPDATE record_stock_minute 
                SET download_status = 'pending', download_progress = 0.0
            """)
            status_fixed = cursor.rowcount
            print(f"✅ 修复了 {status_fixed} 条状态记录")
            
            # 提交更改
            connection.commit()
            
            # 4. 验证修复结果
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success' 
                AND end_date < %s 
                AND record_date < %s
            """, (today, today))
            eligible = cursor.fetchone()['count']
            print(f"🎯 修复后符合下载条件的记录: {eligible}")
            
            # 5. 显示修复后的状态分布
            cursor.execute("SELECT download_status, COUNT(*) as count FROM record_stock_minute GROUP BY download_status")
            statuses = cursor.fetchall()
            print("📈 修复后状态分布:")
            for status in statuses:
                print(f"  {status['download_status']}: {status['count']}")
        
        connection.close()
        print("\n🎉 修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_download_data() 