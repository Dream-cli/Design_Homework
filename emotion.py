#utf-8

import re
import jieba
import numpy as np
import matplotlib.pyplot as plt
from math import sin, asin, cos, radians, fabs, sqrt

EARTH_RADIUS = 6371     #地球半径6371km

emo_index = {
    'anger'  : 0,
    'disgust': 1,
    'fear'   : 2,
    'joy'    : 3,
    'sadness': 4
}

emo_color = {
    'anger'  : 'r',
    'disgust': 'm',
    'fear'   : 'k',
    'joy'    : 'y',
    'sadness': 'b'
}

city_coord = {
    'beijing'  : [39.92, 116.46],
    'shanghai' : [31.22, 121.48],
    'guangzhou': [23.16, 113.23],
    'chengdu'  : [30.67, 104.06]
}

anger='E:/code-Python/week3/emotion_lexicon/anger.txt'
disgust='E:/code-Python/week3/emotion_lexicon/disgust.txt'
fear='E:/code-Python/week3/emotion_lexicon/fear.txt'
joy='E:/code-Python/week3/emotion_lexicon/joy.txt'
sadness='E:/code-Python/week3/emotion_lexicon/sadness.txt'

def txt_dispart(path):
    '''读取文件并将location&text&user_id&created_time分开'''
    pass
    txt_new=[]
    dic={}
    with open(path,mode='r',encoding='utf-8')as f:
        txt=[s.rstrip() for s in f.readlines()]
    for item in txt:
        txt_new.append(item.split('\t'))
    weibo_location,weibo_text,user_id,created_time=[],[],[],[]
    del txt_new[0]
    for item in txt_new:
        weibo_location.append(item[0])
        weibo_text.append(item[1])
        user_id.append(item[2])
        created_time.append(item[3])
    '''位置分割'''
    loc=[]
    for item in weibo_location:
        item.rstrip('[]')
        s=item.split(",")
        s[0]=float(s[0][1:])
        s[1]=float(s[1][1:-1])
        loc.append(s)
    dic['location']=loc
    dic['word']=weibo_text
    dic['id']=user_id
    '''时间分割'''
    t=[]
    for item in created_time:
        t.append(item.split(" "))
    dic['time']=t
    return dic
    
def txt_add(anger,disgust,fear,joy,sadness):
    '''将情绪词文件加入jieba库的自定义词典'''
    pass
    jieba.load_userdict(anger)
    jieba.load_userdict(disgust)
    jieba.load_userdict(fear)
    jieba.load_userdict(joy)
    jieba.load_userdict(sadness)
    return 1

def txt_read(path):
    '''txt文件读取'''
    pass
    with open(path,mode = 'r',encoding='utf-8') as file:
        txt=[s.rstrip() for s in file.readlines()]
    txt.append(" ")
    return txt

def data_wash(word,stopwords):
    '''进行数据清洗'''
    pass
    after=[]
    URL_REGEX = re.compile('(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?',
    re.IGNORECASE)
    for text in word:
        text = re.sub(URL_REGEX,"",text)#去除网址
        text = re.sub(r'[0-9.?,@\t]+','',text)#去除数字及部分符号
        after.append([word for word in jieba.lcut(text) if word not in stopwords])
    return after

def create_emo_vec(word,anger,disgust,fear,joy,sadness):
    '''构建情绪向量'''
    pass
    emo_lis=[]
    emo_lis.append(txt_read(anger))
    emo_lis.append(txt_read(disgust))
    emo_lis.append(txt_read(fear))
    emo_lis.append(txt_read(joy))
    emo_lis.append(txt_read(sadness))
    def emo_vec():
        '''构建向量'''
        nonlocal word,emo_lis
        stand=[0,0,0,0,0,0]       #[anger,disgust,fear,joy,sadness,max_index]
        for item in word:
            for i in range(5):
                if item in emo_lis[i]:
                    stand[i]+=1
        '''标准化向量'''
        s=sum(stand)
        if s!=0:
            for i in range(5):
                stand[i]/=s
            '''寻找MAX'''
            stand[5]=stand.index(max(stand))
        else:#没有情绪词
            stand[5]=-1
        return stand
    return emo_vec

def paint_time(word,data,mode,*emos):
    '''输入模式以及情绪类型得到情绪强度-时间折线图'''
    pass
    plt.figure(num=1)
    if mode == 'week':
        x = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for emo in emos:
            y = [0] * 7
            y_total = [0] * 7
            ind=0
            for item in data['time']:
                i = x.index(item[0])
                y[i]+=create_emo_vec(word[ind],anger,disgust,fear,joy,sadness)()[emo_index[emo]]
                y_total[i] += 1
                ind+=1
            for i in range(7):
                if y_total[i]!=0:
                    y[i] /= y_total[i]
            plt.plot(x, y, emo_color[emo])

    if mode == 'day':
        x = list(range(30))
        for emo in emos:
            y = [0] * 30
            y_total = [0] * 30
            ind=0
            for item in data['time']:
                i = int(item[2])
                y[i] +=create_emo_vec(word[ind],anger,disgust,fear,joy,sadness)()[emo_index[emo]]
                y_total[i] += 1
                ind+=1
            for i in range(24):
                if y_total[i]!=0:
                    y[i] /= y_total[i]
            plt.plot(x, y, emo_color[emo])
    plt.xticks(x)     
    plt.legend(emos)
    plt.show()

def get_distance(coord1, coord2):
    '''用haversine公式计算球面两点间的距离'''
    def hav(theta):
        s = sin(theta / 2)
        return s * s

    lat1 = radians(coord1[0])
    lng1 = radians(coord1[1])
    lat2 = radians(coord2[0])
    lng2 = radians(coord2[1])
    dlng = fabs(lng1 - lng2)
    dlat = fabs(lat1 - lat2)
    h = hav(dlat) + cos(lat1) * cos(lat2) * hav(dlng)
    distance = 2 * EARTH_RADIUS * asin(sqrt(h))
    return distance

def paint_loc(word,data,city,*emos):
    '''输入城市以及情绪得到情绪变化-半径折线图'''
    pass
    plt.figure(num=2)
    center = city_coord[city]
    dist_emo_list = []
    ind=0
    for item in data['location']:
        if (abs(item[0] - center[0]) < 2) and (abs(item[1] - center[1]) < 2):
            dist_emos = [get_distance(center, item),]
            for emo in emos:
                dist_emos.append(create_emo_vec(word[ind],anger,disgust,fear,joy,sadness)()[emo_index[emo]])
            dist_emo_list.append(dist_emos)
        ind+=1
    dist_emo_list = sorted(dist_emo_list, key = (lambda x:x[0]))    # 按与中心的距离排序
    
    count = 0
    emo = [0,] * len(emos)
    x = list(np.arange(0, 10, 0.1))
    ys = []
    for i in x:
        while dist_emo_list[count][0] < i:
            for j in range(len(emos)):
                emo[j] += dist_emo_list[count][j + 1]
            count += 1
        if count != 0: ys.append([e / count for e in emo])
        else: ys.append([e / 1.0 for e in emo])
    for i in range(len(emos)):
        y = [x[i] for x in ys]
        plt.plot(x, y, emo_color[emos[i]])
    
    plt.legend(emos)
    plt.show()

def main():
    data=txt_dispart('E:/code-Python/week3/test.txt')
    txt_add(anger,disgust,fear,joy,sadness)
    word=data_wash(data['word'],txt_read('E:/code-Python/week2/stopwords_list.txt'))
    paint_time(word,data,'week','joy','disgust')
    '''paint_time(word,data,'day','sadness','fear')'''
    paint_loc(word,data,'beijing','joy','sadness')

main()