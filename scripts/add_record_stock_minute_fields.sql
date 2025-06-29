-- 为 record_stock_minute 表添加缺少的字段
-- 根据 RecordStockMinute 模型定义生成
-- 执行前请备份数据库

USE quanttradingsystem;

-- 添加 stock_code_id 字段（外键）
ALTER TABLE record_stock_minute 
ADD COLUMN stock_code_id INT COMMENT '股票代码ID（外键）' AFTER name;

-- 添加下载状态和进度字段
ALTER TABLE record_stock_minute 
ADD COLUMN download_status VARCHAR(20) DEFAULT 'pending' COMMENT '下载状态：pending/processing/success/failed' AFTER stock_code_id,
ADD COLUMN download_progress FLOAT DEFAULT 0.0 COMMENT '下载进度(0-100)' AFTER download_status,
ADD COLUMN error_message TEXT COMMENT '错误信息' AFTER download_progress;

-- 添加数据统计字段
ALTER TABLE record_stock_minute 
ADD COLUMN total_records INT DEFAULT 0 COMMENT '总记录数' AFTER error_message,
ADD COLUMN downloaded_records INT DEFAULT 0 COMMENT '已下载记录数' AFTER total_records,
ADD COLUMN last_download_time DATETIME COMMENT '最后下载时间' AFTER downloaded_records;

-- 添加时间戳字段
ALTER TABLE record_stock_minute 
ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间' AFTER last_download_time,
ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间' AFTER created_at;

-- 添加外键约束（可选，如果stock_market_data表存在）
-- ALTER TABLE record_stock_minute 
-- ADD CONSTRAINT fk_record_stock_minute_stock_code_id 
-- FOREIGN KEY (stock_code_id) REFERENCES stock_market_data(id);

-- 添加索引以提高查询性能
ALTER TABLE record_stock_minute 
ADD INDEX idx_stock_code_id (stock_code_id),
ADD INDEX idx_download_status (download_status),
ADD INDEX idx_record_date (record_date);

-- 验证表结构
DESCRIBE record_stock_minute; 