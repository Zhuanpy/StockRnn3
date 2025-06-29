-- 数据迁移脚本：将 record_stock_minute_copy 表的数据导入到 record_stock_minute 表中
-- 使用SQL直接执行迁移

USE quanttradingsystem;

-- 1. 首先检查表是否存在
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'record_stock_minute_copy') 
        THEN 'record_stock_minute_copy 表存在' 
        ELSE 'record_stock_minute_copy 表不存在' 
    END AS source_table_status;

SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'record_stock_minute') 
        THEN 'record_stock_minute 表存在' 
        ELSE 'record_stock_minute 表不存在' 
    END AS target_table_status;

-- 2. 显示源表数据统计
SELECT 
    '源表数据统计' AS info,
    COUNT(*) AS total_records
FROM record_stock_minute_copy;

-- 3. 显示源表示例数据
SELECT 
    '源表示例数据' AS info,
    id,
    name,
    start_date,
    end_date,
    record_date
FROM record_stock_minute_copy 
LIMIT 5;

-- 4. 执行数据迁移
-- 注意：这里使用INSERT IGNORE来避免重复记录
INSERT IGNORE INTO record_stock_minute 
(stock_code_id, download_status, download_progress, start_date, end_date, record_date, 
 total_records, downloaded_records, created_at, updated_at)
SELECT 
    smd.id AS stock_code_id,
    'pending' AS download_status,
    0.0 AS download_progress,
    rsmc.start_date,
    rsmc.end_date,
    rsmc.record_date,
    0 AS total_records,
    0 AS downloaded_records,
    NOW() AS created_at,
    NOW() AS updated_at
FROM record_stock_minute_copy rsmc
LEFT JOIN stock_market_data smd ON rsmc.name = smd.name
WHERE smd.id IS NOT NULL;  -- 只迁移能找到对应股票ID的记录

-- 5. 显示迁移结果统计
SELECT 
    '迁移结果统计' AS info,
    COUNT(*) AS migrated_records
FROM record_stock_minute;

-- 6. 显示未成功迁移的记录（找不到对应股票ID的记录）
SELECT 
    '未成功迁移的记录' AS info,
    rsmc.id,
    rsmc.name,
    rsmc.start_date,
    rsmc.end_date,
    rsmc.record_date
FROM record_stock_minute_copy rsmc
LEFT JOIN stock_market_data smd ON rsmc.name = smd.name
WHERE smd.id IS NULL;

-- 7. 显示迁移后的示例数据
SELECT 
    '迁移后示例数据' AS info,
    rsm.id,
    rsm.stock_code_id,
    rsm.download_status,
    rsm.start_date,
    rsm.end_date,
    smd.name AS stock_name
FROM record_stock_minute rsm
LEFT JOIN stock_market_data smd ON rsm.stock_code_id = smd.id
LIMIT 5; 