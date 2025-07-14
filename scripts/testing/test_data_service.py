#!/usr/bin/env python3
"""
数据服务测试脚本

测试DataService的各项功能

作者: 系统管理员
创建时间: 2024-01-01
最后修改: 2024-01-01
版本: 1.0.0
"""

import os
import sys
import logging
import unittest
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from App import create_app
from App.exts import db
from App.services.data_service import data_service, validation_service, clean_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestDataService(unittest.TestCase):
    """数据服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 测试数据
        self.test_stock_code = '000001'
        self.test_start_date = '2024-01-01'
        self.test_end_date = '2024-01-31'
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_data_service_initialization(self):
        """测试数据服务初始化"""
        self.assertIsNotNone(data_service)
        self.assertIsNotNone(validation_service)
        self.assertIsNotNone(clean_service)
        logger.info("数据服务初始化测试通过")
    
    def test_get_data_statistics(self):
        """测试获取数据统计"""
        stats = data_service.get_data_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_records', stats)
        self.assertIn('success_records', stats)
        self.assertIn('failed_records', stats)
        logger.info("数据统计测试通过")
    
    def test_get_pending_downloads(self):
        """测试获取待下载列表"""
        pending = data_service.get_pending_downloads()
        self.assertIsInstance(pending, list)
        logger.info("待下载列表测试通过")
    
    def test_get_failed_downloads(self):
        """测试获取失败下载列表"""
        failed = data_service.get_failed_downloads()
        self.assertIsInstance(failed, list)
        logger.info("失败下载列表测试通过")
    
    def test_data_validation(self):
        """测试数据验证功能"""
        import pandas as pd
        from datetime import datetime
        
        # 创建测试数据
        test_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10, freq='1min'),
            'open': [10.0] * 10,
            'close': [10.1] * 10,
            'high': [10.2] * 10,
            'low': [9.9] * 10,
            'volume': [1000] * 10,
            'money': [10000] * 10
        })
        
        # 测试有效数据
        result = validation_service.validate_stock_data(test_data)
        self.assertIsInstance(result, dict)
        self.assertIn('valid', result)
        self.assertIn('errors', result)
        self.assertIn('warnings', result)
        
        # 测试空数据
        empty_result = validation_service.validate_stock_data(pd.DataFrame())
        self.assertFalse(empty_result['valid'])
        
        logger.info("数据验证测试通过")
    
    def test_data_cleaning(self):
        """测试数据清洗功能"""
        import pandas as pd
        
        # 创建包含问题的测试数据
        test_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=5, freq='1min'),
            'open': [10.0, 0.0, 10.1, -1.0, 10.2],  # 包含0和负数
            'close': [10.1, 10.2, 0.0, 10.3, 10.4],  # 包含0
            'high': [10.2, 10.3, 10.4, 10.5, 10.6],
            'low': [9.9, 10.0, 10.1, 10.2, 10.3],
            'volume': [1000, 2000, -100, 3000, 4000],  # 包含负数
            'money': [10000, 20000, 30000, 40000, 50000]
        })
        
        # 清洗数据
        cleaned_data = clean_service.clean_stock_data(test_data)
        
        # 验证清洗结果
        self.assertIsInstance(cleaned_data, pd.DataFrame)
        self.assertLess(len(cleaned_data), len(test_data))  # 应该删除了一些问题数据
        
        # 验证清洗后的数据质量
        if not cleaned_data.empty:
            self.assertTrue((cleaned_data['open'] > 0).all())
            self.assertTrue((cleaned_data['close'] > 0).all())
            self.assertTrue((cleaned_data['volume'] >= 0).all())
        
        logger.info("数据清洗测试通过")
    
    def test_download_status_management(self):
        """测试下载状态管理"""
        # 测试获取不存在的股票状态
        status = data_service.get_download_status('999999')
        self.assertIsNone(status)
        
        logger.info("下载状态管理测试通过")


def run_performance_test():
    """运行性能测试"""
    logger.info("开始性能测试...")
    
    try:
        # 测试批量操作性能
        import time
        
        start_time = time.time()
        stats = data_service.get_data_statistics()
        end_time = time.time()
        
        logger.info(f"获取数据统计耗时: {end_time - start_time:.4f} 秒")
        
        start_time = time.time()
        pending = data_service.get_pending_downloads()
        end_time = time.time()
        
        logger.info(f"获取待下载列表耗时: {end_time - start_time:.4f} 秒")
        
        logger.info("性能测试完成")
        
    except Exception as e:
        logger.error(f"性能测试失败: {e}")


def main():
    """主函数"""
    logger.info("开始数据服务测试")
    
    # 运行单元测试
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # 运行性能测试
    run_performance_test()
    
    logger.info("数据服务测试完成")


if __name__ == '__main__':
    main() 