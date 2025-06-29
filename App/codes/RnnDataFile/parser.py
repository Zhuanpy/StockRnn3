from file_path import *
from config import Config


def my_url(pp: str):
    """
    find my url setting from config
    """
    return Config.get_eastmoney_urls(pp)


def my_headers(pp: str):
    """
    read header data from config
    """
    return Config.get_eastmoney_headers(pp)


if __name__ == '__main__':
    p = file_root()
    print(p)
