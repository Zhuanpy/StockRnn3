#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试基金数据保存功能
"""

import sys
import os
import pandas as pd
from datetime import date

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fund_save():
    """测试基金数据保存功能"""
    print("🧪 测试基金数据保存功能...")
    print("=" * 50)
    
    try:
        from App.models.data.FundsAwkward import get_funds_data_directory, save_funds_holdings_to_csv
        
        # 获取基金数据目录
        funds_dir = get_funds_data_directory()
        print(f"基金数据目录: {funds_dir}")
        print(f"目录是否存在: {os.path.exists(funds_dir)}")
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'fund_name': ['华夏成长', '易方达消费'],
            'fund_code': ['000001', '110022'],
            'stock_name': ['贵州茅台', '五粮液'],
            'stock_code': ['600519', '000858'],
            'holdings_ratio': ['5.2%', '4.8%'],
            'market_value': ['1000万', '800万'],
            'shares': ['10000', '8000'],
            'download_date': ['2024-12-01', '2024-12-01']
        })
        
        print(f"\n测试数据: {len(test_data)} 条记录")
        print(test_data.head())
        
        # 保存测试数据
        save_success = save_funds_holdings_to_csv(test_data, date.today())
        
        if save_success:
            print("\n✅ 测试数据保存成功！")
            
            # 检查文件是否真的创建了
            today_str = date.today().strftime('%Y%m%d')
            expected_file = os.path.join(funds_dir, f"funds_holdings_{today_str}.csv")
            print(f"期望文件路径: {expected_file}")
            print(f"文件是否存在: {os.path.exists(expected_file)}")
            
            if os.path.exists(expected_file):
                # 读取并显示保存的数据
                saved_data = pd.read_csv(expected_file, encoding='utf-8-sig')
                print(f"保存的数据行数: {len(saved_data)}")
                print("保存的数据预览:")
                print(saved_data.head())
                
                # 显示目录中的所有文件
                all_files = os.listdir(funds_dir)
                print(f"\n基金数据目录中的所有文件: {all_files}")
            else:
                print("❌ 文件未创建")
        else:
            print("❌ 测试数据保存失败！")
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)

if __name__ == "__main__":
    test_fund_save() 