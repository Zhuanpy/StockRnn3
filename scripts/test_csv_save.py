#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CSV保存功能，确保不会重复写入header
"""

import sys
import os
import pandas as pd
import threading
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_csv_save():
    """测试CSV保存功能"""
    
    # 模拟基金数据
    test_data1 = pd.DataFrame({
        'stock_name': ['股票A', '股票B'],
        'stock_code': ['000001', '000002'],
        'fund_name': ['基金1', '基金1'],
        'fund_code': ['001', '001'],
        'download_date': ['2025-07-06', '2025-07-06'],
        'holdings_ratio': [5.2, 3.8],
        'market_value': ['N/A', 'N/A'],
        'shares': ['N/A', 'N/A']
    })
    
    test_data2 = pd.DataFrame({
        'stock_name': ['股票C', '股票D'],
        'stock_code': ['000003', '000004'],
        'fund_name': ['基金2', '基金2'],
        'fund_code': ['002', '002'],
        'download_date': ['2025-07-06', '2025-07-06'],
        'holdings_ratio': [4.1, 2.9],
        'market_value': ['N/A', 'N/A'],
        'shares': ['N/A', 'N/A']
    })
    
    # 创建测试目录
    test_dir = os.path.join(os.getcwd(), 'data', 'test_funds_holdings')
    os.makedirs(test_dir, exist_ok=True)
    
    # 测试文件路径
    test_file = os.path.join(test_dir, 'test_funds_holdings_20250706.csv')
    
    # 删除已存在的测试文件
    if os.path.exists(test_file):
        os.remove(test_file)
    
    def save_data(data, delay=0):
        """模拟保存数据"""
        time.sleep(delay)  # 模拟网络延迟
        
        # 使用线程锁来确保线程安全
        import tempfile
        
        # 创建线程锁（全局变量，确保所有线程共享同一个锁）
        if not hasattr(save_data, '_file_lock'):
            save_data._file_lock = threading.Lock()
        
        # 创建临时文件来写入数据
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8-sig')
        temp_path = temp_file.name
        
        try:
            # 写入数据到临时文件
            data.to_csv(temp_path, index=False, encoding='utf-8-sig')
            temp_file.close()
            
            # 使用线程锁来安全地追加到目标文件
            with save_data._file_lock:
                # 检查文件是否为空（是否需要写入header）
                file_exists = os.path.exists(test_file) and os.path.getsize(test_file) > 0
                
                if not file_exists:
                    # 文件不存在或为空，写入完整数据（包括header）
                    with open(temp_path, 'r', encoding='utf-8-sig') as temp_read:
                        with open(test_file, 'w', encoding='utf-8-sig') as target_file:
                            target_file.write(temp_read.read())
                    print(f"数据已保存到新文件: {test_file}")
                else:
                    # 文件存在且不为空，只写入数据行（不包括header）
                    with open(temp_path, 'r', encoding='utf-8-sig') as temp_read:
                        lines = temp_read.readlines()
                        # 跳过header行，只写入数据行
                        with open(test_file, 'a', encoding='utf-8-sig') as target_file:
                            for line in lines[1:]:
                                target_file.write(line)
                    print(f"数据已追加到现有文件: {test_file}")
            
            print(f"本次保存 {len(data)} 条记录")
            return True
                    
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    # 创建多个线程同时保存数据
    threads = []
    
    # 线程1：保存第一组数据
    thread1 = threading.Thread(target=save_data, args=(test_data1, 0.1))
    threads.append(thread1)
    
    # 线程2：保存第二组数据
    thread2 = threading.Thread(target=save_data, args=(test_data2, 0.2))
    threads.append(thread2)
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    # 检查结果
    print(f"\n=== 测试结果 ===")
    print(f"文件路径: {test_file}")
    print(f"文件大小: {os.path.getsize(test_file)} 字节")
    
    # 读取文件内容
    if os.path.exists(test_file):
        with open(test_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()
            lines = content.strip().split('\n')
            print(f"总行数: {len(lines)}")
            print(f"预期行数: 5 (1个header + 4个数据行)")
            
            # 检查header
            if len(lines) > 0:
                print(f"Header: {lines[0]}")
            
            # 检查是否有重复的header
            header_count = sum(1 for line in lines if line.startswith('stock_name'))
            print(f"Header出现次数: {header_count}")
            
            if header_count == 1:
                print("✅ 测试通过：只有一个header")
            else:
                print(f"❌ 测试失败：有 {header_count} 个header")
                
            # 显示文件内容
            print(f"\n=== 文件内容 ===")
            print(content)
    else:
        print("❌ 测试失败：文件未创建")

if __name__ == "__main__":
    test_csv_save() 