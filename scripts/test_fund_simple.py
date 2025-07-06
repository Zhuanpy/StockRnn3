#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的基金数据下载测试
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import date

def test_fund_download():
    """测试基金数据下载"""
    fund_code = "003834"  # 华夏能源革新
    url = f"http://fund.eastmoney.com/{fund_code}.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
            
            # 查找股票持仓表格
            stock_table = soup.find('table', class_='ui-table-hover')
            if stock_table:
                stock_rows = stock_table.find_all('tr')[1:]
                stocks = []
                
                for row in stock_rows:
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        stock_link = cells[0].find('a')
                        if stock_link:
                            stock_name = stock_link.get_text(strip=True)
                            stock_href = stock_link.get('href', '')
                            
                            # 提取股票代码
                            stock_code = None
                            if '/unify/r/' in stock_href:
                                code_match = re.search(r'/unify/r/\d+\.(\d{6})', stock_href)
                                if code_match:
                                    stock_code = code_match.group(1)
                            
                            # 提取持仓占比
                            position_text = cells[1].get_text(strip=True)
                            position = position_text.replace('%', '') if '%' in position_text else '0'
                            
                            if stock_code and stock_name:
                                stocks.append({
                                    'stock_code': stock_code,
                                    'stock_name': stock_name,
                                    'position': float(position),
                                    'fund_code': fund_code
                                })
                
                if stocks:
                    # 创建DataFrame
                    data = pd.DataFrame(stocks)
                    data['fund_name'] = '华夏能源革新'
                    data['download_date'] = date.today().strftime('%Y-%m-%d')
                    data['market_value'] = 'N/A'
                    data['shares'] = 'N/A'
                    
                    # 重命名列
                    data = data.rename(columns={'position': 'holdings_ratio'})
                    data = data[['stock_name', 'stock_code', 'fund_name', 'fund_code', 'download_date', 'holdings_ratio', 'market_value', 'shares']]
                    
                    print(f"成功下载 {len(data)} 条股票数据")
                    print("数据预览:")
                    print(data.head())
                    
                    # 保存到CSV
                    csv_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'funds_holdings')
                    os.makedirs(csv_dir, exist_ok=True)
                    
                    csv_filename = f"test_funds_{date.today().strftime('%Y%m%d')}.csv"
                    csv_path = os.path.join(csv_dir, csv_filename)
                    
                    data.to_csv(csv_path, index=False, encoding='utf-8-sig')
                    print(f"数据已保存到: {csv_path}")
                    
                    return True
                else:
                    print("未提取到股票数据")
                    return False
            else:
                print("未找到股票持仓表格")
                return False
        else:
            print(f"页面访问失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"下载出错: {e}")
        return False

if __name__ == "__main__":
    test_fund_download() 