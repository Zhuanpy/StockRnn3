-- 删除旧的 download_1m_data 表
-- 注意：此操作不可逆，请确保数据已迁移完成

USE quanttradingsystem;

-- 检查表是否存在
SELECT COUNT(*) as table_exists 
FROM information_schema.tables 
WHERE table_schema = 'quanttradingsystem' 
AND table_name = 'download_1m_data';

-- 备份表结构（可选）
-- CREATE TABLE download_1m_data_backup AS SELECT * FROM download_1m_data;

-- 删除表
DROP TABLE IF EXISTS download_1m_data;

-- 验证表已删除
SELECT COUNT(*) as table_exists 
FROM information_schema.tables 
WHERE table_schema = 'quanttradingsystem' 
AND table_name = 'download_1m_data';

-- 显示当前表列表
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'quanttradingsystem' 
AND table_name LIKE '%download%' OR table_name LIKE '%record%'
ORDER BY table_name; 