#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试基金下载功能 - 使用标准库
"""

import sys
import os
import urllib.request
import urllib.parse
import urllib.error
import json
import re
from html.parser import HTMLParser

def get_page_source(url, headers=None):
    """使用标准库获取页面源码"""
    try:
        req = urllib.request.Request(url)
        
        # 设置默认headers
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive'
        }
        
        if headers:
            default_headers.update(headers)
        
        for key, value in default_headers.items():
            req.add_header(key, value)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read()
            
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
            for encoding in encodings:
                try:
                    return content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            
            # 如果所有编码都失败，使用默认编码
            return content.decode('utf-8', errors='ignore')
            
    except Exception as e:
        print(f"获取页面失败: {e}")
        return None

def extract_stock_data(html_content, fund_code):
    """从HTML中提取股票数据"""
    try:
        stocks = []
        
        # 使用正则表达式查找股票链接和持仓信息
        # 匹配模式: <a href="//quote.eastmoney.com/unify/r/1.688123" title="聚辰股份">聚辰股份</a>
        stock_pattern = r'<a href="//quote\.eastmoney\.com/unify/r/\d+\.(\d{6})" title="([^"]+)">[^<]+</a>'
        
        # 查找所有股票链接
        stock_matches = re.findall(stock_pattern, html_content)
        
        # 查找持仓占比 (在股票链接后面的td中)
        position_pattern = r'<td class="alignRight bold">([^<]+)</td>'
        position_matches = re.findall(position_pattern, html_content)
        
        # 查找涨跌幅
        change_pattern = r'<span class="[^"]*">([^<]+)</span>'
        change_matches = re.findall(change_pattern, html_content)
        
        print(f"找到 {len(stock_matches)} 个股票匹配")
        print(f"找到 {len(position_matches)} 个持仓匹配")
        print(f"找到 {len(change_matches)} 个涨跌幅匹配")
        
        # 组合数据
        for i, (stock_code, stock_name) in enumerate(stock_matches):
            if i < len(position_matches) and i < len(change_matches):
                position = position_matches[i].replace('%', '')
                change = change_matches[i].replace('%', '')
                
                try:
                    stocks.append({
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'position': float(position),
                        'change': float(change),
                        'fund_code': fund_code
                    })
                except ValueError:
                    continue
        
        return stocks
        
    except Exception as e:
        print(f"提取股票数据时出错: {e}")
        return []

def test_fund_download(fund_code):
    """测试单个基金下载"""
    try:
        print(f"\n🔍 测试基金: {fund_code}")
        print("=" * 50)
        
        url = f"http://fund.eastmoney.com/{fund_code}.html"
        print(f"URL: {url}")
        
        # 获取页面源码
        source = get_page_source(url)
        
        if not source:
            print("❌ 页面源码为空")
            return False
        
        print(f"✅ 页面源码长度: {len(source)}")
        
        # 提取股票数据
        stocks = extract_stock_data(source, fund_code)
        
        if stocks:
            print(f"✅ 成功提取 {len(stocks)} 只股票")
            
            # 显示前5只股票
            for i, stock in enumerate(stocks[:5]):
                print(f"  {i+1}. {stock['stock_name']} ({stock['stock_code']}) - 持仓: {stock['position']}% - 涨跌: {stock['change']}%")
            
            # 保存到文件
            import csv
            csv_filename = f"test_fund_{fund_code}.csv"
            with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['stock_code', 'stock_name', 'position', 'change', 'fund_code'])
                writer.writeheader()
                writer.writerows(stocks)
            
            print(f"💾 数据已保存到: {csv_filename}")
            return True
        else:
            print("❌ 未提取到股票数据")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始最终测试基金下载功能...")
    print("=" * 60)
    
    # 测试基金代码
    test_funds = ["001072", "003069", "002556"]
    
    success_count = 0
    for fund_code in test_funds:
        if test_fund_download(fund_code):
            success_count += 1
    
    print(f"\n🎉 测试完成！成功: {success_count}/{len(test_funds)}")

if __name__ == "__main__":
    main() 