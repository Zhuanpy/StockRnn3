# -*-coding:utf8-*-

import requests
from selenium import webdriver
import logging
import time


def WebDriver():
    driver = webdriver.Chrome()
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
