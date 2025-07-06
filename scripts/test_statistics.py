#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试下载统计API功能
"""

import requests
import json

def test_download_statistics():
    """测试下载统计API"""
    try:
        # 测试获取下载统计数据
        response = requests.get('http://localhost:5000/download-statistics')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 下载统计API测试成功")
            print(f"📊 统计数据:")
            print(f"   总股票数: {data.get('total', 0)}")
            print(f"   等待下载: {data.get('pending', 0)}")
            print(f"   下载成功: {data.get('success', 0)}")
            print(f"   下载失败: {data.get('failed', 0)}")
            print(f"   正在下载: {data.get('processing', 0)}")
            
            # 验证数据一致性
            total = data.get('total', 0)
            calculated_total = (data.get('pending', 0) + 
                              data.get('success', 0) + 
                              data.get('failed', 0) + 
                              data.get('processing', 0))
            
            if total == calculated_total:
                print("✅ 数据一致性检查通过")
            else:
                print(f"⚠️  数据一致性检查失败: 总数={total}, 计算总数={calculated_total}")
                
        else:
            print(f"❌ API请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Flask应用正在运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

def test_download_status():
    """测试下载状态API"""
    try:
        response = requests.get('http://localhost:5000/download-status')
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 下载状态API测试成功")
            print(f"📈 下载状态: {data.get('status', '未知')}")
            print(f"📊 下载进度: {data.get('progress', 0)}%")
        else:
            print(f"❌ 状态API请求失败，状态码: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保Flask应用正在运行")
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    print("🧪 开始测试下载统计功能...")
    print("=" * 50)
    
    test_download_status()
    print("-" * 30)
    test_download_statistics()
    
    print("=" * 50)
    print("🎉 测试完成！") 