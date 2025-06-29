#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试config中的headers配置
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_config_headers():
    """测试config中的headers配置"""
    try:
        print("🔍 测试config中的headers配置...")
        
        # 测试config中的headers
        from config import Config
        
        headers = Config.get_eastmoney_headers('stock_1m_multiple_days')
        print(f"Headers配置: {headers}")
        
        # 检查关键字段
        required_fields = ['User-Agent', 'Host', 'Accept']
        for field in required_fields:
            if field in headers:
                print(f"✅ {field}: {headers[field]}")
            else:
                print(f"❌ 缺少字段: {field}")
        
        # 测试URL配置
        url = Config.get_eastmoney_urls('stock_1m_multiple_days')
        print(f"\nURL配置: {url}")
        
        # 测试parser模块
        from App.codes.RnnDataFile.parser import my_headers, my_url
        
        parser_headers = my_headers('stock_1m_multiple_days')
        parser_url = my_url('stock_1m_multiple_days')
        
        print(f"\nParser模块测试:")
        print(f"Headers: {parser_headers}")
        print(f"URL: {parser_url}")
        
        if parser_headers and parser_url:
            print("✅ Parser模块配置正确")
        else:
            print("❌ Parser模块配置有问题")
        
        print("\n🎉 配置测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_config_headers()
    sys.exit(0 if success else 1) 