# 量化交易系统项目规则

## 项目架构规范

### 1. 目录结构规范
```
Stock_RNN/
├── app/                          # 主应用代码包
│   ├── __init__.py              # 创建Flask实例，注册蓝图、扩展
│   ├── routes/                  # 路由层（控制器）使用Blueprint分模块
│   ├── models/                  # 数据模型（ORM层）
│   ├── services/                # 业务逻辑层（策略、数据处理、交易等）
│   ├── templates/               # 前端模板（Jinja2）
│   ├── static/                  # 静态文件目录
│   └── tasks.py                 # APScheduler任务定义
├── config.py                    # 全局配置文件
├── run.py                       # Flask启动脚本
├── database/                    # 数据库初始化脚本
├── scripts/                     # 可独立执行的命令行脚本
├── scheduler/                   # 定时任务调度器配置
├── logs/                        # 日志文件目录
└── requirements.txt             # Python依赖库
```

### 2. 模块化规范
- **data模块**: 数据采集、更新、存储
- **strategy模块**: 策略运行、回测、信号生成
- **trade模块**: 交易执行、订单管理
- **evaluation模块**: 绩效分析、风险评估

### 3. 代码组织规范
- 每个功能模块都有对应的routes、models、services、templates
- 业务逻辑必须在services层实现
- routes层只负责请求处理和响应
- models层只负责数据定义和基础操作

### 4. 命名规范
- 文件名使用小写字母和下划线
- 类名使用驼峰命名法
- 函数名使用小写字母和下划线
- 常量使用大写字母和下划线

### 5. 导入规范
- 使用绝对导入路径
- 避免循环导入
- 按标准库、第三方库、本地模块的顺序导入

### 6. 错误处理规范
- 所有外部调用必须有异常处理
- 使用统一的错误响应格式
- 记录详细的错误日志

### 7. 日志规范
- 使用统一的日志格式
- 按级别记录日志（DEBUG、INFO、WARNING、ERROR）
- 敏感信息不得记录到日志中

### 8. 配置管理规范
- 使用环境变量管理敏感配置
- 不同环境使用不同的配置文件
- 配置变更需要记录文档

### 9. 数据库规范
- 使用SQLAlchemy ORM
- 表名使用小写字母和下划线
- 字段名使用小写字母和下划线
- 必须定义主键和外键关系

### 10. API设计规范
- 使用RESTful API设计
- 统一的响应格式
- 适当的HTTP状态码
- 完整的API文档

## 禁止事项
1. 不得随意修改项目根目录结构
2. 不得在routes层直接操作数据库
3. 不得在models层包含业务逻辑
4. 不得硬编码配置信息
5. 不得忽略异常处理
6. 不得使用全局变量存储状态
7. 不得在代码中暴露敏感信息
8. 不得使用过时的API或方法

## 开发流程
1. 新功能开发前先更新此规则文档
2. 代码提交前进行代码审查
3. 重要变更需要更新相关文档
4. 定期进行代码重构和优化 