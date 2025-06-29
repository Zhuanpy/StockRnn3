#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试创建 record_stock_minute 表的简单脚本
"""

import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    logger.info("🚀 开始测试...")
    
    # 导入必要的模块
    from App.exts import db
    from App.models.data.Stock1m import RecordStockMinute
    
    logger.info("✅ 模块导入成功")
    
    # 测试数据库连接
    try:
        result = db.session.execute("SELECT 1")
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        sys.exit(1)
    
    # 检查表是否存在
    try:
        result = db.session.execute("SHOW TABLES LIKE 'record_stock_minute'")
        if result.fetchone():
            logger.info("✅ record_stock_minute 表已存在")
        else:
            logger.info("📝 record_stock_minute 表不存在，开始创建...")
            
            # 创建表
            RecordStockMinute.__table__.create(db.engine, checkfirst=True)
            logger.info("✅ record_stock_minute 表创建成功！")
            
            # 验证表是否创建成功
            result = db.session.execute("SHOW TABLES LIKE 'record_stock_minute'")
            if result.fetchone():
                logger.info("✅ 表验证成功")
                
                # 显示表结构
                result = db.session.execute("DESCRIBE record_stock_minute")
                columns = result.fetchall()
                logger.info("📋 表结构：")
                for column in columns:
                    logger.info(f"  {column[0]} - {column[1]} - {column[2]} - {column[3]} - {column[4]} - {column[5]}")
            else:
                logger.error("❌ 表创建失败")
                
    except Exception as e:
        logger.error(f"❌ 操作表时发生错误: {e}")
        
except Exception as e:
    logger.error(f"❌ 脚本执行失败: {e}")
    import traceback
    traceback.print_exc() 