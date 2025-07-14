"""
临时补丁文件：解决typing_extensions兼容性问题
在导入Flask-SQLAlchemy之前运行此文件
"""

import sys
from typing import TYPE_CHECKING

# 检查typing_extensions版本
try:
    import typing_extensions
    if not hasattr(typing_extensions, 'TypeAliasType'):
        # 如果缺少TypeAliasType，创建一个空的占位符
        class TypeAliasType:
            def __init__(self, *args, **kwargs):
                pass
        
        # 将TypeAliasType添加到typing_extensions模块
        typing_extensions.TypeAliasType = TypeAliasType
        print("已创建TypeAliasType占位符")
    else:
        print("typing_extensions版本正常")
except ImportError:
    print("typing_extensions未安装")
    sys.exit(1)

# 现在可以安全导入SQLAlchemy相关模块
try:
    import sqlalchemy
    print(f"SQLAlchemy版本: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"SQLAlchemy导入失败: {e}")
    sys.exit(1) 