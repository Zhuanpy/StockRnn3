USE quanttradingsystem;

-- 添加created_at字段
ALTER TABLE recordtopfunds500 
ADD COLUMN `created_at` TIMESTAMP NULL DEFAULT NULL COMMENT '创建时间';

-- 添加updated_at字段
ALTER TABLE recordtopfunds500 
ADD COLUMN `updated_at` TIMESTAMP NULL DEFAULT NULL COMMENT '更新时间';

-- 验证字段是否添加成功
DESCRIBE recordtopfunds500; 