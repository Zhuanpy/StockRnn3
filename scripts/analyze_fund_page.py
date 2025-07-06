#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析基金页面结构
"""

import sys
import os
import re

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def analyze_fund_page(fund_code="003069"):
    """详细分析基金页面结构"""
    try:
        print(f"🔍 详细分析基金页面: {fund_code}")
        print("=" * 60)
        
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
            return False
        
        print(f"✅ 页面源码长度: {len(source)}")
        
        # 保存页面源码到文件
        debug_file = f"debug_fund_{fund_code}.html"
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(source)
        print(f"💾 页面源码已保存到: {debug_file}")
        
        # 解析HTML
        soup_obj = soup(source, 'html.parser')
        
        # 1. 查找所有链接
        print(f"\n🔗 分析所有链接...")
        all_links = soup_obj.find_all("a")
        print(f"总链接数量: {len(all_links)}")
        
        # 分类链接
        stock_links = []
        fund_links = []
        other_links = []
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if '/stock/' in href:
                stock_links.append((text, href))
            elif '/fund/' in href or fund_code in href:
                fund_links.append((text, href))
            else:
                other_links.append((text, href))
        
        print(f"股票相关链接: {len(stock_links)}")
        print(f"基金相关链接: {len(fund_links)}")
        print(f"其他链接: {len(other_links)}")
        
        # 显示股票链接
        if stock_links:
            print("\n📈 股票链接:")
            for i, (text, href) in enumerate(stock_links[:10]):
                print(f"  {i+1}. {text} -> {href}")
        else:
            print("\n❌ 未找到股票链接")
        
        # 2. 查找所有表格
        print(f"\n📊 分析表格结构...")
        tables = soup_obj.find_all("table")
        print(f"表格数量: {len(tables)}")
        
        for i, table in enumerate(tables):
            print(f"\n--- 表格 {i+1} ---")
            
            # 查找表头
            thead = table.find("thead")
            if thead:
                headers = [th.get_text(strip=True) for th in thead.find_all(['th', 'td'])]
                print(f"表头: {headers}")
            
            # 查找表体
            tbody = table.find("tbody")
            if tbody:
                rows = tbody.find_all("tr")
                print(f"行数: {len(rows)}")
                
                # 分析前几行
                for j, row in enumerate(rows[:3]):
                    tds = row.find_all('td')
                    td_texts = [td.get_text(strip=True) for td in tds]
                    print(f"  行 {j+1}: {td_texts}")
            else:
                print("无tbody")
        
        # 3. 查找JavaScript数据
        print(f"\n🔍 查找JavaScript数据...")
        
        # 查找script标签
        scripts = soup_obj.find_all("script")
        print(f"Script标签数量: {len(scripts)}")
        
        # 查找可能包含股票数据的script
        for i, script in enumerate(scripts):
            script_content = script.string
            if script_content:
                # 查找包含股票代码的内容
                if 'stock' in script_content.lower() or 'position' in script_content.lower():
                    print(f"\n--- Script {i+1} ---")
                    print(f"内容长度: {len(script_content)}")
                    print(f"内容预览: {script_content[:500]}...")
                    
                    # 查找6位数字（可能的股票代码）
                    numbers = re.findall(r'\b\d{6}\b', script_content)
                    if numbers:
                        print(f"找到的数字: {numbers[:10]}")
        
        # 4. 查找特定class和id
        print(f"\n🎯 查找特定元素...")
        
        # 查找包含"持仓"的元素
        position_elements = soup_obj.find_all(text=lambda text: text and '持仓' in text)
        print(f"包含'持仓'的元素: {len(position_elements)}")
        
        # 查找包含"股票"的元素
        stock_elements = soup_obj.find_all(text=lambda text: text and '股票' in text)
        print(f"包含'股票'的元素: {len(stock_elements)}")
        
        # 查找可能的持仓相关class
        position_classes = ['position', 'holdings', 'stock', 'portfolio']
        for class_name in position_classes:
            elements = soup_obj.find_all(class_=re.compile(class_name, re.I))
            if elements:
                print(f"class包含'{class_name}'的元素: {len(elements)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_funds():
    """测试多个基金"""
    test_funds = ["003069", "002556", "001072"]
    
    for fund_code in test_funds:
        print(f"\n{'='*80}")
        print(f"分析基金: {fund_code}")
        print(f"{'='*80}")
        
        if not analyze_fund_page(fund_code):
            print(f"基金 {fund_code} 分析失败")
        
        print("\n" + "-"*80)

if __name__ == "__main__":
    print("🚀 开始详细分析基金页面结构...")
    
    # 分析单个基金
    analyze_fund_page("003069")
    
    # 或者分析多个基金
    # test_multiple_funds() 