# 量化交易系统项目规则

## 项目结构规范

### 1. 核心应用结构
```
Stock_RNN/
├── App/                           # 主应用代码包
│   ├── routes/                    # 路由层（控制器）
│   │   ├── data/                  # 数据模块路由
│   │   ├── strategy/              # 策略模块路由
│   │   ├── trade/                 # 交易模块路由
│   │   └── evaluation/            # 评估模块路由
│   ├── models/                    # 数据模型层（ORM）
│   │   ├── data/                  # 数据相关模型
│   │   ├── strategy/              # 策略相关模型
│   │   ├── trade/                 # 交易相关模型
│   │   └── evaluation/            # 评估相关模型
│   ├── services/                  # 业务逻辑层
│   ├── templates/                 # 前端模板
│   │   ├── data/                  # 数据展示页面
│   │   ├── strategy/              # 策略展示页面
│   │   ├── trade/                 # 交易界面
│   │   └── evaluation/            # 评估页面
│   ├── static/                    # 静态文件
│   └── utils/                     # 工具函数
├── config.py                      # 全局配置文件
├── run.py                         # Flask启动脚本
└── requirements.txt               # 项目依赖
```

### 2. Scripts文件夹规范

#### 2.1 目录结构
```
scripts/
├── data/                          # 数据处理相关脚本
│   ├── fetch_data.py              # 数据抓取脚本
│   ├── process_data.py            # 数据处理脚本
│   └── migrate_data.py            # 数据迁移脚本
├── testing/                       # 测试相关脚本
│   ├── test_models.py             # 模型测试
│   ├── test_strategies.py         # 策略测试
│   └── test_api.py                # API测试
├── development/                   # 开发调试脚本
│   ├── debug_database.py          # 数据库调试
│   ├── debug_models.py            # 模型调试
│   └── debug_strategies.py        # 策略调试
├── maintenance/                   # 维护脚本
│   ├── backup_database.py         # 数据库备份
│   ├── cleanup_data.py            # 数据清理
│   └── update_config.py           # 配置更新
├── deployment/                    # 部署脚本
│   ├── deploy_production.py       # 生产环境部署
│   └── rollback.py                # 回滚脚本
└── utils/                         # 工具脚本
    ├── generate_reports.py        # 报告生成
    └── monitor_system.py          # 系统监控
```

#### 2.2 脚本命名规范

**命名规则：**
- 使用小写字母和下划线
- 文件名应清晰表达功能
- 测试脚本以`test_`开头
- 调试脚本以`debug_`开头
- 维护脚本使用动词+名词格式

**示例：**
```
✅ 正确命名：
- fetch_stock_data.py
- test_rnn_model.py
- debug_database_connection.py
- backup_daily_data.py
- migrate_user_data.py

❌ 错误命名：
- FetchData.py (大写开头)
- test.py (过于简单)
- debug.py (过于简单)
- 数据处理.py (中文命名)
```

#### 2.3 脚本文件结构规范

每个脚本文件应包含以下部分：

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
    """
    主函数
    """
    try:
        # 创建Flask应用上下文
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

### 3. 开发规范

#### 3.1 脚本开发原则

1. **单一职责原则**：每个脚本只负责一个特定功能
2. **可重复执行**：脚本应该可以安全地重复执行
3. **错误处理**：必须包含适当的错误处理和日志记录
4. **配置外部化**：硬编码的值应该放在配置文件中
5. **文档完整**：每个脚本都要有清晰的文档说明

#### 3.2 测试脚本规范

```python
#!/usr/bin/env python3
"""
测试脚本模板

用于测试特定功能模块
"""

import unittest
from App import create_app
from App.exts import db

class TestTemplate(unittest.TestCase):
    """测试类模板"""
    
    def setUp(self):
        """测试前准备"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_example(self):
        """示例测试方法"""
        # 测试逻辑
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
```

#### 3.3 调试脚本规范

```python
#!/usr/bin/env python3
"""
调试脚本模板

用于调试特定问题
"""

import logging
from App import create_app
from App.exts import db

# 配置详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_function():
    """调试函数"""
    try:
        app = create_app()
        with app.app_context():
            # 调试逻辑
            logger.debug("调试信息")
            
    except Exception as e:
        logger.error(f"调试过程中发生错误: {e}")
        raise

if __name__ == '__main__':
    debug_function()
```

### 4. 脚本执行规范

#### 4.1 执行环境
- 所有脚本必须在项目根目录下执行
- 确保Python环境已激活
- 确保依赖包已安装

#### 4.2 执行命令示例
```bash
# 在项目根目录执行
python scripts/data/fetch_data.py
python scripts/testing/test_models.py
python scripts/development/debug_database.py
```

#### 4.3 参数传递
```python
import argparse

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='脚本描述')
    parser.add_argument('--config', type=str, help='配置文件路径')
    parser.add_argument('--dry-run', action='store_true', help='试运行模式')
    return parser.parse_args()

def main():
    args = parse_args()
    # 使用参数
    pass
```

### 5. 版本控制规范

#### 5.1 Git提交规范
```
feat(scripts): 添加数据抓取脚本
fix(scripts): 修复测试脚本中的数据库连接问题
docs(scripts): 更新脚本文档
refactor(scripts): 重构调试脚本结构
test(scripts): 添加新的测试用例
```

#### 5.2 分支管理
- `main`: 主分支，包含稳定版本
- `develop`: 开发分支
- `feature/script-name`: 新脚本功能分支
- `hotfix/script-name`: 脚本紧急修复分支

### 6. 安全规范

#### 6.1 敏感信息处理
- 不要在脚本中硬编码密码、API密钥等敏感信息
- 使用环境变量或配置文件存储敏感信息
- 确保配置文件不被提交到版本控制系统

#### 6.2 数据安全
- 生产环境脚本必须包含数据备份机制
- 危险操作必须包含确认提示
- 重要数据修改前必须创建备份

### 7. 监控和日志

#### 7.1 日志规范
- 所有脚本必须记录关键操作的日志
- 错误日志必须包含详细的错误信息和堆栈跟踪
- 日志文件按日期和脚本名称分类存储

#### 7.2 监控指标
- 脚本执行时间
- 成功/失败率
- 资源使用情况
- 错误频率

### 8. 文档维护

#### 8.1 脚本文档
每个脚本都应该包含：
- 功能描述
- 参数说明
- 使用示例
- 注意事项
- 依赖关系

#### 8.2 更新记录
- 记录脚本的修改历史
- 说明修改原因和影响
- 标注版本号和发布日期

---

## 执行检查清单

在提交新脚本前，请确认：

- [ ] 脚本命名符合规范
- [ ] 包含完整的文档说明
- [ ] 有适当的错误处理
- [ ] 包含日志记录
- [ ] 可以安全重复执行
- [ ] 已通过基本测试
- [ ] 遵循安全规范
- [ ] 更新了相关文档

---

**注意：** 本规范适用于所有scripts文件夹中的脚本。如有特殊情况需要违反规范，请提前与项目负责人沟通并获得批准。 