import json
import pandas as pd
import numpy as np
import os
from App.my_code.utils.Normal import ResampleData
from App.my_code.Signals.StatisticsMacd import SignalMethod
# 可信区间标准分数
Z_95 = 1.65
Z_98 = 2.33

# 缓存文件路径
CACHE_FILE = "./cache/extreme_values.json"  # 现在使用 JSON 文件保存缓存
os.makedirs("./cache", exist_ok=True)


def load_extreme_values():
    """加载所有股票的极值数据"""
    if not os.path.exists(CACHE_FILE) or os.stat(CACHE_FILE).st_size == 0:
        # 文件不存在或为空，返回空字典
        return {}

    try:
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)

    except Exception as e:
        print(f"读取缓存文件出错: {e}")
        return {}


def save_extreme_values(cache_dict):
    """保存所有股票的极值数据"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_dict, f, indent=4)

    except Exception as e:
        print(f"保存缓存文件出错: {e}")


def calculate_extreme_values(cols_to_standardize):
    """计算标准化所需的极值"""
    extreme_values = {
        "lower_95": {col: np.nan for col in cols_to_standardize},
        "lower_98": {col: np.nan for col in cols_to_standardize},
        "upper_95": {col: np.nan for col in cols_to_standardize},
        "upper_98": {col: np.nan for col in cols_to_standardize}
    }

    # 假设计算极值的方法如下
    for col in cols_to_standardize:
        extreme_values["lower_95"][col] = 100  # 示例值，根据实际需要调整
        extreme_values["lower_98"][col] = 50
        extreme_values["upper_95"][col] = 200
        extreme_values["upper_98"][col] = 250

    return extreme_values


def get_extreme_values(stock_symbol, cols_to_standardize, cache_dict):
    """获取某只股票的极值数据，如果没有则计算并返回"""
    # 使用字典的方式来检查是否有股票数据
    if stock_symbol in cache_dict:
        return cache_dict[stock_symbol]
    else:
        # 如果缓存里没有数据，计算并返回
        extreme_values = calculate_extreme_values(cols_to_standardize)  # 计算极值
        cache_dict[stock_symbol] = extreme_values  # 将数据存入缓存字典
        save_extreme_values(cache_dict)  # 保存整个缓存
        return extreme_values


def clean_and_standardize(stock_symbol, df, cache_dict):
    """去除极端值，并进行 Z-score 标准化"""
    cols_to_standardize = ['open', 'high', 'low', 'close', 'volume']

    extreme_values = get_extreme_values(stock_symbol, df[cols_to_standardize], cache_dict)

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
data_bath_path = "E:/MyProject/MyStock/MyStock/Stock_RNN/App/static/data/years"
output_15m_folder = f"{data_bath_path}/15m"

os.makedirs(output_15m_folder, exist_ok=True)

# 载入缓存
cache_df = load_extreme_values()

# 读取目标年份数据
year = "2020"
data_1m_folder = os.path.join(data_bath_path, year, "1m")
last_year = str(int(year) - 1)
data_1m_last_year_folder = os.path.join(data_bath_path, last_year, "1m")

for file in os.listdir(data_1m_folder):

    if file.endswith('.csv'):
        stock_symbol = file.replace('.csv', '')
        file_path = os.path.join(data_1m_folder, file)

        # 读取数据
        df_1m = pd.read_csv(file_path, parse_dates=['date'])

        try:
            df_1m_last_year = pd.read_csv(os.path.join(data_1m_last_year_folder, file), parse_dates=['date'])
            df_1m = pd.concat([df_1m_last_year, df_1m], ignore_index=True)

        except:
            pass

        # 计算 15 分钟数据
        df_15m = ResampleData.resample_1m_data(df_1m, '15m')
        df_15m = SignalMethod.signal_by_MACD_3ema(df_15m, df_1m)

        # 计算年份和季度
        df_15m['Year'] = df_15m['date'].dt.year
        df_15m['Quarter'] = df_15m['date'].dt.quarter
        df_15m['Year_Quarter'] = df_15m['Year'].astype(str) + "_Q" + df_15m['Quarter'].astype(str)

        df_15m =df_15m[(df_15m['Year'] == int(year)) & (~df_15m['Signal'].isnull( ))]

        # 15m 数据处理完成，保存到文件夹中
        df_15m.to_csv(os.path.join(output_15m_folder, f"{stock_symbol}.csv"), index=False)
        # df_15m = df_15m[df_15m['Year'] == int(year)]
        # MACD 计算
        print(df_15m)
        exit()


        print(f"✅ {stock_symbol} 数据处理完成，已存储！")


def process_stock_data_for_year(year, data_base_path="E:/MyProject/MyStock/MyStock/Stock_RNN/App/static/code_data/years"):
    output_15m_folder = f"{data_base_path}/15m"
    os.makedirs(output_15m_folder, exist_ok=True)
    
    # 载入缓存
    cache_df = load_extreme_values()

    # 读取目标年份数据
    data_1m_folder = os.path.join(data_base_path, year, "1m")
    last_year = str(int(year) - 1)
    data_1m_last_year_folder = os.path.join(data_base_path, last_year, "1m")

    for file in os.listdir(data_1m_folder):
        if not file.endswith('.csv'):
            continue
            
        try:
            stock_symbol = file.replace('.csv', '')
            file_path = os.path.join(data_1m_folder, file)

            # 读取数据
            df_1m = pd.read_csv(file_path, parse_dates=['date'])

            try:
                df_1m_last_year = pd.read_csv(os.path.join(data_1m_last_year_folder, file), parse_dates=['date'])
                df_1m = pd.concat([df_1m_last_year, df_1m], ignore_index=True)
            except Exception as e:
                print(f"警告: 无法读取去年数据 {stock_symbol}: {str(e)}")

            # 计算 15 分钟数据
            df_15m = ResampleData.resample_1m_data(df_1m, '15m')
            df_15m = SignalMethod.signal_by_MACD_3ema(df_15m, df_1m)

            # 计算年份和季度
            df_15m['Year'] = df_15m['date'].dt.year
            df_15m['Quarter'] = df_15m['date'].dt.quarter
            
            # 筛选目标年份的有效数据
            df_15m = df_15m[(df_15m['Year'] == int(year)) & (~df_15m['Signal'].isnull())]
            
            # 按季度处理数据
            for quarter in df_15m['Quarter'].unique():
                quarter_data = df_15m[df_15m['Quarter'] == quarter].copy()
                if not quarter_data.empty:
                    process_15M_data_stand(
                        quarter_data, 
                        stock_symbol,
                        year,
                        quarter,
                        output_15m_folder,
                        cache_df
                    )

            print(f"✅ {stock_symbol} 全部数据处理完成")
            
        except Exception as e:
            print(f"❌ 处理 {stock_symbol} 时发生错误: {str(e)}")
            continue


def process_15M_data_stand(df_15m, stock_symbol, year, quarter, output_base_path, cache_df=None):
    """
    处理15分钟数据的标准化和存储
    
    Args:
        df_15m (pd.DataFrame): 15分钟数据框
        stock_symbol (str): 股票代码
        year (str): 年份
        quarter (str): 季度
        output_base_path (str): 输出基础路径
        cache_df (dict, optional): 缓存数据字典
    
    Returns:
        bool: 处理是否成功
    """
    try:
        if cache_df is None:
            cache_df = load_extreme_values()
            
        # 进行标准化
        df_15m = clean_and_standardize(stock_symbol, df_15m, cache_df)
        
        # 确保输出路径存在
        stock_output_folder = os.path.join(output_base_path, stock_symbol)
        os.makedirs(stock_output_folder, exist_ok=True)
        
        # 按年份和季度分组存储
        year_quarter = f"{year}_Q{quarter}"
        output_file = os.path.join(stock_output_folder, f"{year_quarter}.csv")
        
        # 保存数据
        df_15m.to_csv(output_file, index=False)
        
        print(f"✅ {stock_symbol} {year_quarter} 数据标准化处理完成")
        return True
        
    except Exception as e:
        print(f"❌ 处理 {stock_symbol} {year_quarter} 数据时出错: {str(e)}")
        return False

# 示例调用
# process_stock_data_for_year("2020")
