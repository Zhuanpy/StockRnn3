-- 为 download_1m_data 表添加缺少的字段
-- 根据 Download1MRecord 模型定义生成
-- 执行前请备份数据库

USE quanttradingsystem;

-- 检查表是否存在
SELECT COUNT(*) as table_exists 
FROM information_schema.tables 
WHERE table_schema = 'quanttradingsystem' 
AND table_name = 'download_1m_data';

-- 添加 download_status 字段
ALTER TABLE download_1m_data 
ADD COLUMN IF NOT EXISTS download_status VARCHAR(20) DEFAULT 'pending' COMMENT '下载状态';

-- 添加 error_message 字段
ALTER TABLE download_1m_data 
ADD COLUMN IF NOT EXISTS error_message TEXT COMMENT '错误信息';

-- 添加 created_at 字段
ALTER TABLE download_1m_data 
ADD COLUMN IF NOT EXISTS created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';

-- 添加 updated_at 字段
ALTER TABLE download_1m_data 
ADD COLUMN IF NOT EXISTS updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间';

-- 添加索引以提高查询性能
ALTER TABLE download_1m_data 
ADD INDEX IF NOT EXISTS idx_download_status (download_status),
ADD INDEX IF NOT EXISTS idx_created_at (created_at),
ADD INDEX IF NOT EXISTS idx_updated_at (updated_at);

-- 验证表结构
DESCRIBE download_1m_data;

-- 显示添加的字段
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = 'quanttradingsystem' 
AND TABLE_NAME = 'download_1m_data'
AND COLUMN_NAME IN ('download_status', 'error_message', 'created_at', 'updated_at'); 