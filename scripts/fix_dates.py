#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复异常的日期值
"""

import pymysql
from datetime import date

def fix_abnormal_dates():
    """修复异常的日期值"""
    try:
        print("🔧 开始修复异常日期...")
        
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
            # 检查异常日期
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE end_date > %s OR record_date > %s
            """, (today, today))
            abnormal_count = cursor.fetchone()['count']
            print(f"📅 发现 {abnormal_count} 条异常日期记录")
            
            if abnormal_count > 0:
                # 修复end_date异常值
                cursor.execute("""
                    UPDATE record_stock_minute 
                    SET end_date = %s 
                    WHERE end_date > %s
                """, (yesterday, today))
                end_fixed = cursor.rowcount
                print(f"✅ 修复了 {end_fixed} 条 end_date 异常记录")
                
                # 修复record_date异常值
                cursor.execute("""
                    UPDATE record_stock_minute 
                    SET record_date = %s 
                    WHERE record_date > %s
                """, (yesterday, today))
                record_fixed = cursor.rowcount
                print(f"✅ 修复了 {record_fixed} 条 record_date 异常记录")
                
                # 提交更改
                connection.commit()
                
                # 验证修复结果
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM record_stock_minute 
                    WHERE download_status != 'success' 
                    AND end_date <= %s 
                    AND record_date <= %s
                """, (today, today))
                eligible = cursor.fetchone()['count']
                print(f"🎯 修复后符合下载条件的记录: {eligible}")
            else:
                print("✅ 没有发现异常日期记录")
        
        connection.close()
        print("🎉 修复完成！")
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    fix_abnormal_dates() 