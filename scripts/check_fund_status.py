#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查基金数据库状态
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    try:
        from App import create_app
        from App.models.strategy.StockRecordModels import Top500FundRecord
        
        app = create_app()
        
        with app.app_context():
            # 获取所有基金记录
            all_funds = Top500FundRecord.query.all()
            
            print(f"总基金数量: {len(all_funds)}")
            print("\n基金状态详情:")
            print("-" * 80)
            
            success_count = 0
            failure_count = 0
            waiting_count = 0
            unknown_count = 0
            
            for fund in all_funds:
                print(f"基金: {fund.name} ({fund.code})")
                print(f"  状态: {fund.status}")
                print(f"  日期: {fund.date}")
                
                if fund.status and fund.status.startswith('success-'):
                    success_count += 1
                    print(f"  -> 下载成功")
                elif fund.status and fund.status.startswith('failure-'):
                    failure_count += 1
                    print(f"  -> 下载失败")
                elif fund.status is None or fund.status == '':
                    waiting_count += 1
                    print(f"  -> 等待下载")
                else:
                    unknown_count += 1
                    print(f"  -> 状态未知: {fund.status}")
                print()
            
            print("=" * 80)
            print(f"统计结果:")
            print(f"下载成功: {success_count}")
            print(f"下载失败: {failure_count}")
            print(f"等待下载: {waiting_count}")
            print(f"状态未知: {unknown_count}")
            print(f"总计: {len(all_funds)}")
            
    except Exception as e:
        print(f"检查基金状态时发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 