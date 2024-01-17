from LoadMysql import LoadBasic
from DataBaseStockPool import TableStockBoard, TableStockPool


def print_fun(pool, basic):
    print(pool)
    print(basic)
    exit()


pool = TableStockBoard.load_board()
pool = pool.sort_values(by=['code']).reset_index(drop=True)

basic = LoadBasic.load_basic()

basic = basic[basic['name'].isin(pool['name'])]

basic = basic.sort_values(by=['code']).reset_index(drop=True)
pool['id'] = basic['id']

# 替换目标
TableStockBoard.replace_board(pool)
