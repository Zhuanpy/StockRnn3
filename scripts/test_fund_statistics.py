#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基金下载统计逻辑
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import date
from App import create_app
from App.models.strategy.StockRecordModels import Top500FundRecord

def should_download_fund(fund_record, days_interval=15):
    """判断基金是否需要重新下载"""
    if not fund_record.date:
        return True
    
    days_since_last = (date.today() - fund_record.date).days
    return days_since_last >= days_interval

def get_download_statistics():
    """获取下载统计数据"""
    try:
        # 获取所有基金记录
        all_funds = Top500FundRecord.query.all()
        
        waiting_count = 0
        success_count = 0
        failure_count = 0
        
        print(f"总基金数量: {len(all_funds)}")
        
        for fund in all_funds:
            print(f"基金: {fund.name} ({fund.code})")
            print(f"  状态: {fund.status}")
            print(f"  日期: {fund.date}")
            
            if should_download_fund(fund):
                waiting_count += 1
                print(f"  -> 等待下载")
            elif fund.status and fund.status.startswith('success-'):
                success_count += 1
                print(f"  -> 下载成功")
            elif fund.status and fund.status.startswith('failure-'):
                failure_count += 1
                print(f"  -> 下载失败")
            else:
                print(f"  -> 状态未知")
        
        print(f"\n统计结果:")
        print(f"等待下载: {waiting_count}")
        print(f"下载成功: {success_count}")
        print(f"下载失败: {failure_count}")
        
        return {
            'waiting': waiting_count,
            'success': success_count,
            'failure': failure_count,
            'total': len(all_funds)
        }
    except Exception as e:
        print(f"获取下载统计数据时发生错误: {e}")
        return {'waiting': 0, 'success': 0, 'failure': 0, 'total': 0}

def main():
    app = create_app()
    
    with app.app_context():
        print("=== 基金下载统计测试 ===\n")
        
        # 获取统计数据
        stats = get_download_statistics()
        
        print(f"\n=== 最终统计结果 ===")
        print(f"等待下载: {stats['waiting']}")
        print(f"下载成功: {stats['success']}")
        print(f"下载失败: {stats['failure']}")
        print(f"总计: {stats['total']}")

if __name__ == "__main__":
    main() 