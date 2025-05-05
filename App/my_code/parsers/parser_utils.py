import json
import os

current_dir  = os.path.dirname(os.path.abspath(__file__))

# 递归查找 Flask 应用根目录（假设 'app.py' 在根目录）
while current_dir and not os.path.exists(os.path.join(current_dir, 'app.py')):
    current_dir = os.path.dirname(current_dir)

def read_columns():
    path_ = os.path.join(current_dir , 'App', 'my_code','code_data', 'columns', 'StockColumns.json')
    with open(f'{path_}', 'r') as f:
        col_ = json.load(f)
    return col_

