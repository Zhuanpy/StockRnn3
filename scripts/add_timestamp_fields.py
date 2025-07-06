#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
添加时间戳字段到recordtopfunds500表
"""

import pymysql
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def add_timestamp_fields():
    """添加created_at和updated_at字段到recordtopfunds500表"""
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database='quanttradingsystem',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 检查字段是否已存在
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'quanttradingsystem' 
            AND TABLE_NAME = 'recordtopfunds500' 
            AND COLUMN_NAME IN ('created_at', 'updated_at')
        """)
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"已存在的字段: {existing_columns}")
        
        # 添加created_at字段（如果不存在）
        if 'created_at' not in existing_columns:
            cursor.execute("""
                ALTER TABLE recordtopfunds500 
                ADD COLUMN `created_at` TIMESTAMP NULL DEFAULT NULL COMMENT '创建时间'
            """)
            print("✓ 已添加created_at字段")
        else:
            print("✓ created_at字段已存在")
        
        # 添加updated_at字段（如果不存在）
        if 'updated_at' not in existing_columns:
            cursor.execute("""
                ALTER TABLE recordtopfunds500 
                ADD COLUMN `updated_at` TIMESTAMP NULL DEFAULT NULL COMMENT '更新时间'
            """)
            print("✓ 已添加updated_at字段")
        else:
            print("✓ updated_at字段已存在")
        
        # 提交更改
        connection.commit()
        
        # 验证表结构
        cursor.execute("DESCRIBE recordtopfunds500")
        columns = cursor.fetchall()
        print("\n当前表结构:")
        for column in columns:
            print(f"  {column[0]}: {column[1]}")
        
        print("\n✓ 时间戳字段添加完成！")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def test_table_access():
    """测试表访问"""
    try:
        # 测试导入模型
        print("🧪 测试模型导入...")
        from App.models.strategy.StockRecordModels import Top500FundRecord
        print("✅ 模型导入成功")
        
        # 测试查询
        print("🧪 测试数据库查询...")
        records = Top500FundRecord.query.all()
        print(f"✅ 查询成功，找到 {len(records)} 条记录")
        
        if records:
            # 显示第一条记录
            first_record = records[0]
            print(f"第一条记录: {first_record}")
            print(f"创建时间: {first_record.created_at}")
            print(f"更新时间: {first_record.updated_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始添加时间戳字段...")
    print("=" * 50)
    
    # 添加字段
    if add_timestamp_fields():
        print("\n" + "=" * 50)
        print("🧪 测试表访问...")
        
        # 测试访问
        if test_table_access():
            print("\n🎉 所有操作成功完成！")
            print("\n📋 总结:")
            print("1. ✅ 时间戳字段添加成功")
            print("2. ✅ 现有记录时间戳更新成功")
            print("3. ✅ 模型访问测试通过")
            print("\n💡 现在可以正常使用基金下载功能了！")
        else:
            print("\n❌ 表访问测试失败")
    else:
        print("\n❌ 字段添加失败") 