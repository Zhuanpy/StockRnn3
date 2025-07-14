# Scripts 文件夹说明

本文件夹包含量化交易系统的所有脚本文件，包括测试、调试、数据处理、维护等功能。

## 目录结构

```
scripts/
├── README.md                       # 本文件
├── data/                           # 数据处理脚本
├── testing/                        # 测试脚本
├── development/                    # 开发调试脚本
├── maintenance/                    # 维护脚本
├── deployment/                     # 部署脚本
└── utils/                          # 工具脚本
```

## 使用说明

### 1. 执行环境
所有脚本必须在项目根目录下执行：
```bash
# 正确执行方式
python scripts/data/fetch_data.py

# 错误执行方式
cd scripts/data
python fetch_data.py  # 这样会找不到项目模块
```

### 2. 脚本分类

#### data/ - 数据处理脚本
- 数据抓取、清洗、转换
- 数据库迁移
- 数据备份和恢复

#### testing/ - 测试脚本
- 单元测试
- 集成测试
- 性能测试

#### development/ - 开发调试脚本
- 数据库调试
- 模型调试
- 策略调试

#### maintenance/ - 维护脚本
- 系统维护
- 数据清理
- 配置更新

#### deployment/ - 部署脚本
- 生产环境部署
- 回滚操作
- 环境配置

#### utils/ - 工具脚本
- 报告生成
- 系统监控
- 辅助工具

## 脚本模板

每个新脚本都应该基于以下模板创建：

### 标准脚本模板
```python
#!/usr/bin/env python3
"""
脚本功能描述

作者: [姓名]
创建时间: [YYYY-MM-DD]
最后修改: [YYYY-MM-DD]
版本: [版本号]
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入项目模块
from App import create_app
from App.exts import db
from config import Config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        app = create_app()
        with app.app_context():
            # 脚本主要逻辑
            pass
    except Exception as e:
        logger.error(f"脚本执行失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
```

### 测试脚本模板
```python
#!/usr/bin/env python3
"""
测试脚本模板
"""

import unittest
from App import create_app
from App.exts import db

class TestTemplate(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_example(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
```

## 注意事项

1. **路径问题**：所有脚本都必须正确处理项目路径
2. **依赖管理**：确保所有依赖都在requirements.txt中
3. **错误处理**：必须包含适当的错误处理和日志记录
4. **文档完整**：每个脚本都要有清晰的文档说明
5. **安全考虑**：不要硬编码敏感信息

## 贡献指南

1. 创建新脚本时，请遵循命名规范
2. 添加适当的文档和注释
3. 包含错误处理和日志记录
4. 测试脚本功能
5. 更新本README文件

## 常见问题

### Q: 脚本执行时找不到模块？
A: 确保在项目根目录执行脚本，并且脚本中正确添加了项目路径。

### Q: 如何调试脚本？
A: 使用development/目录下的调试脚本，或添加详细的日志输出。

### Q: 脚本执行失败怎么办？
A: 检查日志输出，确认环境配置正确，数据库连接正常。 