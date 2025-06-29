#!/usr/bin/env python3
"""
调试版数据库迁移脚本
"""

import pymysql
import os
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '651748264Zz',
    'charset': 'utf8mb4'
}

def main():
    print("="*60)
    print("调试版数据库迁移脚本")
    print("="*60)
    
    # 检查SQL文件
    sql_file = "scripts/database_migration_20250628_132936.sql"
    print(f"检查SQL文件: {sql_file}")
    
    if not os.path.exists(sql_file):
        print(f"❌ SQL文件不存在: {sql_file}")
        return
    else:
        print(f"✅ SQL文件存在: {sql_file}")
    
    # 连接数据库
    print("\n尝试连接数据库...")
    try:
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ 数据库连接成功")
        
        # 检查数据库是否存在
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            print(f"现有数据库: {databases}")
            
            if 'mystockrecord' in databases:
                print("✅ 源数据库 mystockrecord 存在")
            else:
                print("❌ 源数据库 mystockrecord 不存在")
                return
                
            if 'quanttradingsystem' in databases:
                print("✅ 目标数据库 quanttradingsystem 存在")
            else:
                print("⚠️ 目标数据库 quanttradingsystem 不存在，将自动创建")
        
        # 读取SQL文件
        print(f"\n读取SQL文件: {sql_file}")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print(f"SQL文件大小: {len(sql_content)} 字符")
        
        # 分割SQL语句
        statements = []
        for stmt in sql_content.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                statements.append(stmt)
        
        print(f"找到 {len(statements)} 条有效SQL语句")
        
        # 执行SQL
        print("\n开始执行SQL语句...")
        with connection.cursor() as cursor:
            for i, sql in enumerate(statements, 1):
                if sql:
                    print(f"\n执行第 {i} 条SQL:")
                    print(f"SQL: {sql[:100]}...")
                    try:
                        cursor.execute(sql)
                        print(f"✅ 第 {i} 条SQL执行成功")
                    except Exception as e:
                        print(f"❌ 第 {i} 条SQL执行失败: {str(e)}")
                        print(f"完整SQL: {sql}")
                        raise
        
        # 提交事务
        connection.commit()
        print("\n✅ 所有SQL执行完成，事务已提交")
        print("✅ 数据库迁移成功！")
        
    except Exception as e:
        print(f"\n❌ 执行失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        if 'connection' in locals():
            try:
                connection.rollback()
                print("事务已回滚")
            except:
                pass
    finally:
        if 'connection' in locals():
            try:
                connection.close()
                print("数据库连接已关闭")
            except:
                pass
    
    print("\n" + "="*60)
    print("脚本执行完成")
    print("="*60)

if __name__ == "__main__":
    main() 