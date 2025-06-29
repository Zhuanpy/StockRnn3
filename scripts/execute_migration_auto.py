#!/usr/bin/env python3
"""
自动执行数据库迁移SQL脚本

用于执行生成的迁移SQL文件，将数据从 mystockrecord 复制到 quanttradingsystem
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


def execute_sql_file(sql_file_path):
    """
    执行SQL文件
    
    Args:
        sql_file_path: SQL文件路径
    """
    # 从config.py获取数据库配置
    db_config = Config.DB_CONFIG
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=db_config['host'],
            port=3306,
            user=db_config['user'],
            password=db_config['password'],
            charset='utf8mb4'
        )
        
        logger.info("数据库连接成功")
        
        # 读取SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        logger.info(f"读取SQL文件: {sql_file_path}")
        
        # 分割SQL语句
        sql_statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        logger.info(f"共找到 {len(sql_statements)} 条SQL语句")
        
        # 执行SQL语句
        with connection.cursor() as cursor:
            for i, sql in enumerate(sql_statements, 1):
                if sql.startswith('--') or not sql.strip():
                    continue
                    
                try:
                    logger.info(f"执行第 {i} 条SQL: {sql[:50]}...")
                    cursor.execute(sql)
                    logger.info(f"第 {i} 条SQL执行成功")
                except Exception as e:
                    logger.error(f"第 {i} 条SQL执行失败: {str(e)}")
                    logger.error(f"SQL内容: {sql}")
                    raise
        
        # 提交事务
        connection.commit()
        logger.info("所有SQL语句执行完成，事务已提交")
        
        return True
        
    except Exception as e:
        logger.error(f"执行SQL文件失败: {str(e)}")
        if 'connection' in locals():
            connection.rollback()
            logger.info("事务已回滚")
        return False
    finally:
        if 'connection' in locals():
            connection.close()
            logger.info("数据库连接已关闭")


def main():
    """主函数"""
    print("数据库迁移自动执行工具")
    print("="*50)
    
    # 查找最新的迁移SQL文件
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    sql_files = [f for f in os.listdir(scripts_dir) if f.startswith('database_migration_') and f.endswith('.sql')]
    
    if not sql_files:
        print("错误: 没有找到迁移SQL文件")
        print("请先运行 database_migration.py 生成SQL文件")
        return
    
    # 按时间排序，选择最新的文件
    sql_files.sort()
    latest_sql_file = sql_files[-1]
    sql_file_path = os.path.join(scripts_dir, latest_sql_file)
    
    print(f"找到迁移SQL文件: {latest_sql_file}")
    print(f"文件路径: {sql_file_path}")
    print("="*50)
    
    print("开始执行迁移...")
    print("="*50)
    
    # 执行SQL文件
    success = execute_sql_file(sql_file_path)
    
    if success:
        print("\n" + "="*50)
        print("✅ 迁移执行成功！")
        print("="*50)
        print("数据已从 mystockrecord 数据库复制到 quanttradingsystem 数据库")
        print("请检查数据完整性")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ 迁移执行失败！")
        print("="*50)
        print("请检查错误日志并修复问题后重试")
        print("="*50)


if __name__ == "__main__":
    main() 