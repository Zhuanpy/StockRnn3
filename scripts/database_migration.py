#!/usr/bin/env python3
"""
数据库迁移脚本

用于将数据从 mystockrecord 数据库迁移到 quanttradingsystem 数据库
"""

import pymysql
import logging
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入配置
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

target_db = "quanttradingsystem"

DB_CONFIG = Config.DB_CONFIG

def check_databases():
    """检查源数据库和目标数据库是否存在"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查源数据库
        cursor.execute("SHOW DATABASES LIKE %s", (source_db,))
        if not cursor.fetchone():
            logger.error(f"源数据库 '{source_db}' 不存在")
            return False
        
        # 检查目标数据库，如果不存在则创建
        cursor.execute("SHOW DATABASES LIKE %s", (target_db,))
        if not cursor.fetchone():
            logger.info(f"目标数据库 '{target_db}' 不存在，正在创建...")
            cursor.execute(f"CREATE DATABASE {target_db}")
            logger.info(f"数据库 '{target_db}' 创建成功")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"检查数据库失败: {str(e)}")
        return False

def get_table_list():
    """获取源数据库中的所有表名"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{source_db}' ORDER BY table_name")
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        logger.info(f"找到 {len(tables)} 个表需要迁移: {tables}")
        return tables
        
    except Exception as e:
        logger.error(f"获取表列表失败: {str(e)}")
        return []

def migrate_table(table_name):
    """迁移单个表"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        logger.info(f"开始迁移表: {table_name}")
        
        # 1. 创建目标表结构
        create_sql = f"CREATE TABLE IF NOT EXISTS {target_db}.{table_name} LIKE {source_db}.{table_name}"
        cursor.execute(create_sql)
        logger.info(f"表结构创建成功: {table_name}")
        
        # 2. 复制数据
        insert_sql = f"INSERT INTO {target_db}.{table_name} SELECT * FROM {source_db}.{table_name}"
        cursor.execute(insert_sql)
        
        # 获取影响的行数
        affected_rows = cursor.rowcount
        logger.info(f"数据复制成功: {table_name} ({affected_rows} 行)")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"迁移表 {table_name} 失败: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False

def migrate_all_tables():
    """迁移所有表"""
    logger.info("开始数据库迁移...")
    logger.info(f"源数据库: {source_db}")
    logger.info(f"目标数据库: {target_db}")
    logger.info(f"数据库配置: {DB_CONFIG['user']}@{DB_CONFIG['host']}")
    
    # 检查数据库
    if not check_databases():
        logger.error("数据库检查失败，迁移终止")
        return False
    
    # 获取表列表
    tables = get_table_list()
    if not tables:
        logger.error("没有找到需要迁移的表")
        return False
    
    # 迁移每个表
    success_count = 0
    failed_count = 0
    
    for table_name in tables:
        if migrate_table(table_name):
            success_count += 1
        else:
            failed_count += 1
    
    # 输出结果
    logger.info("="*50)
    logger.info("迁移完成统计:")
    logger.info(f"成功迁移: {success_count} 个表")
    logger.info(f"迁移失败: {failed_count} 个表")
    logger.info(f"总计: {len(tables)} 个表")
    
    if failed_count == 0:
        logger.info("✅ 所有表迁移成功!")
        return True
    else:
        logger.warning(f"⚠️ 有 {failed_count} 个表迁移失败")
        return False

def generate_migration_sql():
    """生成迁移SQL文件"""
    tables = get_table_list()
    if not tables:
        logger.error("没有找到需要迁移的表")
        return None
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"database_migration_{timestamp}.sql"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("-- 数据库迁移脚本\n")
            f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- 源数据库: {source_db}\n")
            f.write(f"-- 目标数据库: {target_db}\n\n")
            
            f.write(f"USE {target_db};\n\n")
            
            for i, table_name in enumerate(tables, 1):
                f.write(f"-- {i}. 处理表: {table_name}\n")
                f.write(f"CREATE TABLE {target_db}.{table_name} LIKE {source_db}.{table_name};\n")
                f.write(f"INSERT INTO {target_db}.{table_name} SELECT * FROM {source_db}.{table_name};\n\n")
            
            f.write("-- 迁移完成\n")
            f.write("-- 请检查数据完整性\n")
        
        logger.info(f"SQL文件已生成: {filename}")
        return filename
        
    except Exception as e:
        logger.error(f"生成SQL文件失败: {str(e)}")
        return None

def main():
    """主函数"""
    print("数据库迁移工具")
    print("="*50)
    print(f"使用配置: {DB_CONFIG['user']}@{DB_CONFIG['host']}")
    print(f"源数据库: {source_db}")
    print(f"目标数据库: {target_db}")
    print("="*50)
    
    # 询问用户选择操作
    print("\n请选择操作:")
    print("1. 直接执行迁移")
    print("2. 生成SQL文件")
    print("3. 检查数据库状态")
    
    choice = input("\n请输入选择 (1/2/3): ").strip()
    
    if choice == "1":
        # 直接执行迁移
        success = migrate_all_tables()
        if success:
            print("\n✅ 迁移执行成功!")
        else:
            print("\n❌ 迁移执行失败!")
    
    elif choice == "2":
        # 生成SQL文件
        filename = generate_migration_sql()
        if filename:
            print(f"\n✅ SQL文件已生成: {filename}")
            print("你可以手动执行这个SQL文件来完成迁移")
        else:
            print("\n❌ SQL文件生成失败!")
    
    elif choice == "3":
        # 检查数据库状态
        print("\n检查数据库状态...")
        if check_databases():
            tables = get_table_list()
            print(f"✅ 数据库检查通过，找到 {len(tables)} 个表")
        else:
            print("❌ 数据库检查失败")
    
    else:
        print("无效选择")

if __name__ == "__main__":
    # 从config.py获取数据库配置

    source_db = "stockdata"


    main()
