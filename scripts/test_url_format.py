#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试URL格式化
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_url_format():
    """测试URL格式化"""
    try:
        print("🔍 测试URL格式化...")
        
        from config import Config
        from App.codes.RnnDataFile.parser import my_url
        
        # 获取URL模板
        url_template = Config.get_eastmoney_urls('stock_1m_multiple_days')
        print(f"URL模板: {url_template}")
        
        # 模拟参数
        days = 5
        secid = "0.BK0421"  # 模拟股票代码
        
        # 测试格式化
        try:
            formatted_url = url_template.format(days, secid)
            print(f"格式化后的URL: {formatted_url}")
            print("✅ URL格式化成功")
        except Exception as e:
            print(f"❌ URL格式化失败: {e}")
            return False
        
        # 测试parser模块
        try:
            parser_url = my_url('stock_1m_multiple_days')
            test_formatted = parser_url.format(days, secid)
            print(f"Parser模块格式化: {test_formatted}")
            print("✅ Parser模块URL格式化成功")
        except Exception as e:
            print(f"❌ Parser模块URL格式化失败: {e}")
            return False
        
        print("\n🎉 URL格式化测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_url_format()
    sys.exit(0 if success else 1) 