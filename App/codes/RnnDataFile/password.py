import os
from App.static import file_root
from config import Config

password_path = os.path.join(file_root(), 'code_data', 'password')


def sql_password():
    path_ = os.path.join(password_path, 'sql.txt')
    f = open(path_, 'r')
    w = f.read()
    return w


class XueqiuParam:
    folder = "XueQiu"

    @classmethod
    def cookies(cls):
        return Config.get_xueqiu_cookies()

    @classmethod
    def headers(cls):
        return Config.get_xueqiu_headers()


if __name__ == '__main__':
    r = XueqiuParam.headers()
    print(r)
