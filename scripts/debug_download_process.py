#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试批量下载过程
"""

import pymysql
import time
from datetime import date, datetime

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='651748264Zz',
            database='quanttradingsystem',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def monitor_download_process():
    """监控下载过程"""
    try:
        print("🔍 开始监控批量下载过程...")
        print(f"监控时间: {datetime.now()}")
        print("=" * 60)
        
        connection = get_db_connection()
        if not connection:
            return False
        
        today = date.today()
        
        # 初始状态检查
        with connection.cursor() as cursor:
            # 检查符合下载条件的记录
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success' 
                AND end_date <= %s 
                AND record_date <= %s
            """, (today, today))
            eligible_count = cursor.fetchone()['count']
            print(f"🎯 符合下载条件的记录: {eligible_count}")
            
            if eligible_count == 0:
                print("❌ 没有符合下载条件的记录")
                return False
            
            # 显示各状态记录数
            cursor.execute("SELECT download_status, COUNT(*) as count FROM record_stock_minute GROUP BY download_status")
            statuses = cursor.fetchall()
            print("📈 当前状态分布:")
            for status in statuses:
                print(f"  {status['download_status']}: {status['count']}")
        
        print("\n🔄 开始实时监控...")
        print("按 Ctrl+C 停止监控")
        
        # 实时监控
        while True:
            with connection.cursor() as cursor:
                # 检查各状态记录数
                cursor.execute("SELECT download_status, COUNT(*) as count FROM record_stock_minute GROUP BY download_status")
                statuses = cursor.fetchall()
                
                # 检查processing状态的记录
                cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute WHERE download_status = 'processing'")
                processing_count = cursor.fetchone()['count']
                
                # 检查最近更新的记录
                cursor.execute("""
                    SELECT rsm.*, smd.code as stock_code
                    FROM record_stock_minute rsm
                    LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                    WHERE rsm.updated_at >= DATE_SUB(NOW(), INTERVAL 1 MINUTE)
                    ORDER BY rsm.updated_at DESC
                    LIMIT 5
                """)
                recent_updates = cursor.fetchall()
                
                # 显示状态
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')}")
                print(f"📊 状态分布: ", end="")
                for status in statuses:
                    print(f"{status['download_status']}: {status['count']} ", end="")
                print()
                
                if processing_count > 0:
                    print(f"🔄 正在处理: {processing_count} 条记录")
                
                if recent_updates:
                    print("📝 最近更新:")
                    for update in recent_updates:
                        stock_code = update['stock_code'] or f"未知({update['stock_code_id']})"
                        print(f"  {stock_code}: {update['download_status']} - {update['updated_at']}")
                
                # 检查是否完成
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM record_stock_minute 
                    WHERE download_status != 'success' 
                    AND end_date <= %s 
                    AND record_date <= %s
                """, (today, today))
                remaining_count = cursor.fetchone()['count']
                
                if remaining_count == 0:
                    print("✅ 所有符合条件的记录已处理完成！")
                    break
            
            time.sleep(5)  # 每5秒检查一次
        
        connection.close()
        return True
        
    except KeyboardInterrupt:
        print("\n⏹️ 监控已停止")
        return True
    except Exception as e:
        print(f"❌ 监控过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_download_eligibility():
    """检查下载资格"""
    try:
        print("🔍 检查下载资格...")
        
        connection = get_db_connection()
        if not connection:
            return False
        
        today = date.today()
        
        with connection.cursor() as cursor:
            # 检查符合下载条件的记录
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success' 
                AND end_date <= %s 
                AND record_date <= %s
            """, (today, today))
            eligible_count = cursor.fetchone()['count']
            
            print(f"🎯 符合下载条件的记录: {eligible_count}")
            
            if eligible_count > 0:
                # 显示一些符合条件的记录
                cursor.execute("""
                    SELECT rsm.*, smd.code as stock_code
                    FROM record_stock_minute rsm
                    LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                    WHERE rsm.download_status != 'success' 
                    AND rsm.end_date <= %s 
                    AND rsm.record_date <= %s
                    LIMIT 10
                """, (today, today))
                eligible_records = cursor.fetchall()
                
                print("📋 符合条件的记录示例:")
                for record in eligible_records:
                    stock_code = record['stock_code'] or f"未知({record['stock_code_id']})"
                    print(f"  {stock_code}: {record['download_status']}, "
                          f"end_date: {record['end_date']}, record_date: {record['record_date']}")
            else:
                print("❌ 没有符合下载条件的记录")
        
        connection.close()
        return eligible_count > 0
        
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {e}")
        return False

def main():
    """主函数"""
    print(f"时间: {datetime.now()}")
    print("=" * 60)
    
    try:
        # 首先检查下载资格
        if not check_download_eligibility():
            print("\n❌ 没有符合下载条件的记录，请先修复数据")
            return False
        
        # 开始监控
        print("\n" + "=" * 60)
        print("开始监控下载过程...")
        monitor_download_process()
        
        print("\n🎉 监控完成！")
        return True
        
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    import sys
    sys.exit(0 if success else 1) 