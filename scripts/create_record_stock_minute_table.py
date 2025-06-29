#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建 record_stock_minute 表的脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from App.exts import db
from App.models.data.Stock1m import RecordStockMinute

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_record_stock_minute_table():
    """
    创建 record_stock_minute 表
    """
    try:
        # 创建表
        RecordStockMinute.__table__.create(db.engine, checkfirst=True)
        logger.info("✅ record_stock_minute 表创建成功！")
        
        # 验证表是否创建成功
        result = db.session.execute("SHOW TABLES LIKE 'record_stock_minute'")
        if result.fetchone():
            logger.info("✅ 表验证成功，record_stock_minute 表已存在")
            
            # 显示表结构
            result = db.session.execute("DESCRIBE record_stock_minute")
            columns = result.fetchall()
            logger.info("📋 表结构：")
            for column in columns:
                logger.info(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
        else:
            logger.error("❌ 表创建失败")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 创建表时发生错误: {e}")
        return False


def execute_sql_file():
    """
    执行SQL文件创建表
    """
    try:
        sql_file_path = Path(__file__).parent / "create_record_stock_minute_table.sql"
        
        if not sql_file_path.exists():
            logger.error(f"❌ SQL文件不存在: {sql_file_path}")
            return False
            
        # 读取SQL文件
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
            
        # 执行SQL
        db.session.execute(sql_content)
        db.session.commit()
        
        logger.info("✅ 通过SQL文件创建表成功！")
        return True
        
    except Exception as e:
        logger.error(f"❌ 执行SQL文件时发生错误: {e}")
        db.session.rollback()
        return False


def main():
    """
    主函数
    """
    logger.info("🚀 开始创建 record_stock_minute 表...")
    
    # 方法1：使用SQLAlchemy模型创建表
    logger.info("📝 方法1：使用SQLAlchemy模型创建表")
    if create_record_stock_minute_table():
        logger.info("✅ 表创建完成！")
    else:
        logger.info("⚠️ 方法1失败，尝试方法2...")
        
        # 方法2：执行SQL文件
        logger.info("📝 方法2：执行SQL文件创建表")
        if execute_sql_file():
            logger.info("✅ 表创建完成！")
        else:
            logger.error("❌ 所有方法都失败了")


if __name__ == "__main__":
    main() 