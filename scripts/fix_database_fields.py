#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
修复数据库字段问题
"""

import pymysql
import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '651748264Zz',
    'charset': 'utf8mb4'
}

def fix_database_fields():
    """修复数据库字段"""
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='quanttradingsystem',
            charset=DB_CONFIG['charset']
        )
        
        cursor = connection.cursor()
        
        print("🔍 检查表结构...")
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'recordtopfunds500'")
        if not cursor.fetchone():
            print("❌ 表 recordtopfunds500 不存在")
            return False
        
        # 检查字段是否存在
        cursor.execute("DESCRIBE recordtopfunds500")
        columns = [column[0] for column in cursor.fetchall()]
        
        print(f"当前表的字段: {columns}")
        
        # 添加缺失的字段
        fields_to_add = []
        
        if 'created_at' not in columns:
            fields_to_add.append("ADD COLUMN `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'")
        
        if 'updated_at' not in columns:
            fields_to_add.append("ADD COLUMN `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'")
        
        if fields_to_add:
            print(f"📝 需要添加的字段: {len(fields_to_add)} 个")
            
            for field_sql in fields_to_add:
                print(f"正在添加字段: {field_sql}")
                alter_sql = f"ALTER TABLE `recordtopfunds500` {field_sql}"
                cursor.execute(alter_sql)
                print(f"✅ 字段添加成功")
            
            connection.commit()
            print("🎉 所有字段添加完成！")
        else:
            print("✅ 所有字段已存在，无需添加")
        
        # 验证字段是否添加成功
        print("\n🔍 验证表结构...")
        cursor.execute("DESCRIBE recordtopfunds500")
        final_columns = [column[0] for column in cursor.fetchall()]
        print(f"更新后的字段: {final_columns}")
        
        cursor.close()
        connection.close()
        
        print("\n🎉 数据库表结构更新完成！")
        return True
        
    except Exception as e:
        print(f"❌ 更新表结构时发生错误: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始修复数据库字段...")
    print("=" * 50)
    
    if fix_database_fields():
        print("\n🎉 修复完成！现在可以正常使用基金下载功能了！")
    else:
        print("\n❌ 修复失败，请检查错误信息") 