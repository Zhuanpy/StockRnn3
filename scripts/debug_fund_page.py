#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试基金页面结构
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def debug_fund_page(fund_code="002556"):
    """调试基金页面结构"""
    try:
        print(f"🔍 调试基金页面: {fund_code}")
        print("=" * 50)
        
        from App.codes.downloads.download_utils import page_source
        from config import Config
        from bs4 import BeautifulSoup as soup
        
        url = Config.get_eastmoney_urls('funds_awkward').format(fund_code)
        headers = Config.get_eastmoney_headers('funds_awkward')
        
        print(f"URL: {url}")
        
        # 获取页面源码
        source = page_source(url=url, headers=headers)
        
        if not source:
            print("❌ 页面源码为空")
            return
        
        print(f"✅ 页面源码长度: {len(source)}")
        
        # 解析HTML
        soup_obj = soup(source, 'html.parser')
        
        # 查找所有表格
        tables = soup_obj.find_all("table")
        print(f"📊 找到 {len(tables)} 个表格")
        
        for i, table in enumerate(tables):
            print(f"\n--- 表格 {i+1} ---")
            
            # 查找tbody
            tbody = table.find("tbody")
            if tbody:
                print(f"✅ 表格 {i+1} 有tbody")
                
                # 查找所有行
                rows = tbody.find_all("tr")
                print(f"📋 表格 {i+1} 有 {len(rows)} 行")
                
                # 分析前几行
                for j, row in enumerate(rows[:3]):  # 只分析前3行
                    print(f"\n  行 {j+1}:")
                    tds = row.find_all("td")
                    print(f"    TD数量: {len(tds)}")
                    
                    for k, td in enumerate(tds):
                        text = td.get_text(strip=True)
                        print(f"    TD{k+1}: '{text}'")
                        
                        # 检查是否有链接
                        links = td.find_all("a")
                        if links:
                            for link in links:
                                href = link.get('href', '')
                                print(f"      链接: {href}")
            else:
                print(f"❌ 表格 {i+1} 没有tbody")
        
        # 查找特定的class
        print(f"\n🔍 查找特定class...")
        
        # 查找class="tol"的元素
        tol_elements = soup_obj.find_all(class_="tol")
        print(f"class='tol' 元素数量: {len(tol_elements)}")
        for i, elem in enumerate(tol_elements[:5]):
            print(f"  tol{i+1}: '{elem.get_text(strip=True)}'")
        
        # 查找包含股票代码的元素
        print(f"\n🔍 查找股票代码...")
        import re
        
        # 查找6位数字
        pattern = r'\b\d{6}\b'
        matches = re.findall(pattern, source)
        print(f"6位数字匹配: {matches[:10]}")  # 只显示前10个
        
        # 查找股票链接
        stock_links = soup_obj.find_all("a", href=re.compile(r'/stock/'))
        print(f"股票链接数量: {len(stock_links)}")
        for i, link in enumerate(stock_links[:5]):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  股票链接{i+1}: {text} -> {href}")
        
        return True
        
    except Exception as e:
        print(f"❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_funds():
    """测试多个基金"""
    test_funds = ["002556", "001072", "003834"]
    
    for fund_code in test_funds:
        print(f"\n{'='*60}")
        print(f"测试基金: {fund_code}")
        print(f"{'='*60}")
        
        if not debug_fund_page(fund_code):
            print(f"基金 {fund_code} 调试失败")
        
        print("\n" + "-"*60)

if __name__ == "__main__":
    print("🚀 开始调试基金页面结构...")
    
    # 调试单个基金
    debug_fund_page("002556")
    
    # 或者调试多个基金
    # test_multiple_funds() 