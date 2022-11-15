import numpy as np
import random
import math
from PIL import Image
import os
import sys

FilePath = "D:\\data\\originalPics\\2002\\07\\19\\big"
TotalPath = "D:\\data\\originalPics"


def random_walk(mu, X_0, sigma_2, N):
    '''迭代生成N个随机变量'''
    i = 0
    sigma = math.sqrt(sigma_2)
    X_now = X_0
    X_next = mu + X_now + random.normalvariate(mu=mu, sigma=sigma)
    while i < N:
        yield X_next
        X_now = X_next
        X_next = mu + X_now + random.normalvariate(mu=mu, sigma=sigma)
        i += 1
    return 'done'


def multiple_random_walk(l_mu,  l_X_0,  l_sigma_2,  l_N):
    '''实现拼合多个random_walk的生成器,  以生成一组时间上对齐的多维随机游走序列'''
    return zip(random_walk(l_mu[0], l_X_0[0], l_sigma_2[0], l_N[0]),
               random_walk(l_mu[1], l_X_0[1], l_sigma_2[1], l_N[1]),
               random_walk(l_mu[2], l_X_0[2], l_sigma_2[2], l_N[2]))


class FaceDataset():
    def __init__(self,  PhotolisPath):
        self.PhotolisPath = PhotolisPath
        self.index = 0

    def _read(self, path):
        return np.array(Image.open(path))

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.PhotolisPath):
            img = self._read(self.PhotolisPath[self.index])
            self.index += 1
            return img
        else:
            raise StopIteration('图片已经加载完毕共{}'.format(self.index))


class Test():
    def __init__(self, path):
        self.path = path

    def tran(self):
        path = self.path
        pathlis = []
        for x in os.walk(path):
            lis = []
            if(len(x[2]) > 0):
                dirpath = x[0]
                for file in x[2]:
                    lis.append(dirpath+'\\'+file)
            pathlis.append(lis)
        a = []
        while a in pathlis:
            pathlis.remove(a)
        self.pathlis = pathlis

    def test_random_walk(self):
        walk = multiple_random_walk([0, 0, 0], [0, 0, 0], [1, 4, 8], [5, 4, 5])
        print(walk)
        for x in walk:
            print(x)

    def test_facedataset(self):
        facedatas = FaceDataset(self.pathlis[0])
        save_stdout = sys.stdout
        with open("D:\\data\\test.txt", mode='w', encoding='utf-8')as file:
            sys.stdout = file
            for face in facedatas:
                print(face)
        sys.stdout = save_stdout


if __name__ == '__main__':
    '''i = 0
    for x in os.walk(TotalPath):
        print(x)
        i+ = 1
        if i>=6:break'''
    test1 = Test(TotalPath)
    test1.test_random_walk()
    test1.tran()
    test1.test_facedataset()
