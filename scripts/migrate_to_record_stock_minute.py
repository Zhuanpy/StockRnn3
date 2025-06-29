#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整迁移脚本：从 download_1m_data 迁移到 record_stock_minute
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

def check_tables():
    """检查表是否存在"""
    try:
        print("🔍 检查表结构...")
        
        # 检查 record_stock_minute 表
        result = db.session.execute(text("""
            SELECT COUNT(*) as table_exists 
            FROM information_schema.tables 
            WHERE table_schema = 'quanttradingsystem' 
            AND table_name = 'record_stock_minute'
        """))
        
        record_table_exists = result.fetchone()[0]
        print(f"record_stock_minute 表存在: {bool(record_table_exists)}")
        
        # 检查 download_1m_data 表
        result = db.session.execute(text("""
            SELECT COUNT(*) as table_exists 
            FROM information_schema.tables 
            WHERE table_schema = 'quanttradingsystem' 
            AND table_name = 'download_1m_data'
        """))
        
        download_table_exists = result.fetchone()[0]
        print(f"download_1m_data 表存在: {bool(download_table_exists)}")
        
        return record_table_exists, download_table_exists
        
    except Exception as e:
        print(f"❌ 检查表结构时发生错误: {e}")
        return False, False

def migrate_data():
    """迁移数据"""
    try:
        print("\n📦 开始数据迁移...")
        
        # 获取所有股票信息
        stocks = StockCodes.query.all()
        stock_dict = {stock.code: stock.id for stock in stocks}
        print(f"找到 {len(stocks)} 只股票")
        
        # 检查是否还有 download_1m_data 表
        result = db.session.execute(text("""
            SELECT COUNT(*) as table_exists 
            FROM information_schema.tables 
            WHERE table_schema = 'quanttradingsystem' 
            AND table_name = 'download_1m_data'
        """))
        
        if result.fetchone()[0] == 0:
            print("✅ download_1m_data 表已不存在，跳过数据迁移")
            return True
        
        # 获取 download_1m_data 中的数据
        result = db.session.execute(text("""
            SELECT code, end_date, record_date, es_download_status
            FROM download_1m_data
        """))
        
        old_records = result.fetchall()
        print(f"找到 {len(old_records)} 条旧记录")
        
        # 迁移数据
        migrated_count = 0
        for old_record in old_records:
            stock_code = old_record[0]
            end_date = old_record[1]
            record_date = old_record[2]
            es_download_status = old_record[3]
            
            # 获取股票ID
            stock_id = stock_dict.get(stock_code)
            if not stock_id:
                print(f"⚠️ 未找到股票代码 {stock_code} 对应的ID")
                continue
            
            # 检查是否已存在记录
            existing_record = RecordStockMinute.query.filter_by(stock_code_id=stock_id).first()
            if existing_record:
                # 更新现有记录
                existing_record.end_date = end_date
                existing_record.record_date = record_date
                if es_download_status and 'success' in es_download_status:
                    existing_record.download_status = 'success'
                    existing_record.download_progress = 100.0
                else:
                    existing_record.download_status = 'pending'
                    existing_record.download_progress = 0.0
                existing_record.updated_at = datetime.now()
            else:
                # 创建新记录
                new_record = RecordStockMinute(
                    stock_code_id=stock_id,
                    download_status='success' if (es_download_status and 'success' in es_download_status) else 'pending',
                    download_progress=100.0 if (es_download_status and 'success' in es_download_status) else 0.0,
                    start_date=date(2020, 1, 1),
                    end_date=end_date,
                    record_date=record_date,
                    total_records=0,
                    downloaded_records=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.add(new_record)
            
            migrated_count += 1
        
        db.session.commit()
        print(f"✅ 成功迁移 {migrated_count} 条记录")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 数据迁移时发生错误: {e}")
        return False

def init_missing_records():
    """初始化缺失的记录"""
    try:
        print("\n🔧 初始化缺失的记录...")
        
        # 获取所有股票信息
        stocks = StockCodes.query.all()
        
        # 检查已存在的记录
        existing_records = RecordStockMinute.query.all()
        existing_stock_ids = {record.stock_code_id for record in existing_records}
        
        # 创建缺失的记录
        new_records = []
        for stock in stocks:
            if stock.id not in existing_stock_ids:
                record = RecordStockMinute(
                    stock_code_id=stock.id,
                    download_status='pending',
                    download_progress=0.0,
                    start_date=date(2020, 1, 1),
                    end_date=date(2020, 1, 1),
                    record_date=date.today(),
                    total_records=0,
                    downloaded_records=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                new_records.append(record)
        
        if new_records:
            db.session.bulk_save_objects(new_records)
            db.session.commit()
            print(f"✅ 创建了 {len(new_records)} 条新记录")
        else:
            print("✅ 所有股票都已存在记录")
        
        return True
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 初始化记录时发生错误: {e}")
        return False

def show_statistics():
    """显示统计信息"""
    try:
        print("\n📊 迁移后统计信息:")
        
        total_records = RecordStockMinute.query.count()
        pending_records = RecordStockMinute.query.filter_by(download_status='pending').count()
        success_records = RecordStockMinute.query.filter_by(download_status='success').count()
        failed_records = RecordStockMinute.query.filter_by(download_status='failed').count()
        processing_records = RecordStockMinute.query.filter_by(download_status='processing').count()
        
        print(f"  总记录数: {total_records}")
        print(f"  待下载: {pending_records}")
        print(f"  下载成功: {success_records}")
        print(f"  下载失败: {failed_records}")
        print(f"  下载中: {processing_records}")
        
        return True
        
    except Exception as e:
        print(f"❌ 获取统计信息时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始迁移到 record_stock_minute 表")
    print(f"时间: {datetime.now()}")
    print("-" * 50)
    
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        try:
            # 检查表结构
            record_exists, download_exists = check_tables()
            if not record_exists:
                print("❌ record_stock_minute 表不存在，请先创建表")
                return False
            
            # 迁移数据
            if download_exists:
                if not migrate_data():
                    return False
            else:
                print("✅ download_1m_data 表已不存在")
            
            # 初始化缺失的记录
            if not init_missing_records():
                return False
            
            # 显示统计信息
            if not show_statistics():
                return False
            
            print("\n🎉 迁移完成！")
            print("\n📝 下一步操作:")
            print("1. 测试批量下载功能")
            print("2. 确认数据正常后，可以删除 download_1m_data 表")
            print("3. 运行: DROP TABLE IF EXISTS download_1m_data;")
            
            return True
            
        except Exception as e:
            print(f"❌ 迁移过程中发生错误: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 