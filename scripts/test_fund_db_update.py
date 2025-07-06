#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试基金数据库更新功能
"""

import sys
import os
from datetime import date

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fund_db_update():
    """测试基金数据库更新功能"""
    print("🧪 测试基金数据库更新功能...")
    print("=" * 60)
    
    try:
        from App.models.strategy.StockRecordModels import Top500FundRecord
        from App.exts import db
        from flask import Flask
        from config import config
        
        # 创建Flask应用上下文
        app = Flask(__name__)
        app.config.from_object(config['default'])
        
        with app.app_context():
            # 初始化数据库
            db.init_app(app)
            
            # 获取所有基金记录
            all_funds = Top500FundRecord.query.all()
            print(f"数据库中共有 {len(all_funds)} 条基金记录")
            
            if all_funds:
                # 显示前5条记录的状态
                print("\n前5条基金记录状态:")
                for i, fund in enumerate(all_funds[:5]):
                    print(f"  {i+1}. {fund.name} ({fund.code}) - 状态: {fund.status}, 日期: {fund.date}")
                
                # 测试更新第一条记录的状态
                test_fund = all_funds[0]
                print(f"\n测试更新基金: {test_fund.name} ({test_fund.code})")
                print(f"更新前状态: {test_fund.status}")
                print(f"更新前日期: {test_fund.date}")
                
                # 更新状态
                test_date = date.today()
                test_status = f"test-success-{test_date}"
                
                success = test_fund.update_download_status(test_status, test_date)
                print(f"更新结果: {'成功' if success else '失败'}")
                
                # 重新查询验证更新
                updated_fund = Top500FundRecord.query.get(test_fund.id)
                print(f"更新后状态: {updated_fund.status}")
                print(f"更新后日期: {updated_fund.date}")
                
                # 测试统计函数
                print("\n测试统计函数...")
                from App.routes.data.download_top500_funds_awkward import get_download_statistics
                stats = get_download_statistics()
                print(f"统计数据: {stats}")
                
            else:
                print("数据库中没有基金记录")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 60)

if __name__ == "__main__":
    test_fund_db_update() 