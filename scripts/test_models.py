#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试模型初始化脚本
验证所有模型是否能正确加载
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from App import create_app
from App.exts import db

def test_models():
    """测试模型初始化"""
    try:
        print("🔍 测试模型初始化...")
        
        # 创建应用上下文
        app = create_app()
        with app.app_context():
            # 导入所有模型
            from App.models.data.basic_info import StockCodes, StockClassification
            from App.models.data.Stock1m import RecordStockMinute
            
            print("✅ 模型导入成功")
            
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"数据库中的表: {tables}")
            
            # 检查特定表
            required_tables = ['stock_market_data', 'record_stock_minute']
            for table in required_tables:
                if table in tables:
                    print(f"✅ 表 {table} 存在")
                else:
                    print(f"❌ 表 {table} 不存在")
            
            # 尝试创建表结构（不实际创建）
            print("\n🔍 检查表结构...")
            for table in required_tables:
                if table in tables:
                    columns = inspector.get_columns(table)
                    print(f"\n{table} 表的列:")
                    for col in columns:
                        print(f"  {col['name']}: {col['type']} - {col['nullable']}")
            
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