from LoadMysql import MyRecordStock

mr = MyRecordStock()
data = mr.load_basic_info_stock()

print(data)