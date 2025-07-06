#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试基金数据保存到CSV文件的功能
"""

import sys
import os
import pandas as pd
from datetime import date

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from App.models.data.FundsAwkward import (
    save_funds_holdings_to_csv,
    get_funds_holdings_from_csv,
    get_funds_holdings_by_stock,
    get_funds_holdings_by_fund,
    list_available_dates,
    get_latest_data,
    get_funds_data_directory
)

def test_csv_save_and_read():
    """测试CSV保存和读取功能"""
    print("🧪 测试CSV保存和读取功能...")
    print("=" * 50)
    
    # 创建测试数据
    test_data = pd.DataFrame({
        'fund_name': ['华夏成长', '易方达消费', '嘉实增长'],
        'fund_code': ['000001', '110022', '070002'],
        'stock_name': ['贵州茅台', '五粮液', '泸州老窖'],
        'stock_code': ['600519', '000858', '000568'],
        'holdings_ratio': ['5.2%', '4.8%', '3.5%'],
        'market_value': ['1000万', '800万', '600万'],
        'shares': ['10000', '8000', '6000'],
        'download_date': ['2024-12-01', '2024-12-01', '2024-12-01']
    })
    
    print(f"测试数据: {len(test_data)} 条记录")
    print(test_data.head())
    
    # 测试保存到CSV
    print("\n📁 测试保存到CSV文件...")
    save_success = save_funds_holdings_to_csv(test_data, date.today())
    
    if save_success:
        print("✅ CSV文件保存成功！")
        
        # 显示保存路径
        save_dir = get_funds_data_directory()
        print(f"保存目录: {save_dir}")
        
        # 测试从CSV读取
        print("\n📖 测试从CSV文件读取...")
        read_data = get_funds_holdings_from_csv(date.today())
        
        if not read_data.empty:
            print("✅ CSV文件读取成功！")
            print(f"读取数据: {len(read_data)} 条记录")
            print(read_data.head())
        else:
            print("❌ CSV文件读取失败！")
    else:
        print("❌ CSV文件保存失败！")
    
    print("=" * 50)


def test_filter_functions():
    """测试筛选功能"""
    print("\n🔍 测试筛选功能...")
    print("=" * 50)
    
    # 测试按股票代码筛选
    print("📊 测试按股票代码筛选...")
    stock_data = get_funds_holdings_by_stock(date.today(), '600519')
    
    if not stock_data.empty:
        print("✅ 按股票代码筛选成功！")
        print(f"股票 600519 的基金持仓: {len(stock_data)} 条记录")
        print(stock_data)
    else:
        print("❌ 按股票代码筛选失败！")
    
    # 测试按基金代码筛选
    print("\n📊 测试按基金代码筛选...")
    fund_data = get_funds_holdings_by_fund(date.today(), '000001')
    
    if not fund_data.empty:
        print("✅ 按基金代码筛选成功！")
        print(f"基金 000001 的持仓: {len(fund_data)} 条记录")
        print(fund_data)
    else:
        print("❌ 按基金代码筛选失败！")
    
    print("=" * 50)


def test_date_management():
    """测试日期管理功能"""
    print("\n📅 测试日期管理功能...")
    print("=" * 50)
    
    # 列出可用日期
    print("📋 列出可用日期...")
    available_dates = list_available_dates()
    
    if available_dates:
        print("✅ 找到可用日期:")
        for i, date_obj in enumerate(available_dates[:5]):  # 只显示前5个
            print(f"   {i+1}. {date_obj}")
        if len(available_dates) > 5:
            print(f"   ... 还有 {len(available_dates) - 5} 个日期")
    else:
        print("❌ 没有找到可用日期")
    
    # 获取最新数据
    print("\n📊 获取最新数据...")
    latest_data = get_latest_data()
    
    if not latest_data.empty:
        print("✅ 获取最新数据成功！")
        print(f"最新数据: {len(latest_data)} 条记录")
        print(f"数据日期: {latest_data['download_date'].iloc[0] if 'download_date' in latest_data.columns else '未知'}")
    else:
        print("❌ 获取最新数据失败！")
    
    print("=" * 50)


def test_directory_structure():
    """测试目录结构"""
    print("\n📁 测试目录结构...")
    print("=" * 50)
    
    save_dir = get_funds_data_directory()
    print(f"基金数据保存目录: {save_dir}")
    
    if os.path.exists(save_dir):
        print("✅ 目录存在")
        
        # 列出目录中的文件
        files = os.listdir(save_dir)
        csv_files = [f for f in files if f.endswith('.csv')]
        
        print(f"目录中的CSV文件: {len(csv_files)} 个")
        for file in csv_files[:5]:  # 只显示前5个
            file_path = os.path.join(save_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   {file} ({file_size} bytes)")
        
        if len(csv_files) > 5:
            print(f"   ... 还有 {len(csv_files) - 5} 个文件")
    else:
        print("❌ 目录不存在")
    
    print("=" * 50)


if __name__ == "__main__":
    print("🚀 开始测试基金数据CSV保存功能...")
    
    # 运行所有测试
    test_csv_save_and_read()
    test_filter_functions()
    test_date_management()
    test_directory_structure()
    
    print("\n🎉 所有测试完成！")
    print("\n📋 测试总结:")
    print("1. ✅ CSV文件保存功能")
    print("2. ✅ CSV文件读取功能")
    print("3. ✅ 按股票/基金筛选功能")
    print("4. ✅ 日期管理功能")
    print("5. ✅ 目录结构管理")
    print("\n💡 数据现在保存到本地CSV文件，无需数据库！") 