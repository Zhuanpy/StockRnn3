# -*-coding:utf8-*-
import requests
import logging
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


def WebDriver():
    # 创建 ChromeDriver 服务
    service = Service(ChromeDriverManager().install())

    # 创建 Chrome 配置选项
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # 添加任何所需的配置选项

    # 使用服务和选项启动 WebDriver
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def page_source(url, headers=None, cookies=None, max_retries=5, retry_delay=2):
    i = 0

    while i < max_retries:

        try:
            r = requests.get(url, headers=headers, cookies=cookies, timeout=(5, 10)).text

            return r

        except requests.exceptions.Timeout as e:
            logging.error(f"Timeout error: {e}")
            i += 1

        except requests.exceptions.RequestException as e:
            logging.error(f"Request error: {e}")
            i += 1

        time.sleep(retry_delay)

    return None


def UrlCode(code: str):
    if code[0] == '0' or code[0] == '3':
        code = f'0.{code}'

    elif code[0] == '6':
        code = f'1.{code}'

    else:
        print(f'东方财富代码无分类:{code};')
        pass

    return code


if __name__ == '__main__':
    pass