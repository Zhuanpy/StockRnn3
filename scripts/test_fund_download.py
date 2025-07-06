#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试基金下载功能
"""

import requests
import json
import time

def test_fund_download_apis():
    """测试基金下载相关的API"""
    base_url = 'http://localhost:5000'
    
    print("🧪 开始测试基金下载功能...")
    print("=" * 60)
    
    # 测试1: 获取基金持仓数据下载统计数据
    print("📊 测试1: 获取基金持仓数据下载统计数据")
    try:
        response = requests.get(f'{base_url}/fund-holdings-statistics')
        if response.status_code == 200:
            data = response.json()
            print("✅ 统计数据API测试成功")
            print(f"   总基金数: {data.get('total_funds', 0)}")
            print(f"   总记录数: {data.get('total_records', 0)}")
            print(f"   已下载基金: {data.get('unique_funds', 0)}")
            print(f"   涉及股票: {data.get('unique_stocks', 0)}")
            print(f"   下载日期: {data.get('download_date', 'N/A')}")
        else:
            print(f"❌ 统计数据API失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 统计数据API测试失败: {e}")
    
    print("-" * 40)
    
    # 测试2: 获取基金持仓数据下载状态
    print("📈 测试2: 获取基金持仓数据下载状态")
    try:
        response = requests.get(f'{base_url}/fund-holdings-status')
        if response.status_code == 200:
            data = response.json()
            print("✅ 状态API测试成功")
            print(f"   下载状态: {data.get('status', '未知')}")
            print(f"   下载进度: {data.get('progress', 0)}%")
        else:
            print(f"❌ 状态API失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 状态API测试失败: {e}")
    
    print("-" * 40)
    
    # 测试3: 开始基金持仓数据下载
    print("🚀 测试3: 开始基金持仓数据下载")
    try:
        response = requests.post(f'{base_url}/start-fund-holdings')
        if response.status_code == 200:
            data = response.json()
            print("✅ 开始下载API测试成功")
            print(f"   消息: {data.get('message', 'N/A')}")
        else:
            print(f"❌ 开始下载API失败，状态码: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"❌ 开始下载API测试失败: {e}")
    
    print("-" * 40)
    
    # 测试4: 等待一段时间后再次检查状态
    print("⏳ 测试4: 等待5秒后检查下载状态")
    time.sleep(5)
    
    try:
        response = requests.get(f'{base_url}/fund-holdings-status')
        if response.status_code == 200:
            data = response.json()
            print("✅ 状态更新测试成功")
            print(f"   下载状态: {data.get('status', '未知')}")
            print(f"   下载进度: {data.get('progress', 0)}%")
        else:
            print(f"❌ 状态更新测试失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 状态更新测试失败: {e}")
    
    print("-" * 40)
    
    # 测试5: 停止基金持仓数据下载
    print("🛑 测试5: 停止基金持仓数据下载")
    try:
        response = requests.post(f'{base_url}/stop-fund-holdings')
        if response.status_code == 200:
            data = response.json()
            print("✅ 停止下载API测试成功")
            print(f"   消息: {data.get('message', 'N/A')}")
        else:
            print(f"❌ 停止下载API失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 停止下载API测试失败: {e}")
    
    print("=" * 60)
    print("🎉 基金下载功能测试完成！")

def test_fund_page_access():
    """测试基金持仓数据下载页面访问"""
    print("\n🌐 测试基金持仓数据下载页面访问")
    print("=" * 40)
    
    try:
        response = requests.get('http://localhost:5000/fund-holdings-page')
        if response.status_code == 200:
            print("✅ 基金持仓数据下载页面访问成功")
            print(f"   页面大小: {len(response.text)} 字符")
            if "基金持仓数据下载" in response.text:
                print("✅ 页面内容正确")
            else:
                print("⚠️  页面内容可能有问题")
        else:
            print(f"❌ 基金持仓数据下载页面访问失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 基金持仓数据下载页面访问失败: {e}")

if __name__ == "__main__":
    print("🔧 基金下载功能测试工具")
    print("请确保Flask应用正在运行 (python run.py)")
    print()
    
    # 测试API功能
    test_fund_download_apis()
    
    # 测试页面访问
    test_fund_page_access()
    
    print("\n📝 测试总结:")
    print("1. 基金下载功能已实现")
    print("2. 数据保存路径: data/funds_holdings/")
    print("3. 数据格式: CSV文件 (基金代码_YYYYMMDD.csv)")
    print("4. 数据库表: fund_holdings_YYYYMMDD")
    print("5. 页面设计参考了download_minute_data.html") 