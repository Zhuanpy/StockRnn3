#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复外键问题脚本
检查并修复 record_stock_minute 表的外键约束
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
        print("🔍 检查表结构...")
        
        # 检查 stock_market_data 表
        result = db.session.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'stock_market_data'
            AND COLUMN_NAME = 'id'
        """))
        
        stock_table_info = result.fetchone()
        if stock_table_info:
            print(f"stock_market_data.id: {stock_table_info[0]} - {stock_table_info[1]} - {stock_table_info[2]} - {stock_table_info[3]}")
        else:
            print("❌ stock_market_data 表不存在或没有 id 字段")
            return False
        
        # 检查 record_stock_minute 表
        result = db.session.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'record_stock_minute'
            AND COLUMN_NAME = 'stock_code_id'
        """))
        
        record_table_info = result.fetchone()
        if record_table_info:
            print(f"record_stock_minute.stock_code_id: {record_table_info[0]} - {record_table_info[1]} - {record_table_info[2]} - {record_table_info[3]}")
        else:
            print("❌ record_stock_minute 表不存在或没有 stock_code_id 字段")
            return False
        
        # 检查外键约束
        result = db.session.execute(text("""
            SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'record_stock_minute'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """))
        
        foreign_keys = result.fetchall()
        if foreign_keys:
            print("现有外键约束:")
            for fk in foreign_keys:
                print(f"  {fk[0]}: {fk[1]} -> {fk[2]}.{fk[3]}")
        else:
            print("⚠️ 没有外键约束")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查表结构时发生错误: {e}")
        return False

def check_and_create_indexes():
    """检查并创建必要的索引"""
    try:
        print("\n🔍 检查索引...")
        
        # 检查 stock_market_data 表的 id 字段索引
        result = db.session.execute(text("""
            SELECT INDEX_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'stock_market_data'
            AND COLUMN_NAME = 'id'
        """))
        
        indexes = result.fetchall()
        if indexes:
            print("stock_market_data.id 的索引:")
            for idx in indexes:
                print(f"  {idx[0]}: {idx[1]}")
        else:
            print("⚠️ stock_market_data.id 没有索引")
            # 创建索引
            try:
                sql = "ALTER TABLE stock_market_data ADD INDEX idx_id (id)"
                db.session.execute(text(sql))
                db.session.commit()
                print("✅ 成功创建 stock_market_data.id 索引")
            except Exception as e:
                print(f"❌ 创建 stock_market_data.id 索引时发生错误: {e}")
                return False
        
        # 检查 record_stock_minute 表的 stock_code_id 字段索引
        result = db.session.execute(text("""
            SELECT INDEX_NAME, COLUMN_NAME
            FROM INFORMATION_SCHEMA.STATISTICS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'record_stock_minute'
            AND COLUMN_NAME = 'stock_code_id'
        """))
        
        indexes = result.fetchall()
        if indexes:
            print("record_stock_minute.stock_code_id 的索引:")
            for idx in indexes:
                print(f"  {idx[0]}: {idx[1]}")
        else:
            print("⚠️ record_stock_minute.stock_code_id 没有索引")
            # 创建索引
            try:
                sql = "ALTER TABLE record_stock_minute ADD INDEX idx_stock_code_id (stock_code_id)"
                db.session.execute(text(sql))
                db.session.commit()
                print("✅ 成功创建 record_stock_minute.stock_code_id 索引")
            except Exception as e:
                print(f"❌ 创建索引时发生错误: {e}")
                return False
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 检查索引时发生错误: {e}")
        return False

def drop_foreign_key_constraints():
    """删除外键约束"""
    try:
        print("\n🗑️ 删除外键约束...")
        
        # 获取外键约束名称
        result = db.session.execute(text("""
            SELECT CONSTRAINT_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'record_stock_minute'
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """))
        
        constraints = [row[0] for row in result.fetchall()]
        
        if constraints:
            for constraint in constraints:
                try:
                    sql = f"ALTER TABLE record_stock_minute DROP FOREIGN KEY {constraint}"
                    db.session.execute(text(sql))
                    print(f"✅ 删除外键约束: {constraint}")
                except Exception as e:
                    print(f"⚠️ 删除外键约束 {constraint} 时出错: {e}")
            
            db.session.commit()
            print("✅ 外键约束删除完成")
        else:
            print("ℹ️ 没有外键约束需要删除")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 删除外键约束时发生错误: {e}")
        return False

def fix_column_data_type():
    """修复列数据类型"""
    try:
        print("\n🔧 修复列数据类型...")
        
        # 检查 stock_code_id 的数据类型
        result = db.session.execute(text("""
            SELECT DATA_TYPE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'record_stock_minute'
            AND COLUMN_NAME = 'stock_code_id'
        """))
        
        current_type = result.fetchone()[0]
        print(f"当前 stock_code_id 数据类型: {current_type}")
        
        # 如果类型不是 BIGINT，则修改
        if current_type.upper() != 'BIGINT':
            try:
                sql = "ALTER TABLE record_stock_minute MODIFY COLUMN stock_code_id BIGINT NOT NULL COMMENT '股票代码ID'"
                db.session.execute(text(sql))
                db.session.commit()
                print("✅ 成功修改 stock_code_id 数据类型为 BIGINT")
            except Exception as e:
                print(f"❌ 修改数据类型时发生错误: {e}")
                return False
        else:
            print("ℹ️ stock_code_id 数据类型已经是 BIGINT")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 修复数据类型时发生错误: {e}")
        return False

def add_foreign_key_constraint():
    """添加外键约束"""
    try:
        print("\n🔗 添加外键约束...")
        
        # 检查是否已存在外键约束
        result = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'record_stock_minute'
            AND REFERENCED_TABLE_NAME = 'stock_market_data'
        """))
        
        if result.fetchone()[0] > 0:
            print("ℹ️ 外键约束已存在")
            return True
        
        # 添加外键约束
        try:
            sql = """
            ALTER TABLE record_stock_minute 
            ADD CONSTRAINT fk_record_stock_minute_stock_code_id 
            FOREIGN KEY (stock_code_id) REFERENCES stock_market_data(id) ON DELETE CASCADE
            """
            db.session.execute(text(sql))
            db.session.commit()
            print("✅ 成功添加外键约束")
        except Exception as e:
            print(f"❌ 添加外键约束时发生错误: {e}")
            return False
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 添加外键约束时发生错误: {e}")
        return False

def verify_fix():
    """验证修复结果"""
    try:
        print("\n✅ 验证修复结果...")
        
        # 检查表结构
        result = db.session.execute(text("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'record_stock_minute'
            AND COLUMN_NAME = 'stock_code_id'
        """))
        
        column_info = result.fetchone()
        if column_info:
            print(f"stock_code_id 字段: {column_info[0]} - {column_info[1]} - {column_info[2]}")
        
        # 检查外键约束
        result = db.session.execute(text("""
            SELECT CONSTRAINT_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
            FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'record_stock_minute'
            AND REFERENCED_TABLE_NAME = 'stock_market_data'
        """))
        
        foreign_key = result.fetchone()
        if foreign_key:
            print(f"外键约束: {foreign_key[0]} - {foreign_key[1]} -> {foreign_key[2]}.{foreign_key[3]}")
            print("✅ 外键约束修复成功")
        else:
            print("⚠️ 外键约束未创建")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证修复结果时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🔧 开始修复外键问题")
    print(f"时间: {datetime.now()}")
    print("-" * 50)
    
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        try:
            # 检查表结构
            if not check_table_structure():
                return False
            
            # 检查并创建索引
            if not check_and_create_indexes():
                return False
            
            # 删除现有外键约束
            if not drop_foreign_key_constraints():
                return False
            
            # 修复数据类型
            if not fix_column_data_type():
                return False
            
            # 添加外键约束
            if not add_foreign_key_constraint():
                return False
            
            # 验证修复结果
            if not verify_fix():
                return False
            
            print("\n🎉 外键问题修复完成！")
            return True
            
        except Exception as e:
            print(f"❌ 修复过程中发生错误: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 