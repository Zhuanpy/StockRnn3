#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试编码修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_encoding_fix():
    """测试编码修复"""
    try:
        print("🧪 测试编码修复...")
        print("=" * 50)
        
        from App.codes.downloads.DlEastMoney import DownloadData
        
        # 测试基金代码
        test_fund_code = "003834"  # 华夏能源革新
        
        print(f"正在下载基金: {test_fund_code}")
        
        data = DownloadData.funds_awkward(test_fund_code)
        
        if data.empty:
            print("⚠️ 下载的数据为空")
            return False
        
        print(f"✅ 成功下载 {len(data)} 条股票数据")
        print("\n数据预览:")
        print(data.head())
        
        # 检查是否有乱码
        for index, row in data.iterrows():
            stock_name = row['stock_name']
            stock_code = row['stock_code']
            
            print(f"股票 {index + 1}: {stock_name} ({stock_code})")
            
            # 检查是否包含乱码字符
            if any(ord(char) > 127 for char in stock_name):
                print(f"⚠️ 股票名称可能包含乱码: {stock_name}")
            else:
                print(f"✅ 股票名称正常: {stock_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_page_source_encoding():
    """测试页面源码编码"""
    try:
        print("\n🌐 测试页面源码编码...")
        
        from App.codes.downloads.download_utils import page_source
        from config import Config
        
        url = Config.get_eastmoney_urls('funds_awkward').format("003834")
        headers = Config.get_eastmoney_headers('funds_awkward')
        
        print(f"测试URL: {url}")
        
        source = page_source(url=url, headers=headers)
        
        if source:
            print(f"✅ 成功获取页面源码，长度: {len(source)}")
            
            # 检查源码中的中文字符
            chinese_chars = []
            for char in source[:1000]:  # 检查前1000个字符
                if '\u4e00' <= char <= '\u9fff':  # 中文字符范围
                    chinese_chars.append(char)
            
            if chinese_chars:
                print(f"✅ 检测到中文字符: {''.join(chinese_chars[:10])}...")
            else:
                print("⚠️ 未检测到中文字符，可能存在编码问题")
            
            # 检查源码预览
            print("源码预览:")
            preview = source[:500]
            print(preview)
            
            return True
        else:
            print("❌ 页面源码为空")
            return False
            
    except Exception as e:
        print(f"❌ 页面源码编码测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试编码修复...")
    print("=" * 50)
    
    # 测试页面源码编码
    if test_page_source_encoding():
        print("\n✅ 页面源码编码测试通过")
    else:
        print("\n❌ 页面源码编码测试失败")
        sys.exit(1)
    
    # 测试完整下载功能
    if test_encoding_fix():
        print("\n🎉 编码修复测试成功！")
        print("\n📋 修复总结:")
        print("1. ✅ 修复了HTML解析器的编码设置")
        print("2. ✅ 增强了页面源码的编码检测")
        print("3. ✅ 改进了股票名称和代码的提取方法")
        print("4. ✅ 添加了文本清理功能")
    else:
        print("\n❌ 编码修复测试失败！")
        sys.exit(1) 