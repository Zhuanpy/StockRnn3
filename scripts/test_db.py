#!/usr/bin/env python3
"""
测试数据库连接
"""

import pymysql

def test_connection():
    print("测试数据库连接...")
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='651748264Zz',
            charset='utf8mb4'
        )
        
        print("✅ 数据库连接成功！")
        
        # 查看数据库
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = [row[0] for row in cursor.fetchall()]
            print(f"现有数据库: {databases}")
            
            # 检查源数据库
            if 'mystockrecord' in databases:
                print("✅ mystockrecord 数据库存在")
                
                # 查看表
                cursor.execute("USE mystockrecord")
                cursor.execute("SHOW TABLES")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"mystockrecord 中的表: {tables}")
            else:
                print("❌ mystockrecord 数据库不存在")
            
            # 检查目标数据库
            if 'quanttradingsystem' in databases:
                print("✅ quanttradingsystem 数据库存在")
            else:
                print("⚠️ quanttradingsystem 数据库不存在")
        
        connection.close()
        print("数据库连接已关闭")
        
    except Exception as e:
        print(f"❌ 连接失败: {str(e)}")

if __name__ == "__main__":
    test_connection() 