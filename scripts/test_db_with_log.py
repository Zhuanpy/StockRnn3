#!/usr/bin/env python3
"""
测试数据库连接并记录日志
"""

import pymysql
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_test.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def test_connection():
    logging.info("开始测试数据库连接...")
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='651748264Zz',
            charset='utf8mb4'
        )
        
        logging.info("✅ 数据库连接成功！")
        
        # 查看数据库
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            logging.info(f"现有数据库: {databases}")
            
            # 检查源数据库
            if 'mystockrecord' in databases:
                logging.info("✅ mystockrecord 数据库存在")
                
                # 查看表
                cursor.execute("USE mystockrecord")
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                logging.info(f"mystockrecord 中的表: {tables}")
            else:
                logging.error("❌ mystockrecord 数据库不存在")
            
            # 检查目标数据库
            if 'quanttradingsystem' in databases:
                logging.info("✅ quanttradingsystem 数据库存在")
            else:
                logging.warning("⚠️ quanttradingsystem 数据库不存在")
        
        connection.close()
        logging.info("数据库连接已关闭")
        
    except Exception as e:
        logging.error(f"❌ 连接失败: {str(e)}")

if __name__ == "__main__":
    test_connection() 