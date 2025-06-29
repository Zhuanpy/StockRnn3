#!/usr/bin/env python3
"""
更新 stock_market_data 表结构
添加缺失的字段：es_code, market_code, txd_market, hs_market
"""
import pymysql
import logging
from config import Config

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def update_stock_market_data_table():
    """
    更新 stock_market_data 表结构
    """
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password'],
            database='quanttradingsystem',
            charset=Config.DB_CONFIG['charset']
        )
        
        cursor = connection.cursor()
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'stock_market_data'")
        if not cursor.fetchone():
            logger.error("❌ stock_market_data 表不存在")
            return False
        
        # 检查现有字段
        cursor.execute("DESCRIBE stock_market_data")
        existing_columns = [row[0] for row in cursor.fetchall()]
        logger.info(f"现有字段: {existing_columns}")
        
        # 需要添加的字段
        columns_to_add = [
            ("es_code", "VARCHAR(20) COMMENT '东方财富代码'"),
            ("market_code", "VARCHAR(20) COMMENT '市场代码'"),
            ("txd_market", "VARCHAR(20) COMMENT '通达信市场代码'"),
            ("hs_market", "VARCHAR(20) COMMENT '恒生市场代码'"),
            ("created_at", "DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'"),
            ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'")
        ]
        
        # 添加缺失的字段
        for column_name, column_def in columns_to_add:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE stock_market_data ADD COLUMN {column_name} {column_def}"
                    cursor.execute(sql)
                    logger.info(f"✅ 成功添加字段: {column_name}")
                except Exception as e:
                    logger.warning(f"⚠️ 添加字段 {column_name} 时出错: {str(e)}")
            else:
                logger.info(f"ℹ️ 字段 {column_name} 已存在")
        
        # 提交更改
        connection.commit()
        
        # 显示最终的表结构
        cursor.execute("DESCRIBE stock_market_data")
        final_columns = cursor.fetchall()
        logger.info("最终表结构:")
        for column in final_columns:
            logger.info(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
        
        logger.info("✅ stock_market_data 表结构更新完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 更新表结构时出错: {str(e)}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def create_stock_classification_table():
    """
    创建 stock_classification 表（如果不存在）
    """
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password'],
            database='quanttradingsystem',
            charset=Config.DB_CONFIG['charset']
        )
        
        cursor = connection.cursor()
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'stock_classification'")
        if not cursor.fetchone():
            # 创建表
            create_table_sql = """
            CREATE TABLE stock_classification (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(20) COMMENT '股票名称',
                code VARCHAR(20) COMMENT '股票代码',
                classification VARCHAR(20) COMMENT '股票分类',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
            cursor.execute(create_table_sql)
            logger.info("✅ 成功创建 stock_classification 表")
        else:
            logger.info("ℹ️ stock_classification 表已存在")
        
        # 提交更改
        connection.commit()
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建 stock_classification 表时出错: {str(e)}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    logger.info("开始更新数据库表结构...")
    
    # 更新 stock_market_data 表
    if update_stock_market_data_table():
        logger.info("✅ stock_market_data 表更新成功")
    else:
        logger.error("❌ stock_market_data 表更新失败")
    
    # 创建 stock_classification 表
    if create_stock_classification_table():
        logger.info("✅ stock_classification 表创建成功")
    else:
        logger.error("❌ stock_classification 表创建失败")
    
    logger.info("数据库表结构更新完成") 