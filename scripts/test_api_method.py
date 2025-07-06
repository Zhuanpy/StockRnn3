#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试API方法获取基金数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_method():
    """测试API方法"""
    try:
        print("🧪 测试API方法获取基金数据...")
        print("=" * 50)
        
        from App.codes.downloads.DlEastMoney import DownloadData
        
        # 测试基金代码
        test_funds = ["003069", "002556", "001072"]
        
        for fund_code in test_funds:
            print(f"\n📥 测试基金: {fund_code}")
            
            try:
                # 测试API方法
                print(f"  尝试API方法...")
                api_data = DownloadData.funds_awkward_api(fund_code)
                
                if not api_data.empty:
                    print(f"  ✅ API方法成功，获取 {len(api_data)} 条数据")
                    print(f"  数据预览:")
                    print(api_data.head())
                else:
                    print(f"  ❌ API方法失败")
                
                # 测试网页方法
                print(f"  尝试网页方法...")
                web_data = DownloadData.funds_awkward_web(fund_code)
                
                if not web_data.empty:
                    print(f"  ✅ 网页方法成功，获取 {len(web_data)} 条数据")
                    print(f"  数据预览:")
                    print(web_data.head())
                else:
                    print(f"  ❌ 网页方法失败")
                
                # 测试综合方法
                print(f"  尝试综合方法...")
                combined_data = DownloadData.funds_awkward(fund_code)
                
                if not combined_data.empty:
                    print(f"  ✅ 综合方法成功，获取 {len(combined_data)} 条数据")
                    print(f"  数据预览:")
                    print(combined_data.head())
                else:
                    print(f"  ❌ 综合方法失败")
                
            except Exception as e:
                print(f"  ❌ 测试基金 {fund_code} 时出错: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_single_api():
    """测试单个API端点"""
    try:
        print("\n🔍 测试单个API端点...")
        
        from App.codes.downloads.download_utils import page_source
        
        fund_code = "003069"
        
        # 测试不同的API端点
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
                source = page_source(url=api_url, headers=headers)
                
                if source:
                    print(f"✅ 成功获取数据，长度: {len(source)}")
                    print(f"数据预览: {source[:200]}...")
                    
                    # 尝试解析JSON
                    try:
                        import json
                        data = json.loads(source)
                        print(f"✅ 成功解析JSON: {type(data)}")
                        
                        if isinstance(data, dict):
                            print(f"JSON键: {list(data.keys())}")
                    except json.JSONDecodeError:
                        print("❌ 不是有效的JSON格式")
                else:
                    print("❌ 未获取到数据")
                    
            except Exception as e:
                print(f"❌ 请求失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试API方法...")
    
    # 测试单个API端点
    if test_single_api():
        print("\n✅ 单个API测试成功")
    else:
        print("\n❌ 单个API测试失败")
    
    # 测试综合方法
    if test_api_method():
        print("\n🎉 API方法测试成功！")
    else:
        print("\n❌ API方法测试失败！")
        sys.exit(1) 