#!/usr/bin/env python3
"""
简化版数据库迁移SQL生成脚本

直接生成从 mystockrecord 数据库复制表结构和数据到 quanttradingsystem 数据库的 SQL 语句
"""

import pymysql
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from config import Config


def generate_migration_sql(host='localhost', port=3306, user='root', password='651748264Zz', 
                          source_db='mystockrecord', target_db='quanttradingsystem'):
    """
    生成数据库迁移SQL语句
    
    Args:
        host: 数据库主机地址
        port: 数据库端口
        user: 数据库用户名
        password: 数据库密码
        source_db: 源数据库名
        target_db: 目标数据库名
    
    Returns:
        str: 生成的SQL语句
    """
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        print("数据库连接成功！")
        
        with connection.cursor() as cursor:
            # 检查源数据库是否存在
            cursor.execute("SHOW DATABASES LIKE %s", (source_db,))
            if not cursor.fetchone():
                print(f"错误: 源数据库 '{source_db}' 不存在")
                return None
            
            # 检查目标数据库是否存在，如果不存在则创建
            cursor.execute("SHOW DATABASES LIKE %s", (target_db,))
            if not cursor.fetchone():
                print(f"目标数据库 '{target_db}' 不存在，正在创建...")
                cursor.execute(f"CREATE DATABASE {target_db}")
                print(f"数据库 '{target_db}' 创建成功")
            
            # 获取源数据库中的所有表名
            sql = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s
            ORDER BY table_name
            """
            cursor.execute(sql, (source_db,))
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"找到 {len(tables)} 个表需要迁移:")
            for table in tables:
                print(f"  - {table}")
            
            if not tables:
                print(f"源数据库 '{source_db}' 中没有找到任何表")
                return None
            
            # 生成SQL语句
            sql_statements = []
            sql_statements.append(f"USE {target_db};")
            sql_statements.append("")
            
            for table in tables:
                create_sql = f"CREATE TABLE {target_db}.{table} LIKE {source_db}.{table};"
                insert_sql = f"INSERT INTO {target_db}.{table} SELECT * FROM {source_db}.{table};"
                
                sql_statements.append(f"-- 处理表: {table}")
                sql_statements.append(create_sql)
                sql_statements.append(insert_sql)
                sql_statements.append("")
            
            return "\n".join(sql_statements)
            
    except Exception as e:
        print(f"生成SQL失败: {str(e)}")
        return None
    finally:
        if 'connection' in locals():
            connection.close()


def save_sql_to_file(sql_content, filename=None):
    """
    保存SQL内容到文件
    
    Args:
        sql_content: SQL内容
        filename: 文件名，如果为None则自动生成
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"migration_{timestamp}.sql"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("-- 数据库迁移脚本\n")
            f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- 用途: 从 mystockrecord 数据库复制表结构和数据到 quanttradingsystem 数据库\n\n")
            f.write(sql_content)
            f.write("\n-- 迁移完成\n")
        
        print(f"SQL文件已保存: {filename}")
        return filename
    except Exception as e:
        print(f"保存文件失败: {str(e)}")
        return None


def main():
    """主函数"""
    # 从config.py获取数据库配置
    db_config = Config.DB_CONFIG
    
    # 数据库连接配置
    config = {
        'host': db_config['host'],
        'port': 3306,
        'user': db_config['user'],
        'password': db_config['password'],
        'source_db': 'mystockrecord',
        'target_db': 'quanttradingsystem'
    }
    
    print("数据库迁移SQL生成工具")
    print("="*50)
    print(f"使用配置: {config['user']}@{config['host']}")
    print(f"源数据库: {config['source_db']}")
    print(f"目标数据库: {config['target_db']}")
    print("="*50)
    
    print("\n开始生成数据库迁移SQL...")
    
    # 生成SQL
    sql_content = generate_migration_sql(**config)
    
    if sql_content:
        # 保存到文件
        filename = save_sql_to_file(sql_content)
        
        print("\n" + "="*60)
        print("SQL生成完成！")
        print("="*60)
        print(f"文件位置: {filename}")
        print("使用方法:")
        print("1. 检查SQL文件内容")
        print("2. 在MySQL客户端中执行该SQL文件")
        print("3. 或者使用命令行: mysql -u root -p < migration_xxx.sql")
        print("="*60)
        
        # 显示SQL预览
        print("\nSQL预览 (前10行):")
        print("-" * 40)
        lines = sql_content.split('\n')
        for i, line in enumerate(lines[:10]):
            print(f"{i+1:2d}: {line}")
        if len(lines) > 10:
            print("...")
    else:
        print("SQL生成失败，请检查数据库连接配置")


if __name__ == "__main__":
    main() 