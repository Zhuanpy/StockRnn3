#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
检查基金数据和1分钟数据的保存路径
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_paths():
    """检查各种数据保存路径"""
    print("🔍 检查数据保存路径...")
    print("=" * 60)
    
    # 获取当前工作目录
    current_dir = os.getcwd()
    print(f"当前工作目录: {current_dir}")
    
    # 检查基金数据路径
    try:
        from App.models.data.FundsAwkward import get_funds_data_directory
        funds_dir = get_funds_data_directory()
        print(f"\n📁 基金数据保存路径: {funds_dir}")
        print(f"基金数据目录是否存在: {os.path.exists(funds_dir)}")
        
        if os.path.exists(funds_dir):
            files = os.listdir(funds_dir)
            print(f"基金数据目录中的文件: {files}")
    except Exception as e:
        print(f"❌ 获取基金数据路径失败: {e}")
    
    # 检查1分钟数据路径
    try:
        # 1分钟数据通常保存在 data/data/quarters/ 目录
        minute_data_dir = os.path.join(current_dir, 'data', 'data', 'quarters')
        print(f"\n📁 1分钟数据保存路径: {minute_data_dir}")
        print(f"1分钟数据目录是否存在: {os.path.exists(minute_data_dir)}")
        
        if os.path.exists(minute_data_dir):
            files = os.listdir(minute_data_dir)
            print(f"1分钟数据目录中的文件: {files[:10]}...")  # 只显示前10个文件
    except Exception as e:
        print(f"❌ 获取1分钟数据路径失败: {e}")
    
    # 检查项目根目录下的data目录
    data_dir = os.path.join(current_dir, 'data')
    print(f"\n📁 项目data目录: {data_dir}")
    print(f"项目data目录是否存在: {os.path.exists(data_dir)}")
    
    if os.path.exists(data_dir):
        subdirs = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
        print(f"data目录下的子目录: {subdirs}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    check_paths() 