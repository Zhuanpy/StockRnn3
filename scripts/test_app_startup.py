#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试应用启动，验证导入错误是否修复
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_app_import():
    """测试应用导入"""
    print("🧪 测试应用导入...")
    print("=" * 50)
    
    try:
        # 测试导入App模块
        print("📦 测试导入App模块...")
        from App import create_app
        print("✅ App模块导入成功！")
        
        # 测试创建应用实例
        print("🚀 测试创建应用实例...")
        app = create_app()
        print("✅ 应用实例创建成功！")
        
        # 测试蓝图注册
        print("📋 检查蓝图注册...")
        blueprints = list(app.blueprints.keys())
        print(f"✅ 已注册的蓝图: {blueprints}")
        
        # 检查基金下载相关蓝图
        fund_blueprints = [bp for bp in blueprints if 'fund' in bp.lower()]
        if fund_blueprints:
            print(f"✅ 基金下载蓝图: {fund_blueprints}")
        else:
            print("⚠️  未找到基金下载相关蓝图")
        
        print("=" * 50)
        print("🎉 应用启动测试成功！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请检查模块导入路径和依赖")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def test_funds_awkward_import():
    """测试基金模块导入"""
    print("\n🧪 测试基金模块导入...")
    print("=" * 50)
    
    try:
        # 测试导入基金下载蓝图
        print("📦 测试导入基金下载蓝图...")
        from App.routes.data.download_top500_funds_awkward import dl_funds_awkward_bp
        print("✅ 基金下载蓝图导入成功！")
        
        # 测试导入基金数据模型
        print("📦 测试导入基金数据模型...")
        from App.models.data.FundsAwkward import (
            save_funds_holdings_to_csv,
            get_funds_holdings_from_csv,
            get_funds_data_directory
        )
        print("✅ 基金数据模型导入成功！")
        
        # 测试获取数据目录
        print("📁 测试获取数据目录...")
        data_dir = get_funds_data_directory()
        print(f"✅ 数据目录: {data_dir}")
        
        print("=" * 50)
        print("🎉 基金模块导入测试成功！")
        return True
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试应用启动...")
    
    # 运行测试
    app_success = test_app_import()
    funds_success = test_funds_awkward_import()
    
    print("\n📋 测试总结:")
    if app_success and funds_success:
        print("✅ 所有测试通过！应用可以正常启动")
        print("💡 现在可以运行: python run.py")
    else:
        print("❌ 部分测试失败，请检查错误信息")
        if not app_success:
            print("   - 应用启动测试失败")
        if not funds_success:
            print("   - 基金模块导入测试失败") 