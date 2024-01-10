from file_path import *


def sql_password():
    path_ = os.path.join(password_path, 'sql.txt')
    f = open(path_, 'r')
    w = f.read()
    return w
