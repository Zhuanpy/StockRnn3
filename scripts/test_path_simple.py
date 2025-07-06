#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单的路径测试脚本，不依赖Flask
"""

import os

def test_path_calculation():
    """测试路径计算"""
    print("🔍 测试路径计算...")
    print("=" * 60)
    
    # 当前工作目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 模拟从 FundsAwkward.py 文件计算路径
    # 文件位置: App/models/data/FundsAwkward.py
    funds_file = os.path.join(current_dir, 'App', 'models', 'data', 'FundsAwkward.py')
    print(f"FundsAwkward.py 文件路径: {funds_file}")
    print(f"文件是否存在: {os.path.exists(funds_file)}")
    
    if os.path.exists(funds_file):
        # 计算项目根目录 (4层dirname)
        # App/models/data/FundsAwkward.py -> App/models/data -> App/models -> App -> 项目根目录
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
            
            # 创建测试文件
            test_file = os.path.join(funds_dir, "test_path.txt")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("路径测试文件")
            print(f"测试文件已创建: {test_file}")
            
            # 重新列出文件
            files = os.listdir(funds_dir)
            print(f"创建测试文件后的目录内容: {files}")
            
            # 清理测试文件
            os.remove(test_file)
            print("测试文件已清理")
    
    # 检查项目根目录下的data目录
    data_dir = os.path.join(current_dir, 'data')
    print(f"\n项目data目录: {data_dir}")
    print(f"项目data目录是否存在: {os.path.exists(data_dir)}")
    
    if os.path.exists(data_dir):
        subdirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        print(f"data目录下的子目录: {subdirs}")
        
        # 检查funds_holdings目录
        funds_holdings_dir = os.path.join(data_dir, 'funds_holdings')
        print(f"\nfunds_holdings目录: {funds_holdings_dir}")
        print(f"funds_holdings目录是否存在: {os.path.exists(funds_holdings_dir)}")
        
        if os.path.exists(funds_holdings_dir):
            files = os.listdir(funds_holdings_dir)
            print(f"funds_holdings目录中的文件: {files}")
    
    print("=" * 60)

if __name__ == "__main__":
    test_path_calculation() 