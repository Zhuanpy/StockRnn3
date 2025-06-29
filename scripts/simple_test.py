#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_import():
    """测试基本导入"""
    try:
        print("🔍 测试基本导入...")
        
        # 测试导入基本模型
        from App.models.data.basic_info import StockCodes
        print("✅ StockCodes 导入成功")
        
        # 测试导入 RecordStockMinute
        from App.models.data.Stock1m import RecordStockMinute
        print("✅ RecordStockMinute 导入成功")
        
        print("🎉 基本导入测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_import()
    sys.exit(0 if success else 1) 