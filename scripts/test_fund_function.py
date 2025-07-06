#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基金下载函数调用
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_function_call():
    """测试函数调用"""
    try:
        # 导入模块
        from App.routes.data.download_top500_funds_awkward import download_single_fund_data
        
        print("✅ 成功导入 download_single_fund_data 函数")
        
        # 测试函数调用
        fund_code = "001072"
        print(f"🔍 测试基金: {fund_code}")
        
        result = download_single_fund_data(fund_code)
        
        if result:
            print(f"✅ 成功获取 {len(result)} 只股票数据")
            for i, stock in enumerate(result[:3]):
                print(f"  {i+1}. {stock['stock_name']} ({stock['stock_code']}) - 持仓: {stock['position']}%")
        else:
            print("❌ 未获取到数据")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_function_call() 