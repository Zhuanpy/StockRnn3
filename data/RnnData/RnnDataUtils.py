#  创建文件夹
import os
import shutil
from datetime import datetime, timedelta


def create_monthly_folders(start_month, end_month):
    script_directory = os.path.dirname(__file__)
    source_folder = os.path.join(script_directory, "CommonFile")

    start_date = datetime.strptime(start_month, "%Y-%m")
    end_date = datetime.strptime(end_month, "%Y-%m")

    # source_folder = "CommonFile"  # 请替换成你的实际源文件夹路径
    current_date = start_date
    while current_date <= end_date:
        current_month = current_date.strftime("%Y-%m")
        current_folder_path = os.path.join(script_directory, current_month)

        # 复制文件夹
        current_folder_path = os.path.join(script_directory, current_folder_path)
        shutil.copytree(source_folder, current_folder_path)

        print(f'复制完成: {current_month}')

        # 下一个月
        current_date += timedelta(days=31)


# 输入
if __name__ == "__main__":
    start_month = "2022-06"  # input("请输入开始月份（格式：YYYY-MM）：")
    end_month = "2024-12"  # input("请输入结束月份（格式：YYYY-MM）：")

    # target_folder = "目标文件夹"  # 请替换成你的实际目标文件夹路径
    # 调用函数
    create_monthly_folders(start_month, end_month)
