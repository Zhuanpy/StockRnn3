#!/usr/bin/env python3
"""
量化交易系统启动文件
"""
import os
from App import create_app

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'development')

# 创建应用实例
app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    ) 