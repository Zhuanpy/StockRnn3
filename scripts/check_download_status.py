#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查批量下载状态和数据库记录情况
"""

import sys
import os
from datetime import date, datetime
import pymysql
from sqlalchemy import create_engine, text

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_connection():
    """获取数据库连接"""
    try:
        # 使用PyMySQL直接连接
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

def check_download_status():
    """检查下载状态和数据库记录情况"""
    try:
        print("🔍 开始检查批量下载状态...")
        print(f"检查时间: {datetime.now()}")
        print("-" * 60)
        
        # 获取数据库连接
        connection = get_db_connection()
        if not connection:
            return False
        
        # 获取当前日期
        today = date.today()
        
        with connection.cursor() as cursor:
            # 1. 检查总记录数
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute")
            total_records = cursor.fetchone()['count']
            print(f"📊 总记录数: {total_records}")
            
            if total_records == 0:
                print("❌ 数据库中没有记录，需要先初始化数据")
                return False
            
            # 2. 检查各状态记录数
            cursor.execute("SELECT download_status, COUNT(*) as count FROM record_stock_minute GROUP BY download_status")
            status_counts = cursor.fetchall()
            
            print(f"📈 状态统计:")
            status_dict = {}
            for status_record in status_counts:
                status = status_record['download_status']
                count = status_record['count']
                status_dict[status] = count
                print(f"  {status}: {count}")
            
            # 3. 检查符合下载条件的记录
            # 根据下载逻辑，需要满足以下条件：
            # - download_status != 'success'
            # - end_date < today
            # - record_date < today
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success' 
                AND end_date < %s 
                AND record_date < %s
            """, (today, today))
            eligible_records = cursor.fetchone()['count']
            
            print(f"\n🎯 符合下载条件的记录数: {eligible_records}")
            
            if eligible_records == 0:
                print("⚠️ 没有符合下载条件的记录")
                
                # 分析原因
                print("\n🔍 分析可能的原因:")
                
                # 检查日期问题
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM record_stock_minute 
                    WHERE end_date >= %s OR record_date >= %s
                """, (today, today))
                date_issues_count = cursor.fetchone()['count']
                
                if date_issues_count > 0:
                    print(f"  日期问题: {date_issues_count} 条记录的日期 >= 今天")
                
                # 检查成功状态
                success_count = status_dict.get('success', 0)
                if success_count > 0:
                    print(f"  成功状态: {success_count} 条记录状态为 'success'")
            
            # 4. 显示一些示例记录
            print(f"\n📋 示例记录 (前5条):")
            cursor.execute("""
                SELECT rsm.*, smd.name as stock_name, smd.code as stock_code
                FROM record_stock_minute rsm
                LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                LIMIT 5
            """)
            sample_records = cursor.fetchall()
            
            for record in sample_records:
                stock_code = record['stock_code'] or f"未知({record['stock_code_id']})"
                print(f"  ID: {record['id']}, 股票: {stock_code}, 状态: {record['download_status']}, "
                      f"结束日期: {record['end_date']}, 记录日期: {record['record_date']}")
            
            # 5. 检查股票代码表
            cursor.execute("SELECT COUNT(*) as count FROM stock_market_data")
            stock_count = cursor.fetchone()['count']
            print(f"\n📈 股票代码表记录数: {stock_count}")
            
            # 6. 检查是否有未关联的股票
            if stock_count > 0:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM stock_market_data smd
                    LEFT JOIN record_stock_minute rsm ON smd.id = rsm.stock_code_id
                    WHERE rsm.id IS NULL
                """)
                missing_stocks = cursor.fetchone()['count']
                
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM record_stock_minute rsm
                    LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                    WHERE smd.id IS NULL
                """)
                extra_records = cursor.fetchone()['count']
                
                if missing_stocks > 0:
                    print(f"⚠️ 有 {missing_stocks} 只股票没有下载记录")
                if extra_records > 0:
                    print(f"⚠️ 有 {extra_records} 条记录对应的股票不存在")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def fix_common_issues():
    """修复常见问题"""
    try:
        print("\n🔧 开始修复常见问题...")
        
        connection = get_db_connection()
        if not connection:
            return False
        
        today = date.today()
        yesterday = date(today.year, today.month, today.day - 1)
        fixed_count = 0
        
        with connection.cursor() as cursor:
            # 1. 修复end_date >= 今天的记录
            cursor.execute("""
                UPDATE record_stock_minute 
                SET end_date = %s 
                WHERE end_date >= %s
            """, (yesterday, today))
            end_fixed = cursor.rowcount

            # 2. 修复record_date >= 今天的记录
            cursor.execute("""
                UPDATE record_stock_minute 
                SET record_date = %s 
                WHERE record_date >= %s
            """, (yesterday, today))
            record_fixed = cursor.rowcount

            # 3. 将所有download_status不是pending的记录批量改为pending，download_progress设为0
            cursor.execute("""
                UPDATE record_stock_minute 
                SET download_status = 'pending', download_progress = 0.0 
                WHERE download_status != 'pending'
            """)
            status_fixed = cursor.rowcount

            fixed_count = end_fixed + record_fixed + status_fixed
            
            if fixed_count > 0:
                connection.commit()
                print(f"✅ 修复了 {fixed_count} 条记录 (end_date: {end_fixed}, record_date: {record_fixed}, 状态: {status_fixed})")
            else:
                print("✅ 没有需要修复的记录")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 修复过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print(f"时间: {datetime.now()}")
    print("=" * 60)
    
    try:
        # 检查状态
        if not check_download_status():
            print("\n❌ 状态检查失败")
            return False
        
        # 询问是否修复问题
        print("\n" + "=" * 60)
        print("是否要修复常见问题？(y/n): ", end="")
        # 这里可以添加用户输入，暂时自动修复
        fix_issues = True  # 可以根据需要修改
        
        if fix_issues:
            if not fix_common_issues():
                print("❌ 修复失败")
                return False
            
            # 重新检查状态
            print("\n" + "=" * 60)
            print("修复后重新检查状态:")
            check_download_status()
        
        print("\n🎉 检查完成！")
        return True
        
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 