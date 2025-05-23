from file_path import *


def my_url(pp: str):
    """
    find my url setting
    """
    ppl = os.path.join(password_path, 'EastMoney', f'Url_{pp}.txt')
    f2 = open(ppl, 'r')
    lines = f2.readlines()
    url = lines[0]
    url = url.strip('\n')
    url = url.replace(' ', '')
    return url


def my_headers(pp: str):

    """
    read header code_data
    save to different web heaer to txt and read txt;
    """
    h = {}

    pph = os.path.join(password_path, 'EastMoney', f'header_{pp}.txt')
    f2 = open(pph, 'r')
    lines = f2.readlines()

    for line in lines:
        line = line.strip('\n')
        line = line.replace(' ', '')
        line = line.split(':')
        keys = line[0]
        values = line[1]
        h[keys] = values

    return h


if __name__ == '__main__':
    p = file_root()
    print(p)
