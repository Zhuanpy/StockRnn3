#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金数据下载调试脚本
用于测试数据下载和保存过程，检查数据格式和编码问题
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import date

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_download_single_fund(fund_code):
    """测试下载单个基金数据"""
    print(f"正在测试下载基金 {fund_code} 的数据...")
    
    # 基金详情页面URL
    url = f"http://fund.eastmoney.com/{fund_code}.html"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Connection': 'keep-alive'
    }
    
    try:
        # 获取页面源码
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"基金 {fund_code} 页面访问失败: {response.status_code}")
            return None
        
        print(f"页面访问成功，内容长度: {len(response.text)}")
        
        # 使用BeautifulSoup解析
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 查找股票持仓表格
        stock_table = soup.find('table', class_='ui-table-hover')
        if not stock_table:
            print(f"基金 {fund_code} 未找到股票持仓表格")
            # 尝试查找其他可能的表格
            all_tables = soup.find_all('table')
            print(f"页面中共有 {len(all_tables)} 个表格")
            for i, table in enumerate(all_tables):
                print(f"表格 {i+1} 类名: {table.get('class', '无类名')}")
            return None
        
        # 查找所有股票行
        stock_rows = stock_table.find_all('tr')[1:]  # 跳过表头
        print(f"找到 {len(stock_rows)} 行股票数据")
        
        stocks = []
        for i, row in enumerate(stock_rows):
            cells = row.find_all('td')
            print(f"第 {i+1} 行有 {len(cells)} 个单元格")
            
            if len(cells) >= 3:
                # 提取股票链接和名称
                stock_link = cells[0].find('a')
                if stock_link:
                    stock_name = stock_link.get_text(strip=True)
                    stock_href = stock_link.get('href', '')
                    
                    print(f"  股票名称: {stock_name}")
                    print(f"  股票链接: {stock_href}")
                    
                    # 从链接中提取股票代码
                    stock_code = None
                    if '/unify/r/' in stock_href:
                        # 格式: /unify/r/1.688123 或 /unify/r/0.002222
                        code_match = re.search(r'/unify/r/\d+\.(\d{6})', stock_href)
                        if code_match:
                            stock_code = code_match.group(1)
                            print(f"  提取的股票代码: {stock_code}")
                    
                    # 提取持仓占比
                    position_text = cells[1].get_text(strip=True)
                    position = position_text.replace('%', '') if '%' in position_text else '0'
                    print(f"  持仓占比: {position_text} -> {position}")
                    
                    # 提取涨跌幅
                    change_text = cells[2].get_text(strip=True)
                    change = change_text.replace('%', '') if '%' in change_text else '0'
                    print(f"  涨跌幅: {change_text} -> {change}")
                    
                    if stock_code and stock_name:
                        stock_data = {
                            'stock_code': stock_code,
                            'stock_name': stock_name,
                            'position': float(position),
                            'change': float(change),
                            'fund_code': fund_code
                        }
                        stocks.append(stock_data)
                        print(f"  添加股票数据: {stock_data}")
                    else:
                        print(f"  跳过无效数据: stock_code={stock_code}, stock_name={stock_name}")
        
        if stocks:
            print(f"基金 {fund_code} 成功提取 {len(stocks)} 只股票")
            return stocks
        else:
            print(f"基金 {fund_code} 未提取到股票数据")
            return None
            
    except Exception as e:
        print(f"下载基金 {fund_code} 数据时出错: {e}")
        return None

def test_save_to_csv(data, download_date):
    """测试保存数据到CSV"""
    try:
        # 创建下载目录
        csv_dir = os.path.join(project_root, 'data', 'funds_holdings')
        os.makedirs(csv_dir, exist_ok=True)
        
        # 生成文件名
        csv_filename = f"test_funds_holdings_{download_date.strftime('%Y%m%d')}.csv"
        csv_path = os.path.join(csv_dir, csv_filename)
        
        # 检查文件是否已存在
        file_exists = os.path.exists(csv_path)
        print(f"CSV文件路径: {csv_path}")
        print(f"文件已存在: {file_exists}")
        
        # 保存到CSV文件
        data.to_csv(csv_path, mode='a', header=not file_exists, index=False, encoding='utf-8-sig')
        
        print(f"数据已{'追加到' if file_exists else '保存到'}: {csv_path}")
        
        # 读取并显示保存的数据
        saved_data = pd.read_csv(csv_path, encoding='utf-8-sig')
        print(f"保存的数据行数: {len(saved_data)}")
        print("保存的数据预览:")
        print(saved_data.head())
        
        return True
        
    except Exception as e:
        print(f"保存数据到CSV时出错: {e}")
        return False

def main():
    """主函数"""
    print("=== 基金数据下载调试测试 ===")
    
    # 测试基金代码
    test_fund_code = "003834"  # 华夏能源革新
    
    # 下载数据
    stocks_data = test_download_single_fund(test_fund_code)
    
    if stocks_data:
        print(f"\n=== 下载结果 ===")
        print(f"下载到 {len(stocks_data)} 条股票数据")
        
        # 转换为DataFrame
        data = pd.DataFrame(stocks_data)
        print("\n=== DataFrame预览 ===")
        print(data.head())
        print(f"DataFrame形状: {data.shape}")
        print(f"DataFrame列名: {list(data.columns)}")
        
        # 添加基金信息
        data['fund_name'] = '华夏能源革新'
        data['download_date'] = date.today().strftime('%Y-%m-%d')
        data['market_value'] = 'N/A'
        data['shares'] = 'N/A'
        
        print("\n=== 添加基金信息后的数据 ===")
        print(data.head())
        
        # 测试保存到CSV
        print("\n=== 测试保存到CSV ===")
        save_success = test_save_to_csv(data, date.today())
        
        if save_success:
            print("数据保存测试成功!")
        else:
            print("数据保存测试失败!")
    else:
        print("下载测试失败，未获取到数据")

if __name__ == "__main__":
    main() 