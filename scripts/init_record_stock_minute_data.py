#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化 record_stock_minute 表数据
从 stock_market_data 表创建下载记录
"""

import sys
import os
from datetime import date, datetime
from sqlalchemy import text

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from App.exts import db
from App import create_app
from App.models.data.Stock1m import RecordStockMinute
from App.models.data.basic_info import StockCodes

def init_record_stock_minute_data():
    """初始化 record_stock_minute 表数据"""
    try:
        print("🔧 开始初始化 record_stock_minute 表数据...")
        
        # 获取所有股票信息
        stocks = StockCodes.query.all()
        print(f"找到 {len(stocks)} 只股票")
        
        # 检查已存在的记录
        existing_records = RecordStockMinute.query.all()
        existing_stock_ids = {record.stock_code_id for record in existing_records}
        print(f"已存在 {len(existing_records)} 条记录")
        
        # 创建新记录
        new_records = []
        for stock in stocks:
            if stock.id not in existing_stock_ids:
                # 创建新的下载记录
                record = RecordStockMinute(
                    stock_code_id=stock.id,
                    download_status='pending',
                    download_progress=0.0,
                    start_date=date(2020, 1, 1),  # 默认开始日期
                    end_date=date(2020, 1, 1),    # 默认结束日期
                    record_date=date.today(),
                    total_records=0,
                    downloaded_records=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                new_records.append(record)
        
        if new_records:
            # 批量插入新记录
            db.session.bulk_save_objects(new_records)
            db.session.commit()
            print(f"✅ 成功创建 {len(new_records)} 条新记录")
        else:
            print("✅ 所有股票都已存在下载记录")
        
        # 显示统计信息
        total_records = RecordStockMinute.query.count()
        pending_records = RecordStockMinute.query.filter_by(download_status='pending').count()
        success_records = RecordStockMinute.query.filter_by(download_status='success').count()
        failed_records = RecordStockMinute.query.filter_by(download_status='failed').count()
        
        print(f"\n📊 统计信息:")
        print(f"  总记录数: {total_records}")
        print(f"  待下载: {pending_records}")
        print(f"  下载成功: {success_records}")
        print(f"  下载失败: {failed_records}")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 初始化数据时发生错误: {e}")
        return False

def update_existing_records():
    """更新现有记录的状态"""
    try:
        print("\n🔄 更新现有记录状态...")
        
        # 将状态为空的记录设置为pending
        empty_status_records = RecordStockMinute.query.filter(
            (RecordStockMinute.download_status.is_(None)) | 
            (RecordStockMinute.download_status == '')
        ).all()
        
        if empty_status_records:
            for record in empty_status_records:
                record.download_status = 'pending'
                record.download_progress = 0.0
                record.updated_at = datetime.now()
            
            db.session.commit()
            print(f"✅ 更新了 {len(empty_status_records)} 条记录的状态")
        else:
            print("✅ 没有需要更新的记录")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 更新记录时发生错误: {e}")
        return False

def main():
    """主函数"""
    print(f"时间: {datetime.now()}")
    print("-" * 50)
    
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        try:
            # 初始化数据
            if not init_record_stock_minute_data():
                return False
            
            # 更新现有记录
            if not update_existing_records():
                return False
            
            print("\n🎉 record_stock_minute 表数据初始化完成！")
            return True
            
        except Exception as e:
            print(f"❌ 初始化过程中发生错误: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 