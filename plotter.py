import os
import abc
import csv
import cv2
import jieba
import random
import imageio
import librosa
import numpy as np
from PIL import Image
import librosa.display
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


class plotter(abc.ABC):
    @abc.abstractclassmethod
    def plot(data, *args, **kwargs):
        pass


class Point():
    def __init__(self, x, y):
        self.x = x
        self.y = y


class PointPlotter(plotter):
    def plot(data):
        x_lis = []
        y_lis = []
        for i in data:
            x_lis.append(i.x)
            y_lis.append(i.y)
        plt.scatter(x_lis, y_lis)
        plt.show()


class ArrayPlotter(plotter):
    def plot(data):
        dimension = len(data)
        if dimension == 2:
            plt.scatter(data[0], data[1])
            plt.show()
        elif dimension == 3:
            fig = plt.figure()
            ax = fig.gca(projection="3d")
            ax.scatter(data[0], data[1], data[2])
            ax.set(xlabel="X", ylabel="Y", zlabel="Z")
            plt.show()
        else:
            print("\n\n--!!ERROR!!--\n\n")


class TextPoltter(plotter):
    def plot(data):
        words = []
        for item in data[0]:
            word_lis = list(jieba.lcut(item))
            for word in word_lis:
                if word not in data[1]:
                    words.append(word)
        dict = {}
        for item in words:
            dict[item] = dict.get(item, 0) + 1
        sortword = sorted(dict.items(), key=lambda x: x[1], reverse=True)
        dic = {}
        for item in sortword:
            dic[item[0]] = item[1]
        wcd = WordCloud('C:/Windows/Fonts/simkai.ttf', background_color='white')
        wcd.generate_from_frequencies(dic)
        plt.imshow(wcd)
        plt.axis('off')
        plt.show()


class ImagePoltter(plotter):
    def plot(data):
        filepath, row, col = data[0], data[1], data[2]
        image_lis = []
        if os.path.isfile(filepath):
            image_lis.append(Image.open(filepath))
        else:
            for file in os.listdir(filepath):
                if file.split('.')[-1] == "jpg":
                    image_lis.append(Image.open(filepath + '\\' + file))
        for i in range(row * col):
            if i >= len(image_lis):
                break
            plt.subplot(row, col, i + 1)
            plt.axis('off')
            plt.imshow(image_lis[i])
        plt.show()


class GifPlotter(plotter):
    def plot(data):
        filepath, outPath = data[0], data[1]
        image_lis = []
        if os.path.isfile(filepath):
            image_lis.append(imageio.imread(filepath))
        else:
            for file in os.listdir(filepath):
                if file.split('.')[-1] == "jpg":
                    image_lis.append(imageio.imread(filepath + '\\' + file))
        imageio.mimsave(outPath, image_lis, 'GIF', duration=0.5)


class KeyFeaturePlooter(plotter):
    def plot(data):
        if len(data) > 3:
            mat = np.array(data)
            mat = np.transpose(mat)
            pca = PCA(n_components=3)
            mat = pca.fit_transform(mat)
            mat = np.transpose(mat)
            ArrayPlotter.plot(mat)


class MusickPlotter(plotter):
    def plot(data):
        signal, sr = librosa.load(data, sr=None)
        librosa.display.waveshow(signal, sr)
        plt.xlabel('time')
        plt.ylabel('amplitude')
        plt.show()


class VideoPlooter(plotter):
    def plot(data):
        videopath, outpath = data[0], data[1]
        cap = cv2.VideoCapture(videopath)
        success, frame = cap.read()
        i = 0
        while success:
            i += 1
            image_path = f'{outpath}\\{i}.jpg'
            cv2.imwrite(image_path, frame)
            success, frame = cap.read()
        GifPlotter.plot([outpath, outpath + '\\res.gif'])


if __name__ == '__main__':

    points = []
    for i in range(15):
        point = Point(random.randint(0, 10), random.randint(0, 10))
        points.append(point)
    PointPlotter.plot(points)

    array_x = []
    array_y = []
    array_z = []
    for i in range(15):
        array_x.append(random.randint(0, 10))
        array_y.append(random.randint(0, 10))
        array_z.append(random.randint(0, 10))
    ArrayPlotter.plot([array_x, array_y])
    ArrayPlotter.plot([array_x, array_y, array_z])

    textFile = "E:\\code-Python\\week2\\danmuku.csv"
    stopwordsfile = "E:\\code-Python\\week2\\stopwords_list.txt"
    with open(stopwordsfile, mode='r', encoding='utf-8') as inFile:
        stopwords = [s.rstrip() for s in inFile.readlines()]
        stopwords.append(" ")
    text = []
    with open(textFile, mode='r', encoding='utf-8') as inFile:
        danmu_lis = list(csv.reader(inFile))
    for i in range(10000):
        text.append(danmu_lis[i + 1][0])
    TextPoltter.plot([text, stopwords])

    ImageFile = "D:\\data\\plotter\\Iamge"
    row, col = 2, 3
    ImagePoltter.plot([ImageFile, row, col])

    outPath = "D:\\data\\plotter\\result\\new.gif"
    GifPlotter.plot([ImageFile, outPath])

    array_h = []
    for i in range(15):
        array_h.append(random.randint(0, 10))
    KeyFeaturePlooter.plot([array_x, array_y, array_z, array_h])

    MusicPath = "D:\\data\\Decorate\\sound\\test.wav"
    MusickPlotter.plot(MusicPath)

    VideoPath = "D:\\data\\plotter\\video\\test.mp4"
    video_to_Image = "D:\\data\\plotter\\video"
    VideoPlooter.plot([VideoPath, video_to_Image])
