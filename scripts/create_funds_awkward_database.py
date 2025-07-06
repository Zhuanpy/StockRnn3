#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建基金重仓数据数据库
"""

import pymysql
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def create_funds_awkward_database():
    """创建funds_awkward数据库"""
    
    # 获取数据库配置
    db_config = Config.DB_CONFIG
    
    try:
        # 连接MySQL服务器（不指定数据库）
        connection = pymysql.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            charset=db_config['charset']
        )
        
        cursor = connection.cursor()
        
        # 创建数据库
        database_name = 'funds_awkward'
        create_db_sql = f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        
        print(f"正在创建数据库: {database_name}")
        cursor.execute(create_db_sql)
        
        # 验证数据库是否创建成功
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        
        if database_name in databases:
            print(f"✅ 数据库 {database_name} 创建成功！")
            
            # 切换到新创建的数据库
            cursor.execute(f"USE `{database_name}`")
            
            # 创建示例表（可选）
            create_sample_table_sql = """
            CREATE TABLE IF NOT EXISTS `awkward_20241201` (
                `id` INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
                `fund_name` VARCHAR(255) COMMENT '基金名称',
                `fund_code` VARCHAR(50) COMMENT '基金代码',
                `stock_name` VARCHAR(255) COMMENT '股票名称',
                `stock_code` VARCHAR(50) COMMENT '股票代码',
                `holdings_ratio` VARCHAR(20) COMMENT '持仓比例',
                `market_value` VARCHAR(50) COMMENT '市值',
                `shares` VARCHAR(50) COMMENT '持股数量',
                `download_date` VARCHAR(20) COMMENT '下载日期',
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='基金重仓数据示例表'
            """
            
            print("正在创建示例表...")
            cursor.execute(create_sample_table_sql)
            print("✅ 示例表创建成功！")
            
        else:
            print(f"❌ 数据库 {database_name} 创建失败！")
            return False
            
        connection.commit()
        cursor.close()
        connection.close()
        
        print(f"🎉 数据库 {database_name} 初始化完成！")
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库时发生错误: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    
    try:
        # 测试连接funds_awkward数据库
        connection = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password'],
            database='funds_awkward',
            charset=Config.DB_CONFIG['charset']
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        
        print(f"✅ 数据库连接测试成功！MySQL版本: {version[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始创建基金重仓数据数据库...")
    print("=" * 50)
    
    # 创建数据库
    if create_funds_awkward_database():
        print("\n" + "=" * 50)
        print("🧪 测试数据库连接...")
        
        # 测试连接
        if test_database_connection():
            print("\n🎉 数据库创建和连接测试全部成功！")
            print("\n📋 数据库信息:")
            print(f"   数据库名: funds_awkward")
            print(f"   字符集: utf8mb4")
            print(f"   排序规则: utf8mb4_unicode_ci")
            print(f"   示例表: awkward_20241201")
        else:
            print("\n❌ 数据库连接测试失败！")
    else:
        print("\n❌ 数据库创建失败！") 