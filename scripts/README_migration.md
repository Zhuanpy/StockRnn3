# 数据库迁移说明：从 download_1m_data 到 record_stock_minute

## 概述

本次迁移将废弃 `download_1m_data` 表，改用 `record_stock_minute` 表来管理股票1分钟数据的下载记录。

## 迁移原因

1. **避免重复**：两个表功能相似，合并可以避免数据冗余
2. **统一管理**：使用一个表管理所有下载记录
3. **更好的设计**：`record_stock_minute` 的设计更现代化，支持更详细的进度跟踪

## 迁移步骤

### 1. 运行迁移脚本

```bash
cd /path/to/your/project
python scripts/migrate_to_record_stock_minute.py
```

这个脚本会：
- 检查表结构
- 迁移现有数据
- 初始化缺失的记录
- 显示统计信息

### 2. 测试批量下载功能

访问批量下载页面，测试功能是否正常：
- 开始下载
- 查看进度
- 停止下载

### 3. 删除旧表（可选）

确认功能正常后，可以删除旧的 `download_1m_data` 表：

```sql
USE quanttradingsystem;
DROP TABLE IF EXISTS download_1m_data;
```

或者运行提供的SQL脚本：
```bash
mysql -u username -p < scripts/drop_download_1m_data_table.sql
```

## 表结构对比

### 旧表：download_1m_data
```sql
- id (主键)
- name (股票名称)
- market_code (市场代码)
- code (股票代码)
- es_code (东方财富代码)
- es_download_status (下载状态)
- classification (分类)
- start_date, end_date, record_date
- download_status, error_message, created_at, updated_at
```

### 新表：record_stock_minute
```sql
- id (主键)
- stock_code_id (外键，关联stock_market_data)
- download_status (下载状态)
- download_progress (下载进度)
- error_message (错误信息)
- start_date, end_date, record_date
- total_records, downloaded_records
- last_download_time
- created_at, updated_at
```

## 主要改进

1. **外键关联**：通过 `stock_code_id` 关联到 `stock_market_data` 表，避免数据重复
2. **进度跟踪**：新增 `download_progress` 字段，支持实时进度显示
3. **详细统计**：新增 `total_records` 和 `downloaded_records` 字段
4. **时间戳**：新增 `last_download_time` 字段，记录最后下载时间

## 代码变更

### 修改的文件：
1. `App/routes/data/download_data_route.py` - 更新下载逻辑
2. `App/models/data/__init__.py` - 移除旧模型导入
3. `App/models/__init__.py` - 移除旧模型导入
4. `App/models/data/Download.py` - 已删除

### 新增的文件：
1. `scripts/migrate_to_record_stock_minute.py` - 迁移脚本
2. `scripts/init_record_stock_minute_data.py` - 初始化脚本
3. `scripts/drop_download_1m_data_table.sql` - 删除旧表脚本

## 注意事项

1. **备份数据**：迁移前请备份数据库
2. **测试功能**：迁移后请测试批量下载功能
3. **数据完整性**：确保所有股票都有对应的下载记录
4. **错误处理**：新代码包含更完善的错误处理机制

## 回滚方案

如果需要回滚，可以：
1. 恢复 `download_1m_data` 表的数据
2. 恢复 `App/models/data/Download.py` 文件
3. 修改路由代码使用旧模型

## 联系支持

如果遇到问题，请检查：
1. 数据库连接是否正常
2. 表结构是否正确
3. 数据迁移是否成功
4. 应用日志中的错误信息 