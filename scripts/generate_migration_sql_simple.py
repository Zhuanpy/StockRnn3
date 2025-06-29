#!/usr/bin/env python3
"""
简化版数据库迁移SQL生成脚本（无需数据库连接）

直接生成从 mystockrecord 数据库复制表结构和数据到 quanttradingsystem 数据库的 SQL 语句
"""

from datetime import datetime


def generate_migration_sql():
    """
    生成数据库迁移SQL语句
    
    Returns:
        str: 生成的SQL语句
    """
    # 直接使用你提供的SQL查询
    sql_query = """
USE quanttradingsystem;

SELECT 
    CONCAT(
        'CREATE TABLE quanttradingsystem.', table_name, ' LIKE mystockrecord.', table_name, '; ',
        'INSERT INTO quanttradingsystem.', table_name, ' SELECT * FROM mystockrecord.', table_name, ';'
    ) AS sql_statement
FROM information_schema.tables
WHERE table_schema = 'mystockrecord';
"""
    
    return sql_query


def generate_direct_sql():
    """
    生成直接的SQL语句（用于手动执行）
    
    Returns:
        str: 生成的SQL语句
    """
    # 这里你可以手动添加需要迁移的表名
    # 或者先运行上面的查询获取表名列表
    tables = [
        # 添加你的表名，例如：
        # 'accounts',
        # 'positions', 
        # 'trade_records',
        # 'trade_signals',
        # 'rnn_training_records',
        # 'rnn_running_records',
        # 'count_board',
        # 'count_stock_pool',
        # 'stock_basic_information_others_code',
        # 'stock_basic_information_stock',
        # 'stock_daily',
        # 'stock_1m',
        # 'stock_15m',
        # 'funds_awkward',
        # 'download_1m_record',
        # 'top500_fund_record',
        # 'issue'
    ]
    
    sql_statements = []
    sql_statements.append("USE quanttradingsystem;")
    sql_statements.append("")
    
    for table in tables:
        create_sql = f"CREATE TABLE quanttradingsystem.{table} LIKE mystockrecord.{table};"
        insert_sql = f"INSERT INTO quanttradingsystem.{table} SELECT * FROM mystockrecord.{table};"
        
        sql_statements.append(f"-- 处理表: {table}")
        sql_statements.append(create_sql)
        sql_statements.append(insert_sql)
        sql_statements.append("")
    
    return "\n".join(sql_statements)


def save_sql_to_file(sql_content, filename=None):
    """
    保存SQL内容到文件
    
    Args:
        sql_content: SQL内容
        filename: 文件名，如果为None则自动生成
    """
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"migration_{timestamp}.sql"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("-- 数据库迁移脚本\n")
            f.write(f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-- 用途: 从 mystockrecord 数据库复制表结构和数据到 quanttradingsystem 数据库\n\n")
            f.write(sql_content)
            f.write("\n-- 迁移完成\n")
        
        print(f"SQL文件已保存: {filename}")
        return filename
    except Exception as e:
        print(f"保存文件失败: {str(e)}")
        return None


def main():
    """主函数"""
    print("数据库迁移SQL生成工具")
    print("="*50)
    print("选择生成方式:")
    print("1. 生成查询SQL（用于获取表名）")
    print("2. 生成直接迁移SQL（需要手动添加表名）")
    
    choice = input("请选择 (1 或 2): ").strip()
    
    if choice == "1":
        sql_content = generate_migration_sql()
        print("\n生成的查询SQL:")
        print("-" * 40)
        print(sql_content)
        
        # 保存查询SQL
        filename = save_sql_to_file(sql_content, "migration_query.sql")
        
        print(f"\n查询SQL已保存到: {filename}")
        print("使用方法:")
        print("1. 在MySQL中执行这个查询")
        print("2. 复制查询结果中的sql_statement列")
        print("3. 在MySQL中执行复制的SQL语句")
        
    elif choice == "2":
        sql_content = generate_direct_sql()
        
        if not sql_content.strip().endswith("USE quanttradingsystem;"):
            print("\n生成的直接迁移SQL:")
            print("-" * 40)
            print(sql_content)
            
            # 保存直接SQL
            filename = save_sql_to_file(sql_content, "migration_direct.sql")
            
            print(f"\n直接迁移SQL已保存到: {filename}")
            print("使用方法:")
            print("1. 在MySQL中直接执行这个SQL文件")
            print("2. 或者使用命令行: mysql -u root -p < migration_direct.sql")
        else:
            print("\n请在脚本中手动添加需要迁移的表名")
            print("编辑 generate_direct_sql() 函数中的 tables 列表")
    
    else:
        print("无效选择")


if __name__ == "__main__":
    main() 