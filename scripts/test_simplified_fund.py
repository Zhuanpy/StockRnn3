#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试简化的基金下载方法
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_simplified_method():
    """测试简化的基金下载方法"""
    try:
        print("🧪 测试简化的基金下载方法...")
        print("=" * 50)
        
        from App.codes.downloads.DlEastMoney import DownloadData
        
        # 测试多个基金
        test_funds = ["002556", "001072", "003834"]
        
        for fund_code in test_funds:
            print(f"\n📥 测试基金: {fund_code}")
            
            try:
                data = DownloadData.funds_awkward(fund_code)
                
                if data.empty:
                    print(f"⚠️ 基金 {fund_code} 无数据")
                else:
                    print(f"✅ 基金 {fund_code} 成功下载 {len(data)} 条股票数据")
                    print("数据预览:")
                    print(data.head())
                    
                    # 检查数据质量
                    for index, row in data.iterrows():
                        stock_name = row['stock_name']
                        stock_code = row['stock_code']
                        print(f"  股票 {index + 1}: {stock_name} ({stock_code})")
                        
            except Exception as e:
                print(f"❌ 基金 {fund_code} 下载失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_page_structure():
    """测试页面结构分析"""
    try:
        print("\n🔍 测试页面结构分析...")
        
        from App.codes.downloads.download_utils import page_source
        from config import Config
        from bs4 import BeautifulSoup as soup
        
        fund_code = "002556"
        url = Config.get_eastmoney_urls('funds_awkward').format(fund_code)
        headers = Config.get_eastmoney_headers('funds_awkward')
        
        print(f"分析基金页面: {fund_code}")
        
        source = page_source(url=url, headers=headers)
        
        if not source:
            print("❌ 页面源码为空")
            return False
        
        soup_obj = soup(source, 'html.parser')
        
        # 查找股票链接
        stock_links = soup_obj.find_all("a", href=lambda href: href and '/stock/' in href)
        print(f"找到 {len(stock_links)} 个股票链接")
        
        # 显示前几个链接
        for i, link in enumerate(stock_links[:5]):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  链接 {i+1}: {text} -> {href}")
        
        return True
        
    except Exception as e:
        print(f"❌ 页面结构分析失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试简化的基金下载方法...")
    
    # 测试页面结构
    if test_page_structure():
        print("\n✅ 页面结构分析成功")
    else:
        print("\n❌ 页面结构分析失败")
    
    # 测试下载功能
    if test_simplified_method():
        print("\n🎉 简化方法测试成功！")
    else:
        print("\n❌ 简化方法测试失败！")
        sys.exit(1) 