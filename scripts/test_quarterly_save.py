#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试按季度保存CSV功能
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_quarterly_save():
    """测试按季度保存功能"""
    try:
        print("🔍 测试按季度保存功能...")
        
        from App.codes.RnnDataFile.save_download import save_1m_to_csv
        from config import Config
        
        # 创建跨季度的测试数据
        test_data = pd.DataFrame({
            'date': [
                datetime(2025, 3, 15, 9, 30) + timedelta(minutes=i),  # Q1
                datetime(2025, 3, 15, 9, 30) + timedelta(minutes=i+1),  # Q1
                datetime(2025, 4, 15, 9, 30) + timedelta(minutes=i+2),  # Q2
                datetime(2025, 4, 15, 9, 30) + timedelta(minutes=i+3),  # Q2
                datetime(2025, 7, 15, 9, 30) + timedelta(minutes=i+4),  # Q3
                datetime(2025, 7, 15, 9, 30) + timedelta(minutes=i+5),  # Q3
            ] for i in range(5)
        }).explode('date').reset_index(drop=True)
        
        # 添加其他列
        test_data['open'] = 100.0 + test_data.index * 0.1
        test_data['close'] = 100.1 + test_data.index * 0.1
        test_data['high'] = 100.2 + test_data.index * 0.1
        test_data['low'] = 99.9 + test_data.index * 0.1
        test_data['volume'] = 1000 + test_data.index * 100
        test_data['money'] = 100000 + test_data.index * 10000
        
        print(f"测试数据形状: {test_data.shape}")
        print(f"测试数据日期范围: {test_data['date'].min()} 到 {test_data['date'].max()}")
        print(f"测试数据样本:\n{test_data.head()}")
        
        # 检查季度分组
        quarters = test_data.groupby(test_data['date'].dt.to_period('Q'))
        print(f"\n数据将按以下季度分组:")
        for quarter, group in quarters:
            print(f"  {quarter}: {len(group)} 条记录")
        
        # 测试保存CSV
        test_stock_code = 'BK0421'
        try:
            save_1m_to_csv(test_data, test_stock_code)
            print(f"✅ 成功保存 {test_stock_code} 数据到CSV")
            
            # 检查保存的文件
            base_dir = os.path.join(Config.get_project_root(), 'data', 'data', 'quarters', str(test_data['date'].dt.year), f"Q{test_data['date'].dt.quarter}")
            if os.path.exists(base_dir):
                print(f"✅ 目录结构已创建: {base_dir}")
                for root, dirs, files in os.walk(base_dir):
                    for file in files:
                        if file.endswith('.csv'):
                            print(f"  📁 {os.path.join(root, file)}")
            else:
                print(f"❌ 目录未创建: {base_dir}")
                
        except Exception as e:
            print(f"❌ 保存CSV失败: {e}")
            return False
        
        print("\n🎉 按季度保存测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_quarterly_save()
    sys.exit(0 if success else 1) 