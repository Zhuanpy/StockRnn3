#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查基金数据表
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def check_funds_table():
    """检查基金数据表"""
    
    # 创建数据库连接
    engine = create_engine(Config.get_database_uri("quanttradingsystem"))
    
    try:
        # 检查recordtopfunds500表
        print("=" * 50)
        print("检查 quanttradingsystem.recordtopfunds500 表")
        print("=" * 50)
        
        # 查询表结构
        with engine.connect() as conn:
            result = conn.execute(text("DESCRIBE recordtopfunds500"))
            columns = result.fetchall()
            print("表结构：")
            for col in columns:
                print(f"  {col[0]} - {col[1]} - {col[2]}")
            print()
        
        # 查询数据数量
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) as total FROM recordtopfunds500"))
            total = result.fetchone()[0]
            print(f"总记录数：{total}")
            
            # 查询状态分布
            result = conn.execute(text("""
                SELECT status, COUNT(*) as count 
                FROM recordtopfunds500 
                GROUP BY status
            """))
            status_dist = result.fetchall()
            print("状态分布：")
            for status, count in status_dist:
                print(f"  {status}: {count}")
            
            # 查询选择状态分布
            result = conn.execute(text("""
                SELECT selection, COUNT(*) as count 
                FROM recordtopfunds500 
                GROUP BY selection
            """))
            selection_dist = result.fetchall()
            print("选择状态分布：")
            for selection, count in selection_dist:
                print(f"  {selection}: {count}")
            
            # 查询前10条记录
            result = conn.execute(text("""
                SELECT id, name, code, selection, status, date 
                FROM recordtopfunds500 
                LIMIT 10
            """))
            records = result.fetchall()
            print("\n前10条记录：")
            for record in records:
                print(f"  ID:{record[0]} | {record[1]} ({record[2]}) | 选择:{record[3]} | 状态:{record[4]} | 日期:{record[5]}")
        
        print("\n" + "=" * 50)
        print("检查完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"检查表时发生错误: {e}")

if __name__ == "__main__":
    check_funds_table() 