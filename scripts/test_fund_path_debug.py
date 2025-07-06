#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
调试基金数据路径计算
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fund_path_debug():
    """调试基金数据路径计算"""
    print("🔍 调试基金数据路径计算...")
    print("=" * 60)
    
    # 当前工作目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 模拟从 FundsAwkward.py 文件计算路径
    funds_file = os.path.join(current_dir, 'App', 'models', 'data', 'FundsAwkward.py')
    print(f"FundsAwkward.py 文件路径: {funds_file}")
    print(f"文件是否存在: {os.path.exists(funds_file)}")
    
    if os.path.exists(funds_file):
        # 逐步计算路径
        abs_path = os.path.abspath(funds_file)
        print(f"绝对路径: {abs_path}")
        
        # 4层dirname计算
        dir1 = os.path.dirname(abs_path)  # App/models/data
        dir2 = os.path.dirname(dir1)      # App/models
        dir3 = os.path.dirname(dir2)      # App
        dir4 = os.path.dirname(dir3)      # 项目根目录
        
        print(f"第1层dirname: {dir1}")
        print(f"第2层dirname: {dir2}")
        print(f"第3层dirname: {dir3}")
        print(f"第4层dirname: {dir4}")
        
        # 计算基金数据目录
        funds_dir = os.path.join(dir4, 'data', 'funds_holdings')
        print(f"计算出的基金数据目录: {funds_dir}")
        
        # 检查目录是否存在
        print(f"基金数据目录是否存在: {os.path.exists(funds_dir)}")
        
        # 创建目录
        os.makedirs(funds_dir, exist_ok=True)
        print(f"创建目录后是否存在: {os.path.exists(funds_dir)}")
        
        # 列出目录内容
        if os.path.exists(funds_dir):
            files = os.listdir(funds_dir)
            print(f"基金数据目录中的文件: {files}")
    
    # 检查期望的路径
    expected_dir = os.path.join(current_dir, 'data', 'funds_holdings')
    print(f"\n期望的基金数据目录: {expected_dir}")
    print(f"期望目录是否存在: {os.path.exists(expected_dir)}")
    
    if os.path.exists(expected_dir):
        files = os.listdir(expected_dir)
        print(f"期望目录中的文件: {files}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_fund_path_debug() 