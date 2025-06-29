#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试板块代码处理
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_bk_code():
    """测试板块代码处理"""
    try:
        print("🔍 测试板块代码处理...")
        
        from App.codes.downloads.download_utils import UrlCode
        
        # 测试不同类型的代码
        test_codes = [
            'BK0421',  # 板块代码
            '000001',  # 深市股票
            '600000',  # 沪市股票
            '300001',  # 创业板
            'UNKNOWN'  # 未知代码
        ]
        
        for code in test_codes:
            result = UrlCode(code)
            print(f"代码: {code} -> {result}")
        
        # 测试URL格式化
        from App.codes.RnnDataFile.parser import my_url
        
        url_template = my_url('stock_1m_multiple_days')
        print(f"\nURL模板: {url_template}")
        
        # 测试板块代码的URL格式化
        try:
            bk_code = UrlCode('BK0421')
            days = 5
            formatted_url = url_template.format(days, bk_code)
            print(f"板块代码URL: {formatted_url}")
            print("✅ 板块代码URL格式化成功")
        except Exception as e:
            print(f"❌ 板块代码URL格式化失败: {e}")
            return False
        
        print("\n🎉 板块代码测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bk_code()
    sys.exit(0 if success else 1) 