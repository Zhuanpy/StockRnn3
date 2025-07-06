#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基金下载功能修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_funds_download():
    """测试基金下载功能"""
    try:
        print("🧪 测试基金下载功能...")
        print("=" * 50)
        
        # 测试配置
        print("📋 测试配置...")
        from config import Config
        
        url = Config.get_eastmoney_urls('funds_awkward')
        headers = Config.get_eastmoney_headers('funds_awkward')
        
        print(f"URL配置: {url}")
        print(f"Headers配置: {headers}")
        
        if not url:
            print("❌ URL配置为空")
            return False
        
        if not headers:
            print("❌ Headers配置为空")
            return False
        
        print("✅ 配置测试通过")
        
        # 测试下载功能
        print("\n📥 测试下载功能...")
        from App.codes.downloads.DlEastMoney import DownloadData
        
        # 测试基金代码
        test_fund_code = "003069"  # 光大创业板量
        
        print(f"正在下载基金: {test_fund_code}")
        
        try:
            data = DownloadData.funds_awkward(test_fund_code)
            
            if data.empty:
                print("⚠️ 下载的数据为空")
                return False
            
            print(f"✅ 成功下载 {len(data)} 条股票数据")
            print("数据预览:")
            print(data.head())
            
            # 检查数据格式
            if 'stock_name' in data.columns and 'stock_code' in data.columns:
                print("✅ 数据格式正确")
            else:
                print("❌ 数据格式不正确")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_page_source():
    """测试页面源码获取功能"""
    try:
        print("\n🌐 测试页面源码获取...")
        
        from App.codes.downloads.DlEastMoney import DownloadData
        from App.codes.downloads.download_utils import page_source
        from config import Config
        
        url = Config.get_eastmoney_urls('funds_awkward').format("003069")
        headers = Config.get_eastmoney_headers('funds_awkward')
        
        print(f"测试URL: {url}")
        
        source = page_source(url=url, headers=headers)
        
        if source:
            print(f"✅ 成功获取页面源码，长度: {len(source)}")
            print("源码预览:")
            print(source[:500] + "..." if len(source) > 500 else source)
            return True
        else:
            print("❌ 页面源码为空")
            return False
            
    except Exception as e:
        print(f"❌ 页面源码获取失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试基金下载功能修复...")
    print("=" * 50)
    
    # 测试页面源码获取
    if test_page_source():
        print("\n✅ 页面源码获取测试通过")
    else:
        print("\n❌ 页面源码获取测试失败")
        sys.exit(1)
    
    # 测试完整下载功能
    if test_funds_download():
        print("\n🎉 基金下载功能测试成功！")
        print("\n📋 修复总结:")
        print("1. ✅ 添加了funds_awkward的URL配置")
        print("2. ✅ 添加了funds_awkward的Headers配置")
        print("3. ✅ 增强了错误处理和日志记录")
        print("4. ✅ 添加了数据验证和备用解析方法")
    else:
        print("\n❌ 基金下载功能测试失败！")
        sys.exit(1) 