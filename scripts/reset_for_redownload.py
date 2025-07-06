#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置记录状态以便重新下载
"""

import pymysql
from datetime import date

def reset_for_redownload():
    """重置记录状态以便重新下载"""
    try:
        print("🔧 重置记录状态以便重新下载...")
        
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
            # 检查可以重置的记录数量
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status = 'success'
                AND end_date != %s AND record_date != %s
            """, (ignore_date, ignore_date))
            success_count = cursor.fetchone()['count']
            print(f"📊 可以重置的success记录: {success_count}")
            
            if success_count == 0:
                print("❌ 没有可以重置的记录")
                return False
            
            # 重置前10条记录（避免重置太多）
            reset_count = min(10, success_count)
            cursor.execute("""
                UPDATE record_stock_minute 
                SET download_status = 'pending', 
                    download_progress = 0.0,
                    updated_at = NOW()
                WHERE download_status = 'success'
                AND end_date != %s AND record_date != %s
                LIMIT %s
            """, (ignore_date, ignore_date, reset_count))
            
            actual_reset = cursor.rowcount
            connection.commit()
            
            print(f"✅ 重置了 {actual_reset} 条记录为pending状态")
            
            # 验证重置结果
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
            print(f"🎯 现在符合下载条件的记录: {eligible_count}")
            
            # 显示重置后的记录
            cursor.execute("""
                SELECT rsm.*, smd.code as stock_code
                FROM record_stock_minute rsm
                LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                WHERE rsm.download_status = 'pending'
                AND rsm.end_date != %s AND rsm.record_date != %s
                LIMIT 5
            """, (ignore_date, ignore_date))
            reset_records = cursor.fetchall()
            
            print("📋 重置后的记录示例:")
            for record in reset_records:
                stock_code = record['stock_code'] or f"未知({record['stock_code_id']})"
                print(f"  {stock_code}: {record['download_status']}, "
                      f"end_date: {record['end_date']}, record_date: {record['record_date']}")
        
        connection.close()
        print("🎉 重置完成！")
        return True
        
    except Exception as e:
        print(f"❌ 重置失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    reset_for_redownload() 