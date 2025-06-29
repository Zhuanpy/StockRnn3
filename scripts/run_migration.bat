@echo off
chcp 65001
echo 开始执行数据迁移脚本...
echo.

echo 方法1: 使用Python脚本迁移
python scripts/migrate_record_stock_minute_data.py

echo.
echo 方法2: 使用SQL脚本迁移（可选）
echo 请手动执行: scripts/migrate_record_stock_minute_data.sql

echo.
echo 迁移完成！
pause 