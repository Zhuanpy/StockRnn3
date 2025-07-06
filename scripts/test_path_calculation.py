#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试路径计算
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_path_calculation():
    """测试路径计算"""
    print("🔍 测试路径计算...")
    print("=" * 60)
    
    # 当前工作目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 测试从 FundsAwkward.py 文件计算路径
    funds_file = os.path.join(current_dir, 'App', 'models', 'data', 'FundsAwkward.py')
    print(f"FundsAwkward.py 文件路径: {funds_file}")
    print(f"文件是否存在: {os.path.exists(funds_file)}")
    
    if os.path.exists(funds_file):
        # 计算项目根目录
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(funds_file)))))
        print(f"计算出的项目根目录: {base_dir}")
        
        # 计算基金数据目录
        funds_dir = os.path.join(base_dir, 'data', 'funds_holdings')
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
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_path_calculation() 