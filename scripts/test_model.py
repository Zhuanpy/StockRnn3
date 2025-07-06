#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试Top500FundRecord模型
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from App import create_app
from App.models.strategy.StockRecordModels import Top500FundRecord
from datetime import date

def test_model():
    """测试模型功能"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=" * 50)
            print("测试 Top500FundRecord 模型")
            print("=" * 50)
            
            # 测试查询所有记录
            all_records = Top500FundRecord.query.all()
            print(f"总记录数: {len(all_records)}")
            
            if all_records:
                # 显示第一条记录
                first_record = all_records[0]
                print(f"第一条记录: {first_record}")
                print(f"基金名称: {first_record.name}")
                print(f"基金代码: {first_record.code}")
                print(f"选择状态: {first_record.selection}")
                print(f"下载状态: {first_record.status}")
                print(f"日期: {first_record.date}")
                
                # 测试转换为字典
                record_dict = first_record.to_dict()
                print(f"字典格式: {record_dict}")
                
                # 测试获取待下载基金
                today = date.today()
                success_status = f'success-{today}'
                pending_funds = Top500FundRecord.get_pending_funds(success_status)
                print(f"待下载基金数: {len(pending_funds)}")
                
                # 测试获取已选择基金
                selected_funds = Top500FundRecord.get_funds_by_selection(1)
                print(f"已选择基金数: {len(selected_funds)}")
                
            else:
                print("表中没有数据")
            
            print("=" * 50)
            print("模型测试完成！")
            print("=" * 50)
            
        except Exception as e:
            print(f"测试模型时发生错误: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_model() 