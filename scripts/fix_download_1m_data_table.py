#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 download_1m_data 表结构
添加缺少的字段以匹配模型定义
"""

import sys
import os
from sqlalchemy import text, inspect
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from App.exts import db
from App import create_app

def check_table_structure():
    """检查表结构"""
    try:
        # 检查表是否存在
        result = db.session.execute(text("""
            SELECT COUNT(*) as table_exists 
            FROM information_schema.tables 
            WHERE table_schema = 'quanttradingsystem' 
            AND table_name = 'download_1m_data'
        """))
        
        table_exists = result.fetchone()[0]
        if not table_exists:
            print("❌ 表 download_1m_data 不存在")
            return False
            
        print("✅ 表 download_1m_data 存在")
        
        # 检查现有字段
        result = db.session.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'download_1m_data'
            ORDER BY ORDINAL_POSITION
        """))
        
        existing_columns = {row[0] for row in result.fetchall()}
        print(f"现有字段: {', '.join(sorted(existing_columns))}")
        
        return existing_columns
        
    except Exception as e:
        print(f"❌ 检查表结构时发生错误: {e}")
        return False

def add_missing_columns(existing_columns):
    """添加缺少的字段"""
    try:
        # 需要添加的字段
        required_columns = {
            'download_status': "VARCHAR(20) DEFAULT 'pending' COMMENT '下载状态'",
            'error_message': "TEXT COMMENT '错误信息'",
            'created_at': "DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'",
            'updated_at': "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'"
        }
        
        # 找出缺少的字段
        missing_columns = {col: definition for col, definition in required_columns.items() 
                          if col not in existing_columns}
        
        if not missing_columns:
            print("✅ 所有必需字段都已存在")
            return True
            
        print(f"需要添加的字段: {', '.join(missing_columns.keys())}")
        
        # 添加缺少的字段
        for column_name, definition in missing_columns.items():
            try:
                sql = f"ALTER TABLE download_1m_data ADD COLUMN {column_name} {definition}"
                print(f"执行SQL: {sql}")
                db.session.execute(text(sql))
                print(f"✅ 成功添加字段: {column_name}")
            except Exception as e:
                print(f"❌ 添加字段 {column_name} 失败: {e}")
                return False
        
        # 添加索引
        try:
            index_sql = """
            ALTER TABLE download_1m_data 
            ADD INDEX IF NOT EXISTS idx_download_status (download_status),
            ADD INDEX IF NOT EXISTS idx_created_at (created_at),
            ADD INDEX IF NOT EXISTS idx_updated_at (updated_at)
            """
            db.session.execute(text(index_sql))
            print("✅ 成功添加索引")
        except Exception as e:
            print(f"⚠️ 添加索引时发生错误: {e}")
        
        db.session.commit()
        print("✅ 数据库迁移完成")
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 添加字段时发生错误: {e}")
        return False

def verify_migration():
    """验证迁移结果"""
    try:
        result = db.session.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'download_1m_data'
            AND COLUMN_NAME IN ('download_status', 'error_message', 'created_at', 'updated_at')
            ORDER BY COLUMN_NAME
        """))
        
        columns = result.fetchall()
        print("\n验证迁移结果:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (默认值: {col[3]}, 注释: {col[4]})")
            
        return len(columns) == 4
        
    except Exception as e:
        print(f"❌ 验证迁移结果时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🔧 开始修复 download_1m_data 表结构...")
    print(f"时间: {datetime.now()}")
    print("-" * 50)
    
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        try:
            # 检查表结构
            existing_columns = check_table_structure()
            if existing_columns is False:
                return False
                
            # 添加缺少的字段
            if not add_missing_columns(existing_columns):
                return False
                
            # 验证迁移结果
            if not verify_migration():
                return False
                
            print("\n🎉 表结构修复完成！")
            return True
            
        except Exception as e:
            print(f"❌ 修复过程中发生错误: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 