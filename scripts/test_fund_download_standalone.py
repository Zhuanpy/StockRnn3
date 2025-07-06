#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立的基金下载测试脚本，不依赖Flask
"""

import sys
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup as soup
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def page_source_standalone(url, headers=None, max_retries=3):
    """独立的页面源码获取函数"""
    session = requests.Session()
    
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    
    if headers:
        default_headers.update(headers)
    
    for i in range(max_retries):
        try:
            response = session.get(
                url,
                headers=default_headers,
                timeout=10,
                verify=False
            )
            
            if response.status_code == 200:
                # 处理编码
                if response.encoding == 'ISO-8859-1':
                    try:
                        return response.content.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            return response.content.decode('gbk')
                        except UnicodeDecodeError:
                            return response.text
                else:
                    return response.text
            else:
                logging.error(f"HTTP error {response.status_code} for URL: {url}")
                
        except Exception as e:
            logging.error(f"Request error: {e}")
            
        if i < max_retries - 1:
            import time
            time.sleep(2)
    
    return None

def test_web_method(fund_code):
    """测试网页解析方法"""
    try:
        print(f"\n🌐 测试网页解析方法 - 基金: {fund_code}")
        
        url = f"http://fund.eastmoney.com/{fund_code}.html"
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'fund.eastmoney.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
        }
        
        print(f"URL: {url}")
        
        source = page_source_standalone(url, headers)
        
        if not source:
            print("❌ 页面源码为空")
            return pd.DataFrame()
        
        print(f"✅ 页面源码长度: {len(source)}")
        
        # 解析HTML
        soup_obj = soup(source, 'html.parser')
        
        # 查找股票链接
        stock_links = soup_obj.find_all("a", href=lambda href: href and '/stock/' in href)
        
        if not stock_links:
            print("❌ 未找到股票链接")
            return pd.DataFrame()
        
        print(f"✅ 找到 {len(stock_links)} 个股票链接")
        
        li_name = []
        li_code = []
        
        for link in stock_links:
            try:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                if '/stock/' in href:
                    code_match = href.split('/stock/')[-1].split('.')[0]
                    if len(code_match) == 6 and code_match.isdigit():
                        stock_code = code_match
                        stock_name = text
                        
                        if stock_name and len(stock_name) > 0:
                            stock_name = stock_name.replace('\n', '').replace('\r', '').replace('\t', '').strip()
                            
                            li_name.append(stock_name)
                            li_code.append(stock_code)
                            print(f"  ✅ 解析到股票: {stock_name} ({stock_code})")
                
            except Exception as e:
                print(f"  ❌ 解析链接时出错: {e}")
                continue
        
        if li_name and li_code:
            dic = {'stock_name': li_name, 'stock_code': li_code}
            data = pd.DataFrame(dic)
            print(f"✅ 成功解析 {len(data)} 条股票数据")
            return data
        else:
            print("❌ 未解析到有效的股票数据")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ 网页解析方法失败: {e}")
        return pd.DataFrame()

def test_api_method(fund_code):
    """测试API方法"""
    try:
        print(f"\n🔌 测试API方法 - 基金: {fund_code}")
        
        # 尝试不同的API端点
        api_endpoints = [
            f"http://fund.eastmoney.com/api/FundPosition/{fund_code}",
            f"http://fund.eastmoney.com/api/FundHoldings/{fund_code}",
            f"http://fund.eastmoney.com/data/fbsfundranking.html?ft={fund_code}",
        ]
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': f'http://fund.eastmoney.com/{fund_code}.html',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        for i, api_url in enumerate(api_endpoints):
            print(f"\n--- API端点 {i+1}: {api_url} ---")
            
            try:
                source = page_source_standalone(api_url, headers)
                
                if source and len(source) > 100:
                    print(f"✅ 成功获取数据，长度: {len(source)}")
                    print(f"数据预览: {source[:200]}...")
                    
                    # 尝试解析JSON
                    try:
                        import json
                        data = json.loads(source)
                        print(f"✅ 成功解析JSON: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"JSON键: {list(data.keys())}")
                            
                            # 尝试提取股票数据
                            result = parse_api_data(data, fund_code)
                            if not result.empty:
                                print(f"✅ API方法成功获取 {len(result)} 条股票数据")
                                return result
                            
                    except json.JSONDecodeError:
                        print("❌ 不是有效的JSON格式")
                else:
                    print("❌ 未获取到数据")
                    
            except Exception as e:
                print(f"❌ 请求失败: {e}")
        
        print("❌ 所有API端点都失败了")
        return pd.DataFrame()
        
    except Exception as e:
        print(f"❌ API方法失败: {e}")
        return pd.DataFrame()

def parse_api_data(data, fund_code):
    """解析API返回的数据"""
    try:
        li_name = []
        li_code = []
        
        if isinstance(data, dict):
            possible_fields = ['data', 'result', 'list', 'stocks', 'positions', 'holdings']
            
            for field in possible_fields:
                if field in data:
                    items = data[field]
                    if isinstance(items, list):
                        for item in items:
                            if isinstance(item, dict):
                                stock_name = item.get('name') or item.get('stock_name') or item.get('title')
                                stock_code = item.get('code') or item.get('stock_code') or item.get('id')
                                
                                if stock_name and stock_code:
                                    li_name.append(str(stock_name))
                                    li_code.append(str(stock_code))
                                    print(f"  ✅ 从API解析到股票: {stock_name} ({stock_code})")
        
        if li_name and li_code:
            dic = {'stock_name': li_name, 'stock_code': li_code}
            return pd.DataFrame(dic)
        else:
            return pd.DataFrame()
            
    except Exception as e:
        print(f"❌ 解析API数据时发生错误: {e}")
        return pd.DataFrame()

def test_fund_download():
    """测试基金下载功能"""
    try:
        print("🧪 测试基金下载功能（独立版本）...")
        print("=" * 60)
        
        # 测试基金代码
        test_funds = ["003069", "002556", "001072"]
        
        for fund_code in test_funds:
            print(f"\n{'='*60}")
            print(f"测试基金: {fund_code}")
            print(f"{'='*60}")
            
            # 测试API方法
            api_data = test_api_method(fund_code)
            
            # 测试网页方法
            web_data = test_web_method(fund_code)
            
            # 总结结果
            if not api_data.empty:
                print(f"\n🎉 API方法成功！获取 {len(api_data)} 条数据")
                print("数据预览:")
                print(api_data.head())
            elif not web_data.empty:
                print(f"\n🎉 网页方法成功！获取 {len(web_data)} 条数据")
                print("数据预览:")
                print(web_data.head())
            else:
                print(f"\n❌ 两种方法都失败了")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 开始独立测试基金下载功能...")
    
    if test_fund_download():
        print("\n🎉 独立测试成功！")
    else:
        print("\n❌ 独立测试失败！")
        sys.exit(1) 