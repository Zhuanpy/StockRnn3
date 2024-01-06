import json
from root_ import file_root
import os

_path = file_root()  # 获取root file 路径


def read_columns():
    path_ = os.path.join(_path, 'data', 'columns', 'StockColumns.json')
    with open(f'{path_}', 'r') as f:
        col_ = json.load(f)

    return col_


if __name__ == '__main__':
    p = file_root()
    print(p)
