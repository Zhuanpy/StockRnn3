#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查recordtopfunds500表的详细结构
"""

import os
import sys
from sqlalchemy import create_engine, text

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def check_table_structure():
    """检查recordtopfunds500表的详细结构"""
    
    # 创建数据库连接
    engine = create_engine(Config.get_database_uri("quanttradingsystem"))
    
    try:
        print("=" * 60)
        print("检查 quanttradingsystem.recordtopfunds500 表结构")
        print("=" * 60)
        
        with engine.connect() as conn:
            # 查询表结构
            result = conn.execute(text("DESCRIBE recordtopfunds500"))
            columns = result.fetchall()
            
            print("表结构详情：")
            print(f"{'字段名':<20} {'类型':<20} {'NULL':<8} {'KEY':<8} {'DEFAULT':<15} {'EXTRA':<10}")
            print("-" * 80)
            
            for col in columns:
                field_name = col[0]
                field_type = col[1]
                is_null = col[2]
                key = col[3]
                default = col[4] if col[4] else 'NULL'
                extra = col[5] if col[5] else ''
                
                print(f"{field_name:<20} {field_type:<20} {is_null:<8} {key:<8} {default:<15} {extra:<10}")
            
            print("\n" + "=" * 60)
            print("数据统计")
            print("=" * 60)
            
            # 查询数据统计
            result = conn.execute(text("SELECT COUNT(*) as total FROM recordtopfunds500"))
            total = result.fetchone()[0]
            print(f"总记录数：{total}")
            
            if total > 0:
                # 查询前5条记录作为示例
                result = conn.execute(text("SELECT * FROM recordtopfunds500 LIMIT 5"))
                records = result.fetchall()
                
                print("\n前5条记录示例：")
                for i, record in enumerate(records, 1):
                    print(f"记录 {i}: {record}")
        
        print("\n" + "=" * 60)
        print("检查完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"检查表结构时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_table_structure() 