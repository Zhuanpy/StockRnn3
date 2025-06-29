#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CSV保存功能
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_csv_save():
    """测试CSV保存功能"""
    try:
        print("🔍 测试CSV保存功能...")
        
        from App.codes.RnnDataFile.save_download import save_1m_to_csv
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'date': [
                datetime.now() - timedelta(minutes=i) 
                for i in range(10, 0, -1)
            ],
            'open': [100.0 + i * 0.1 for i in range(10)],
            'close': [100.1 + i * 0.1 for i in range(10)],
            'high': [100.2 + i * 0.1 for i in range(10)],
            'low': [99.9 + i * 0.1 for i in range(10)],
            'volume': [1000 + i * 100 for i in range(10)],
            'money': [100000 + i * 10000 for i in range(10)]
        })
        
        print(f"测试数据形状: {test_data.shape}")
        print(f"测试数据样本:\n{test_data.head()}")
        
        # 测试保存CSV
        test_stock_code = 'BK0421'
        try:
            save_1m_to_csv(test_data, test_stock_code)
            print(f"✅ 成功保存 {test_stock_code} 数据到CSV")
        except Exception as e:
            print(f"❌ 保存CSV失败: {e}")
            return False
        
        print("\n🎉 CSV保存测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_csv_save()
    sys.exit(0 if success else 1) 