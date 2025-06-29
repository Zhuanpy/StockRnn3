-- 数据库迁移脚本
-- 生成时间: 2025-06-28 13:29:36
-- 用途: 从 mystockrecord 数据库复制表结构和数据到 quanttradingsystem 数据库

USE quanttradingsystem;

-- 1. 处理表: basic_info_others_code
CREATE TABLE quanttradingsystem.basic_info_others_code LIKE mystockrecord.basic_info_others_code;
INSERT INTO quanttradingsystem.basic_info_others_code SELECT * FROM mystockrecord.basic_info_others_code;

-- 2. 处理表: count_board
CREATE TABLE quanttradingsystem.count_board LIKE mystockrecord.count_board;
INSERT INTO quanttradingsystem.count_board SELECT * FROM mystockrecord.count_board;

-- 3. 处理表: count_stock_pool
CREATE TABLE quanttradingsystem.count_stock_pool LIKE mystockrecord.count_stock_pool;
INSERT INTO quanttradingsystem.count_stock_pool SELECT * FROM mystockrecord.count_stock_pool;

-- 4. 处理表: download_1m_data
CREATE TABLE quanttradingsystem.download_1m_data LIKE mystockrecord.download_1m_data;
INSERT INTO quanttradingsystem.download_1m_data SELECT * FROM mystockrecord.download_1m_data;

-- 5. 处理表: record_stock_pool
CREATE TABLE quanttradingsystem.record_stock_pool LIKE mystockrecord.record_stock_pool;
INSERT INTO quanttradingsystem.record_stock_pool SELECT * FROM mystockrecord.record_stock_pool;

-- 6. 处理表: record_trading
CREATE TABLE quanttradingsystem.record_trading LIKE mystockrecord.record_trading;
INSERT INTO quanttradingsystem.record_trading SELECT * FROM mystockrecord.record_trading;

-- 7. 处理表: recordtopfunds500
CREATE TABLE quanttradingsystem.recordtopfunds500 LIKE mystockrecord.recordtopfunds500;
INSERT INTO quanttradingsystem.recordtopfunds500 SELECT * FROM mystockrecord.recordtopfunds500;

-- 8. 处理表: rnn_running_records
CREATE TABLE quanttradingsystem.rnn_running_records LIKE mystockrecord.rnn_running_records;
INSERT INTO quanttradingsystem.rnn_running_records SELECT * FROM mystockrecord.rnn_running_records;

-- 9. 处理表: rnn_training_records
CREATE TABLE quanttradingsystem.rnn_training_records LIKE mystockrecord.rnn_training_records;
INSERT INTO quanttradingsystem.rnn_training_records SELECT * FROM mystockrecord.rnn_training_records;

-- 10. 处理表: stock_classification
CREATE TABLE quanttradingsystem.stock_classification LIKE mystockrecord.stock_classification;
INSERT INTO quanttradingsystem.stock_classification SELECT * FROM mystockrecord.stock_classification;

-- 11. 处理表: stock_issue
CREATE TABLE quanttradingsystem.stock_issue LIKE mystockrecord.stock_issue;
INSERT INTO quanttradingsystem.stock_issue SELECT * FROM mystockrecord.stock_issue;

-- 迁移完成
-- 请检查数据完整性
