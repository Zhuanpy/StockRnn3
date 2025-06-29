-- 数据库迁移查询SQL
-- 用途: 从 mystockrecord 数据库复制表结构和数据到 quanttradingsystem 数据库
-- 生成时间: 2024-12-19

USE quanttradingsystem;

SELECT 
    CONCAT(
        'CREATE TABLE quanttradingsystem.', table_name, ' LIKE mystockrecord.', table_name, '; ',
        'INSERT INTO quanttradingsystem.', table_name, ' SELECT * FROM mystockrecord.', table_name, ';'
    ) AS sql_statement
FROM information_schema.tables
WHERE table_schema = 'mystockrecord'; 