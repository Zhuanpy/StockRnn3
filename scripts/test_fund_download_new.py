#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的基金下载功能
"""

import sys
import os
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def download_fund_data(fund_code):
    """下载单个基金的重仓股票数据"""
    try:
        print(f"正在下载基金 {fund_code} 的数据...")
        
        # 基金详情页面URL
        url = f"http://fund.eastmoney.com/{fund_code}.html"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        
        # 获取页面源码
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"基金 {fund_code} 页面访问失败: {response.status_code}")
            return None
        
        # 使用BeautifulSoup解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找股票持仓表格
        stock_table = soup.find('table', class_='ui-table-hover')
        if not stock_table:
            print(f"基金 {fund_code} 未找到股票持仓表格")
            return None
        
        # 查找所有股票行
        stock_rows = stock_table.find_all('tr')[1:]  # 跳过表头
        
        stocks = []
        for row in stock_rows:
            cells = row.find_all('td')
            if len(cells) >= 3:
                # 提取股票链接和名称
                stock_link = cells[0].find('a')
                if stock_link:
                    stock_name = stock_link.get_text(strip=True)
                    stock_href = stock_link.get('href', '')
                    
                    # 从链接中提取股票代码
                    stock_code = None
                    if '/unify/r/' in stock_href:
                        # 格式: /unify/r/1.688123 或 /unify/r/0.002222
                        code_match = re.search(r'/unify/r/\d+\.(\d{6})', stock_href)
                        if code_match:
                            stock_code = code_match.group(1)
                    
                    # 提取持仓占比
                    position_text = cells[1].get_text(strip=True)
                    position = position_text.replace('%', '') if '%' in position_text else '0'
                    
                    # 提取涨跌幅
                    change_text = cells[2].get_text(strip=True)
                    change = change_text.replace('%', '') if '%' in change_text else '0'
                    
                    if stock_code and stock_name:
                        stocks.append({
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'position': float(position),
                            'change': float(change),
                            'fund_code': fund_code
                        })
        
        if stocks:
            print(f"基金 {fund_code} 成功提取 {len(stocks)} 只股票")
            return stocks
        else:
            print(f"基金 {fund_code} 未提取到股票数据")
            return None
            
    except Exception as e:
        print(f"下载基金 {fund_code} 数据时出错: {e}")
        return None

def test_fund_download():
    """测试基金下载功能"""
    print("🚀 开始测试新的基金下载功能...")
    print("=" * 60)
    
    # 测试基金代码
    test_funds = ["001072", "003069", "002556"]
    
    for fund_code in test_funds:
        print(f"\n{'='*80}")
        print(f"测试基金: {fund_code}")
        print(f"{'='*80}")
        
        # 下载基金数据
        stocks_data = download_fund_data(fund_code)
        
        if stocks_data:
            print(f"✅ 成功下载 {len(stocks_data)} 只股票")
            
            # 转换为DataFrame并显示
            df = pd.DataFrame(stocks_data)
            print("\n📊 股票持仓数据:")
            print(df.to_string(index=False))
            
            # 保存到CSV文件
            csv_filename = f"test_fund_{fund_code}.csv"
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"\n💾 数据已保存到: {csv_filename}")
        else:
            print("❌ 下载失败")
        
        print("\n" + "-"*80)
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_fund_download() 