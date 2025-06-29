-- 创建 record_stock_minute 表
-- 用于记录股票分钟数据下载状态和进度

USE quanttradingsystem;

CREATE TABLE IF NOT EXISTS `record_stock_minute` (
    `id` BIGINT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `stock_code_id` INT NOT NULL COMMENT '股票代码ID',
    `download_status` VARCHAR(20) DEFAULT 'pending' COMMENT '下载状态：pending/processing/success/failed',
    `download_progress` FLOAT DEFAULT 0.0 COMMENT '下载进度(0-100)',
    `error_message` TEXT COMMENT '错误信息',
    `start_date` DATE COMMENT '数据开始日期',
    `end_date` DATE COMMENT '数据结束日期',
    `record_date` DATE COMMENT '记录创建日期',
    `total_records` INT DEFAULT 0 COMMENT '总记录数',
    `downloaded_records` INT DEFAULT 0 COMMENT '已下载记录数',
    `last_download_time` DATETIME COMMENT '最后下载时间',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    PRIMARY KEY (`id`),
    INDEX `idx_stock_code_id` (`stock_code_id`),
    INDEX `idx_download_status` (`download_status`),
    INDEX `idx_created_at` (`created_at`),
    
    -- 外键约束（如果stock_market_data表存在）
    -- FOREIGN KEY (`stock_code_id`) REFERENCES `stock_market_data`(`id`) ON DELETE CASCADE
    
    -- 添加约束
    CONSTRAINT `chk_download_status` CHECK (`download_status` IN ('pending', 'processing', 'success', 'failed')),
    CONSTRAINT `chk_download_progress` CHECK (`download_progress` >= 0 AND `download_progress` <= 100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票分钟数据下载记录表';

-- 插入一些示例数据（可选）
-- INSERT INTO `record_stock_minute` (`stock_code_id`, `download_status`, `record_date`) 
-- VALUES (1, 'pending', CURDATE()); 