import numpy as np
import imageio
import os


def to_npy_file(file_: str, nums=450):
    path_ = f'E:/Python/Project/Stock/Project_01/code/Dl_Strategy/Stock_RNN/data/output/MacdTrend/train/{file_}'
    os.chdir(path_)  # 切换python工作路径到你要操作的图片文件夹，mri_2d_test为我的图片文件夹

    a = np.zeros(0)
    i = 0

    for filename in os.listdir(path_):  # 使用os.listdir()获取该文件夹下每一张图片的名字
        im = imageio.imread(filename)
        im.shape = (1, im.shape[0], im.shape[1], im.shape[2])

        if not a.shape[0]:
            a = im

        else:
            a = np.append(a, im, axis=0)

        i += 1

        if i == nums:  # 190为文件夹中的图片数量
            break

    print(f'{file_} shape: {a.shape}')
    np.save(f'{file_}.npy', a)


def train_file():
    flies = ['_down', 'down_', '_up', 'up_']
    for file in flies:
        to_npy_file(file)


def train_data():
    x = np.zeros(0)
    y = np.zeros(0)
    flies = {'_down': 0, 'down_': 1, '_up': 2, 'up_': 3}

    for keys, values in flies.items():

        x_ = np.load(f'train/{keys}/{keys}.npy')
        # print(x_.shape)
        # exit()
        y_ = np.random.randint(values, (values + 1), (x_.shape[0], 1))

        if not x.shape[0]:
            x = x_
            y = y_

        else:
            x = np.append(x, x_, axis=0)
            y = np.append(y, y_, axis=0)

    print(f'X shape: {x.shape}, Y shape:{y.shape}')

    np.save('X.npy', x)
    np.save('Y.npy', y)


# train_file()

train_data()
