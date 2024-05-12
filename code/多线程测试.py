from Normal import ResampleData as rd
from MySql.DataBaseStockData1m import StockData1m as sd

if __name__ == '__main__':
    df = sd.load_1m('600000', "2024")
    print(df)
    data = rd.resample_fun(df, "15m")
    print(data)