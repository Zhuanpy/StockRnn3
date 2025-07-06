#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试修复后的基金数据路径
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fund_path():
    """测试基金数据路径"""
    print("🔍 测试基金数据路径...")
    print("=" * 60)
    
    try:
        from App.models.data.FundsAwkward import get_funds_data_directory
        
        # 获取基金数据目录
        funds_dir = get_funds_data_directory()
        print(f"基金数据目录: {funds_dir}")
        print(f"目录是否存在: {os.path.exists(funds_dir)}")
        
        # 创建测试文件
        test_file = os.path.join(funds_dir, "test_file.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("测试文件")
        
        print(f"测试文件已创建: {test_file}")
        print(f"测试文件是否存在: {os.path.exists(test_file)}")
        
        # 列出目录内容
        if os.path.exists(funds_dir):
            files = os.listdir(funds_dir)
            print(f"目录中的文件: {files}")
        
        # 清理测试文件
        if os.path.exists(test_file):
            os.remove(test_file)
            print("测试文件已清理")
        
        # 检查当前工作目录
        current_dir = os.getcwd()
        print(f"\n当前工作目录: {current_dir}")
        
        # 检查项目根目录下的data目录
        data_dir = os.path.join(current_dir, 'data')
        print(f"项目data目录: {data_dir}")
        print(f"项目data目录是否存在: {os.path.exists(data_dir)}")
        
        if os.path.exists(data_dir):
            subdirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
            print(f"data目录下的子目录: {subdirs}")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_fund_path() 