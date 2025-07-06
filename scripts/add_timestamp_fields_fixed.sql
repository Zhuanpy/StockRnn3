USE quanttradingsystem;

-- 检查并添加created_at字段
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'quanttradingsystem' 
     AND TABLE_NAME = 'recordtopfunds500' 
     AND COLUMN_NAME = 'created_at') = 0,
    'ALTER TABLE recordtopfunds500 ADD COLUMN `created_at` TIMESTAMP NULL DEFAULT NULL COMMENT ''创建时间''',
    'SELECT ''created_at column already exists'' as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 检查并添加updated_at字段
SET @sql = (SELECT IF(
    (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
     WHERE TABLE_SCHEMA = 'quanttradingsystem' 
     AND TABLE_NAME = 'recordtopfunds500' 
     AND COLUMN_NAME = 'updated_at') = 0,
    'ALTER TABLE recordtopfunds500 ADD COLUMN `updated_at` TIMESTAMP NULL DEFAULT NULL COMMENT ''更新时间''',
    'SELECT ''updated_at column already exists'' as message'
));
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 验证字段是否添加成功
DESCRIBE recordtopfunds500; 