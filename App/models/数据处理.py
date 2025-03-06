import pandas as pd
import numpy as np
import os

# 可信区间标准分数
Z_95 = 1.65
Z_98 = 2.33

# 缓存文件路径
CACHE_FILE = "./cache/extreme_values.csv"
os.makedirs("./cache", exist_ok=True)


def load_extreme_values():
    """加载缓存中的极值数据"""
    if os.path.exists(CACHE_FILE):
        return pd.read_csv(CACHE_FILE, index_col="Stock_Symbol")

    return pd.DataFrame()


def save_extreme_values(cache_df):
    """保存极值数据到缓存"""
    cache_df.to_csv(CACHE_FILE)


def get_extreme_values(stock_symbol, df, cache_df):
    """获取股票的极值数据，若缓存存在则直接加载，否则计算并缓存"""
    if stock_symbol in cache_df.index:
        return cache_df.loc[stock_symbol]

    # 计算极值范围
    mean = df.mean()
    std = df.std()

    extreme_values = {
        "lower_95": mean - Z_95 * std,
        "lower_98": mean - Z_98 * std,
        "upper_95": mean + Z_95 * std,
        "upper_98": mean + Z_98 * std
    }

    # 保存到缓存
    cache_df.loc[stock_symbol] = extreme_values
    save_extreme_values(cache_df)

    return extreme_values


def clean_and_standardize(stock_symbol, df, cache_df):

    """去除极端值，并进行 Z-score 标准化"""
    cols_to_standardize = ['Open', 'High', 'Low', 'Close', 'Volume']

    extreme_values = get_extreme_values(stock_symbol, df[cols_to_standardize], cache_df)

    for col in cols_to_standardize:
        lower_95, lower_98 = extreme_values["lower_95"][col], extreme_values["lower_98"][col]
        upper_95, upper_98 = extreme_values["upper_95"][col], extreme_values["upper_98"][col]

        # 处理极端值
        df.loc[df[col] > upper_98, col] = np.random.uniform(upper_95, upper_98, df[col].gt(upper_98).sum())
        df.loc[df[col] < lower_98, col] = np.random.uniform(lower_98, lower_95, df[col].lt(lower_98).sum())

        # 标准化
        mean, std = df[col].mean(), df[col].std()
        df[col] = (df[col] - mean) / std

    return df


# 处理所有股票数据
data_folder = "./stock_data"
output_folder = "./processed_data"
os.makedirs(output_folder, exist_ok=True)

# 载入缓存
cache_df = load_extreme_values()

for file in os.listdir(data_folder):

    if file.endswith('.csv'):
        stock_symbol = file.replace('.csv', '')
        file_path = os.path.join(data_folder, file)

        # 读取数据
        df = pd.read_csv(file_path, parse_dates=['Datetime'])

        # 计算 15 分钟 MACD
        df = df.set_index('Datetime').resample('15T').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna().reset_index()

        # 计算 MACD
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # 计算年份和季度
        df['Year'] = df['Datetime'].dt.year
        df['Quarter'] = df['Datetime'].dt.quarter
        df['Year_Quarter'] = df['Year'].astype(str) + "_Q" + df['Quarter'].astype(str)

        # 进行标准化（使用缓存优化）
        df = clean_and_standardize(stock_symbol, df, cache_df)

        # 按季度存储
        stock_output_folder = os.path.join(output_folder, stock_symbol)

        os.makedirs(stock_output_folder, exist_ok=True)

        for (year_quarter), group in df.groupby('Year_Quarter'):
            output_file = os.path.join(stock_output_folder, f"{year_quarter}.csv")
            group.to_csv(output_file, index=False)

        print(f"✅ {stock_symbol} 数据处理完成，已存储！")
