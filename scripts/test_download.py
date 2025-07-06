#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的下载状态测试
"""

import sys
import os
from datetime import date

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import pymysql
    print("✅ pymysql 已安装")
except ImportError:
    print("❌ pymysql 未安装")
    sys.exit(1)

def test_download_status():
    """测试下载状态"""
    try:
        print("🔍 测试下载状态...")
        
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
        
        with connection.cursor() as cursor:
            # 检查总记录数
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute")
            total = cursor.fetchone()['count']
            print(f"📊 总记录数: {total}")
            
            # 检查状态分布
            cursor.execute("SELECT download_status, COUNT(*) as count FROM record_stock_minute GROUP BY download_status")
            statuses = cursor.fetchall()
            print("📈 状态分布:")
            for status in statuses:
                print(f"  {status['download_status']}: {status['count']}")
            
            # 检查符合下载条件的记录
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success' 
                AND end_date <= %s 
                AND record_date <= %s
            """, (today, today))
            eligible = cursor.fetchone()['count']
            print(f"🎯 符合下载条件的记录: {eligible}")
            
            # 显示一些示例记录
            cursor.execute("""
                SELECT rsm.*, smd.code as stock_code
                FROM record_stock_minute rsm
                LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                WHERE rsm.download_status != 'success'
                LIMIT 5
            """)
            records = cursor.fetchall()
            print("📋 非success状态记录示例:")
            for record in records:
                stock_code = record['stock_code'] or f"未知({record['stock_code_id']})"
                print(f"  {stock_code}: {record['download_status']}, "
                      f"end_date: {record['end_date']}, record_date: {record['record_date']}")
        
        connection.close()
        print("✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_download_status() 