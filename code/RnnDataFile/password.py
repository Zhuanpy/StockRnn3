import os
from root_ import file_root

password_path = os.path.join(file_root(), 'data', 'password')


def sql_password():
    path_ = os.path.join(password_path, 'sql.txt')
    f = open(path_, 'r')
    w = f.read()
    return w


class XueqiuParam:
    folder = "XueQiu"

    @classmethod
    def cookies(cls):
        p = os.path.join(password_path, cls.folder, "cookies.txt")
        f = open(p, 'r')
        cookies = {}
        for line in f.read().split(';'):
            name, value = line.strip().split('=', 1)
            cookies[name] = value

        return cookies

    @classmethod
    def headers(cls):
        path_ = os.path.join(password_path, cls.folder, "headers.txt")
        f = open(path_, 'r')
        h = {}
        for line in f.readlines():
            name, value = line.replace("'", "").replace('\n', '').split(': ', 1)

            h[name] = value

        return h


if __name__ == '__main__':
    r = XueqiuParam.headers()
    print(r)
