#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试模板路径是否正确
"""

import os
import sys

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from App import create_app

def test_template_paths():
    """测试所有模板路径是否存在"""
    app = create_app()
    
    with app.app_context():
        from flask import render_template_string
        
        # 测试的模板路径列表
        template_paths = [
            'data/success.html',
            'data/progress.html',
            'data/股票下载.html',
            'data/resample_to_daily_data.html',
            'data/download_minute_data.html',
            'data/下载基金持仓数据.html',
            'data/download_fund_data.html',
            'data/stock_market_data.html',
            'data/stock_detail.html',
            'data/data_management.html',
            'data/stock_classification.html',
            'data/record_stock_minute.html'
        ]
        
        print("测试模板路径...")
        print("=" * 50)
        
        for template_path in template_paths:
            try:
                # 尝试渲染模板（即使只是检查路径）
                template_exists = app.jinja_env.get_template(template_path)
                print(f"✓ {template_path} - 存在")
            except Exception as e:
                print(f"✗ {template_path} - 不存在: {e}")
        
        print("=" * 50)
        print("模板路径测试完成！")

if __name__ == "__main__":
    test_template_paths() 