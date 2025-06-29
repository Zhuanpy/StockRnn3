#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据迁移脚本：将 record_stock_minute_copy 表的数据导入到 record_stock_minute 表中
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from sqlalchemy import text

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from App.exts import db
from App.models.data.Stock1m import RecordStockMinute
from run import app  # 导入Flask应用

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_stock_id_by_name(name):
    """
    根据股票名称获取stock_market_data表中的ID
    
    Args:
        name: 股票名称
        
    Returns:
        int: 股票ID，如果未找到返回None
    """
    try:
        # 查询stock_market_data表
        result = db.session.execute(
            text("SELECT id FROM stock_market_data WHERE name = :name"),
            {"name": name}
        )
        row = result.fetchone()
        return row[0] if row else None
    except Exception as e:
        logger.error(f"查询股票ID时发生错误: {e}")
        return None


def migrate_data():
    """
    执行数据迁移
    """
    try:
        logger.info("🚀 开始数据迁移...")
        
        # 1. 检查源表是否存在
        result = db.session.execute(text("SHOW TABLES LIKE 'record_stock_minute_copy'"))
        if not result.fetchone():
            logger.error("❌ 源表 record_stock_minute_copy 不存在")
            return False
            
        # 2. 检查目标表是否存在
        result = db.session.execute(text("SHOW TABLES LIKE 'record_stock_minute'"))
        if not result.fetchone():
            logger.error("❌ 目标表 record_stock_minute 不存在")
            return False
            
        # 3. 获取源表数据
        logger.info("📊 获取源表数据...")
        result = db.session.execute(text("SELECT id, name, start_date, end_date, record_date FROM record_stock_minute_copy"))
        source_data = result.fetchall()
        
        if not source_data:
            logger.info("ℹ️ 源表没有数据需要迁移")
            return True
            
        logger.info(f"📋 找到 {len(source_data)} 条记录需要迁移")
        
        # 4. 开始迁移数据
        success_count = 0
        error_count = 0
        
        for row in source_data:
            try:
                source_id, name, start_date, end_date, record_date = row
                
                # 根据名称查找stock_code_id
                stock_code_id = get_stock_id_by_name(name)
                if stock_code_id is None:
                    logger.warning(f"⚠️ 未找到股票名称 '{name}' 对应的ID，跳过此记录")
                    error_count += 1
                    continue
                
                # 检查目标表中是否已存在相同记录
                existing = db.session.execute(
                    text("SELECT id FROM record_stock_minute WHERE stock_code_id = :stock_code_id"),
                    {"stock_code_id": stock_code_id}
                ).fetchone()
                
                if existing:
                    logger.info(f"ℹ️ 股票ID {stock_code_id} 的记录已存在，跳过")
                    continue
                
                # 插入新记录
                insert_sql = text("""
                INSERT INTO record_stock_minute 
                (stock_code_id, download_status, download_progress, start_date, end_date, record_date, 
                 total_records, downloaded_records, created_at, updated_at)
                VALUES 
                (:stock_code_id, 'pending', 0.0, :start_date, :end_date, :record_date, 
                 0, 0, NOW(), NOW())
                """)
                
                db.session.execute(insert_sql, {
                    "stock_code_id": stock_code_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "record_date": record_date
                })
                
                success_count += 1
                logger.info(f"✅ 成功迁移记录: {name} (ID: {source_id}) -> stock_code_id: {stock_code_id}")
                
            except Exception as e:
                logger.error(f"❌ 迁移记录时发生错误: {e}")
                error_count += 1
                continue
        
        # 5. 提交事务
        db.session.commit()
        
        logger.info(f"🎉 数据迁移完成！")
        logger.info(f"✅ 成功迁移: {success_count} 条记录")
        logger.info(f"❌ 失败记录: {error_count} 条")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 数据迁移过程中发生错误: {e}")
        db.session.rollback()
        return False


def verify_migration():
    """
    验证迁移结果
    """
    try:
        logger.info("🔍 验证迁移结果...")
        
        # 统计源表记录数
        result = db.session.execute(text("SELECT COUNT(*) FROM record_stock_minute_copy"))
        source_count = result.fetchone()[0]
        
        # 统计目标表记录数
        result = db.session.execute(text("SELECT COUNT(*) FROM record_stock_minute"))
        target_count = result.fetchone()[0]
        
        logger.info(f"📊 源表记录数: {source_count}")
        logger.info(f"📊 目标表记录数: {target_count}")
        
        # 显示目标表的一些示例数据
        result = db.session.execute(text("""
            SELECT r.id, r.stock_code_id, r.download_status, r.start_date, r.end_date, s.name
            FROM record_stock_minute r
            LEFT JOIN stock_market_data s ON r.stock_code_id = s.id
            LIMIT 5
        """))
        
        logger.info("📋 目标表示例数据:")
        for row in result.fetchall():
            logger.info(f"  ID: {row[0]}, 股票ID: {row[1]}, 状态: {row[2]}, 开始日期: {row[3]}, 结束日期: {row[4]}, 股票名称: {row[5]}")
            
    except Exception as e:
        logger.error(f"❌ 验证过程中发生错误: {e}")


def main():
    """
    主函数
    """
    logger.info("🚀 开始 record_stock_minute 数据迁移...")
    
    # 使用Flask应用上下文
    with app.app_context():
        # 执行迁移
        if migrate_data():
            # 验证结果
            verify_migration()
            logger.info("✅ 数据迁移任务完成！")
        else:
            logger.error("❌ 数据迁移失败！")


if __name__ == "__main__":
    main() 