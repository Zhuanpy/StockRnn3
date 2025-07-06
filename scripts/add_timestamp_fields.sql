-- 添加时间戳字段到recordtopfunds500表
-- 运行此脚本前请先备份数据库

USE quanttradingsystem;

-- 检查表是否存在
SELECT COUNT(*) as table_exists 
FROM information_schema.tables 
WHERE table_schema = 'quanttradingsystem' 
AND table_name = 'recordtopfunds500';

-- 显示当前表结构
DESCRIBE recordtopfunds500;

-- 添加created_at字段（如果不存在）
ALTER TABLE recordtopfunds500 
ADD COLUMN IF NOT EXISTS `created_at` TIMESTAMP NULL DEFAULT NULL COMMENT '创建时间';

-- 添加updated_at字段（如果不存在）
ALTER TABLE recordtopfunds500 
ADD COLUMN IF NOT EXISTS `updated_at` TIMESTAMP NULL DEFAULT NULL COMMENT '更新时间';

-- 显示更新后的表结构
DESCRIBE recordtopfunds500;

-- 更新现有记录的时间戳
UPDATE recordtopfunds500 
SET created_at = NOW(), updated_at = NOW() 
WHERE created_at IS NULL OR updated_at IS NULL;

-- 显示更新结果
SELECT COUNT(*) as total_records,
       COUNT(created_at) as records_with_created_at,
       COUNT(updated_at) as records_with_updated_at
FROM recordtopfunds500; 