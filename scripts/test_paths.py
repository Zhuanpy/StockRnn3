#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试路径配置脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_paths():
    """测试路径配置"""
    try:
        print("🔍 测试路径配置...")
        
        # 测试config中的路径
        from config import Config
        
        print(f"项目根目录: {Config.get_project_root()}")
        print(f"密码文件路径: {Config.get_password_path()}")
        print(f"东方财富路径: {Config.get_eastmoney_path()}")
        print(f"雪球路径: {Config.get_xueqiu_path()}")
        print(f"代码数据路径: {Config.get_code_data_path()}")
        
        # 测试file_path中的路径
        from App.codes.RnnDataFile.file_path import password_path
        print(f"file_path中的password_path: {password_path}")
        
        # 检查关键文件是否存在
        header_file = Config.get_eastmoney_path() / 'header_stock_1m_multiple_days.txt'
        print(f"\n检查关键文件:")
        print(f"header_stock_1m_multiple_days.txt: {header_file}")
        print(f"文件是否存在: {header_file.exists()}")
        
        if header_file.exists():
            print("✅ 路径配置正确，文件存在")
        else:
            print("❌ 文件不存在，路径可能有问题")
        
        print("\n🎉 路径测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 路径测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_paths()
    sys.exit(0 if success else 1) 