#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化测试基金下载功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_single_fund():
    """测试单个基金下载"""
    try:
        print("🧪 测试基金下载功能...")
        
        from App.codes.downloads.DlEastMoney import DownloadData
        
        # 测试基金代码
        test_fund_code = "002556"  # 博时丝路主题
        
        print(f"正在下载基金: {test_fund_code}")
        
        data = DownloadData.funds_awkward(test_fund_code)
        
        if data.empty:
            print("⚠️ 下载的数据为空")
            return False
        
        print(f"✅ 成功下载 {len(data)} 条股票数据")
        print("数据预览:")
        print(data.head())
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始简化测试...")
    
    if test_single_fund():
        print("\n🎉 测试成功！")
    else:
        print("\n❌ 测试失败！")
        sys.exit(1) 