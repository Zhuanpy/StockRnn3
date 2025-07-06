#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的下载逻辑
"""

import pymysql
from datetime import date

def test_new_logic():
    """测试新的下载逻辑"""
    try:
        print("🔍 测试新的下载逻辑...")
        
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
            # 1. 检查最新记录日期
            cursor.execute("""
                SELECT record_date 
                FROM record_stock_minute 
                WHERE record_date != %s
                ORDER BY record_date DESC 
                LIMIT 1
            """, (ignore_date,))
            latest_record = cursor.fetchone()
            
            if latest_record:
                latest_date = latest_record['record_date']
                print(f"📅 最新记录日期: {latest_date}")
                print(f"📅 今天日期: {today}")
                
                if latest_date != today:
                    print("🔄 检测到日期不同，需要重置success记录")
                    
                    # 检查可以重置的记录数量
                    cursor.execute("""
                        SELECT COUNT(*) as count 
                        FROM record_stock_minute 
                        WHERE download_status = 'success'
                        AND end_date != %s AND record_date != %s
                    """, (ignore_date, ignore_date))
                    success_count = cursor.fetchone()['count']
                    print(f"📊 可以重置的success记录: {success_count}")
                    
                    if success_count > 0:
                        # 模拟重置操作
                        cursor.execute("""
                            UPDATE record_stock_minute 
                            SET download_status = 'pending', 
                                download_progress = 0.0,
                                updated_at = NOW()
                            WHERE download_status = 'success'
                            AND end_date != %s AND record_date != %s
                        """, (ignore_date, ignore_date))
                        
                        reset_count = cursor.rowcount
                        connection.commit()
                        print(f"✅ 重置了 {reset_count} 条记录为pending状态")
                        
                        # 验证重置后的状态
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
                        print(f"🎯 重置后符合下载条件的记录: {eligible_count}")
                        
                        if eligible_count > 0:
                            print("🎉 现在有数据可以下载了！")
                        else:
                            print("⚠️ 仍然没有符合下载条件的记录")
                    else:
                        print("ℹ️ 没有success记录需要重置")
                else:
                    print("✅ 记录日期是最新的，无需重置")
            else:
                print("❌ 没有找到有效记录")
            
            # 显示最终状态分布
            cursor.execute("SELECT download_status, COUNT(*) as count FROM record_stock_minute GROUP BY download_status")
            statuses = cursor.fetchall()
            print("\n📈 最终状态分布:")
            for status in statuses:
                print(f"  {status['download_status']}: {status['count']}")
        
        connection.close()
        print("✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_logic() 