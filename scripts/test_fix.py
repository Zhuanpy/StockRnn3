#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试外键修复脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_models():
    """测试模型导入和外键关系"""
    try:
        print("🔍 测试模型导入...")
        
        # 测试导入基本模型
        from App.models.data.basic_info import StockCodes
        print("✅ StockCodes 导入成功")
        
        # 测试导入 RecordStockMinute
        from App.models.data.Stock1m import RecordStockMinute
        print("✅ RecordStockMinute 导入成功")
        
        # 检查表名和绑定键
        print(f"\n📋 模型信息:")
        print(f"StockCodes.__tablename__: {StockCodes.__tablename__}")
        print(f"StockCodes.__bind_key__: {getattr(StockCodes, '__bind_key__', 'None')}")
        print(f"RecordStockMinute.__tablename__: {RecordStockMinute.__tablename__}")
        print(f"RecordStockMinute.__bind_key__: {getattr(RecordStockMinute, '__bind_key__', 'None')}")
        
        # 检查外键定义
        stock_code_id_column = RecordStockMinute.__table__.columns.get('stock_code_id')
        if stock_code_id_column:
            foreign_key = stock_code_id_column.foreign_keys[0]
            print(f"\n🔗 外键信息:")
            print(f"外键表: {foreign_key.column.table.name}")
            print(f"外键列: {foreign_key.column.name}")
            print(f"引用表: {foreign_key.parent.table.name}")
            print(f"引用列: {foreign_key.parent.name}")
        
        print("\n🎉 模型测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_models()
    sys.exit(0 if success else 1) 