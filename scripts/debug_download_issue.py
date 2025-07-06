#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试批量下载问题
"""

import sys
import os
from datetime import date, datetime
import pymysql

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

def debug_download_issue():
    """调试下载问题"""
    try:
        print("🔍 开始调试批量下载问题...")
        print(f"调试时间: {datetime.now()}")
        print("=" * 60)
        
        connection = get_db_connection()
        if not connection:
            return False
        
        today = date.today()
        yesterday = date(today.year, today.month, today.day - 1)
        
        with connection.cursor() as cursor:
            # 1. 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'record_stock_minute'")
            if not cursor.fetchone():
                print("❌ record_stock_minute 表不存在！")
                return False
            print("✅ record_stock_minute 表存在")
            
            # 2. 检查总记录数
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute")
            total_records = cursor.fetchone()['count']
            print(f"📊 总记录数: {total_records}")
            
            if total_records == 0:
                print("❌ 表中没有任何记录！")
                return False
            
            # 3. 检查各状态记录数
            cursor.execute("SELECT download_status, COUNT(*) as count FROM record_stock_minute GROUP BY download_status")
            status_counts = cursor.fetchall()
            print(f"📈 状态统计:")
            status_dict = {}
            for status_record in status_counts:
                status = status_record['download_status']
                count = status_record['count']
                status_dict[status] = count
                print(f"  {status}: {count}")
            
            # 4. 检查日期分布
            print(f"\n📅 日期分布检查:")
            
            # 检查end_date分布
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN end_date IS NULL THEN 'NULL'
                        WHEN end_date < %s THEN '小于今天'
                        WHEN end_date = %s THEN '等于今天'
                        ELSE '大于今天'
                    END as date_category,
                    COUNT(*) as count
                FROM record_stock_minute 
                GROUP BY date_category
            """, (today, today))
            end_date_dist = cursor.fetchall()
            print(f"  end_date 分布:")
            for dist in end_date_dist:
                print(f"    {dist['date_category']}: {dist['count']}")
            
            # 检查record_date分布
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN record_date IS NULL THEN 'NULL'
                        WHEN record_date < %s THEN '小于今天'
                        WHEN record_date = %s THEN '等于今天'
                        ELSE '大于今天'
                    END as date_category,
                    COUNT(*) as count
                FROM record_stock_minute 
                GROUP BY date_category
            """, (today, today))
            record_date_dist = cursor.fetchall()
            print(f"  record_date 分布:")
            for dist in record_date_dist:
                print(f"    {dist['date_category']}: {dist['count']}")
            
            # 5. 检查符合下载条件的记录
            print(f"\n🎯 下载条件检查:")
            
            # 条件1: download_status != 'success'
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute WHERE download_status != 'success'")
            condition1_count = cursor.fetchone()['count']
            print(f"  条件1 (download_status != 'success'): {condition1_count}")
            
            # 条件2: end_date < today
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute WHERE end_date < %s", (today,))
            condition2_count = cursor.fetchone()['count']
            print(f"  条件2 (end_date < {today}): {condition2_count}")
            
            # 条件3: record_date < today
            cursor.execute("SELECT COUNT(*) as count FROM record_stock_minute WHERE record_date < %s", (today,))
            condition3_count = cursor.fetchone()['count']
            print(f"  条件3 (record_date < {today}): {condition3_count}")
            
            # 所有条件都满足的记录
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute 
                WHERE download_status != 'success' 
                AND end_date < %s 
                AND record_date < %s
            """, (today, today))
            all_conditions_count = cursor.fetchone()['count']
            print(f"  所有条件都满足: {all_conditions_count}")
            
            # 6. 显示一些示例记录
            print(f"\n📋 示例记录 (前10条):")
            cursor.execute("""
                SELECT rsm.*, smd.name as stock_name, smd.code as stock_code
                FROM record_stock_minute rsm
                LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                LIMIT 10
            """)
            sample_records = cursor.fetchall()
            
            for record in sample_records:
                stock_code = record['stock_code'] or f"未知({record['stock_code_id']})"
                print(f"  ID: {record['id']}, 股票: {stock_code}")
                print(f"    状态: {record['download_status']}, 进度: {record['download_progress']}")
                print(f"    end_date: {record['end_date']}, record_date: {record['record_date']}")
                print(f"    创建时间: {record['created_at']}, 更新时间: {record['updated_at']}")
                print()
            
            # 7. 检查股票代码表
            cursor.execute("SELECT COUNT(*) as count FROM stock_market_data")
            stock_count = cursor.fetchone()['count']
            print(f"\n📈 股票代码表记录数: {stock_count}")
            
            # 8. 检查关联关系
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM record_stock_minute rsm
                LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
                WHERE smd.id IS NULL
            """)
            orphan_records = cursor.fetchone()['count']
            if orphan_records > 0:
                print(f"⚠️ 有 {orphan_records} 条记录对应的股票不存在")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 调试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def fix_all_issues():
    """修复所有问题"""
    try:
        print("\n🔧 开始修复所有问题...")
        
        connection = get_db_connection()
        if not connection:
            return False
        
        today = date.today()
        yesterday = date(today.year, today.month, today.day - 1)
        fixed_count = 0
        
        with connection.cursor() as cursor:
            # 1. 修复NULL的end_date
            cursor.execute("""
                UPDATE record_stock_minute 
                SET end_date = %s 
                WHERE end_date IS NULL
            """, (yesterday,))
            null_end_fixed = cursor.rowcount
            
            # 2. 修复NULL的record_date
            cursor.execute("""
                UPDATE record_stock_minute 
                SET record_date = %s 
                WHERE record_date IS NULL
            """, (yesterday,))
            null_record_fixed = cursor.rowcount
            
            # 3. 修复end_date >= 今天的记录
            cursor.execute("""
                UPDATE record_stock_minute 
                SET end_date = %s 
                WHERE end_date >= %s
            """, (yesterday, today))
            end_fixed = cursor.rowcount
            
            # 4. 修复record_date >= 今天的记录
            cursor.execute("""
                UPDATE record_stock_minute 
                SET record_date = %s 
                WHERE record_date >= %s
            """, (yesterday, today))
            record_fixed = cursor.rowcount
            
            # 5. 将所有download_status改为pending
            cursor.execute("""
                UPDATE record_stock_minute 
                SET download_status = 'pending', download_progress = 0.0
            """)
            status_fixed = cursor.rowcount
            
            fixed_count = null_end_fixed + null_record_fixed + end_fixed + record_fixed + status_fixed
            
            if fixed_count > 0:
                connection.commit()
                print(f"✅ 修复了 {fixed_count} 条记录:")
                print(f"  NULL end_date: {null_end_fixed}")
                print(f"  NULL record_date: {null_record_fixed}")
                print(f"  end_date >= 今天: {end_fixed}")
                print(f"  record_date >= 今天: {record_fixed}")
                print(f"  状态重置: {status_fixed}")
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
        # 调试问题
        if not debug_download_issue():
            print("\n❌ 调试失败")
            return False
        
        # 询问是否修复
        print("\n" + "=" * 60)
        print("是否要修复所有问题？(y/n): ", end="")
        fix_issues = True  # 自动修复
        
        if fix_issues:
            if not fix_all_issues():
                print("❌ 修复失败")
                return False
            
            # 重新检查
            print("\n" + "=" * 60)
            print("修复后重新检查:")
            debug_download_issue()
        
        print("\n🎉 调试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 脚本执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 