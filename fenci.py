#utf-8

import math
import csv
import jieba
import random
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def danmukureade(path):
    '''文件读取并转换为列表'''
    pass
    word=[]
    print("文件读入开始",end='')
    with open(path,mode ='r',newline = '',encoding='utf-8') as file:
        numfile=csv.reader(file)
        l=list(numfile)
        for item in l:
            word.append(item[0])
        print("---------->完成")
        del word[0]
        return word

def fenci(word,path):
    '''读入停用词并分词'''
    pass
    print("读入停用词文件",end='')
    with open(path,mode = 'r',encoding='utf-8') as file:
        stopwords=[s.rstrip() for s in file.readlines()]
        '''print(stopwords)'''
        stopwords.append(" ")
        print("---------->完成\n分词开始")
        fenci=[]
        after=[]
        fenci_list=[]
        for item in word:
            fenci.append(jieba.lcut(item))
        print("去除停用词开始",end='')
        for item in fenci:
            l=[]
            for w in item:
                if w not in stopwords:
                    after.append(w)
                    l.append(w)
            fenci_list.append(l)
        #print(after)
        print("---------->完成")
        return fenci_list,after

def statistic(word):
    '''统计排序得到高频词与低频词'''
    pass
    dict={}
    #统计
    print("词频统计开始",end='')
    for item in word:
        dict[item]=dict.get(item,0)+1
    print("---------->完成\n排序开始",end='')
    #排序
    sortword=sorted(dict.items(),key = lambda x: x[1],reverse=True)
    print("---------->完成")
    print("max")
    print(sortword[:50])
    print("min")
    print(sortword[-10:])
    return sortword

def special_build(sordword):
    '''建立特征集'''
    pass
    print('建立特征集开始',end='')
    special=[]
    for item in sordword:
        if item[1]<20000:
            break
        special.append(item[0])
    print('---------->完成')
    print(special)
    num=len(special)
    return special,num

def vector_build(fenci_list,special,snum):
    '''建立向量集'''
    pass
    print('建立向量集',end='')
    vector=[]
    fenci_num=len(fenci_list)
    for i in range(fenci_num):
        v=[]
        for j in range(snum):
            v.append(0)
        vector.append(v)
    for i in range(snum):
        for j in range(fenci_num):
            for item in fenci_list[j]:
                if item == special[i]:
                    vector[j][i]+=1
    #print(vector)
    print('---------->完成')
    return vector

def distance(v1,v2,num):
    '''用欧氏距离计算两向量之间的距离'''
    pass
    d=0
    for i in range(num):
        d+=((v1[i]-v2[i])**2)
    return math.sqrt(d)

def sum_word(v1):
    '''计算弹幕长度'''
    pass
    num=len(v1)
    sum=0
    for i in range(num):
        sum+=v1[i]
    return sum

def similar_compare(word,snum,fenci_num,vector):
    '''随机取一条弹幕得到距离最短的三条弹幕以及最远的三条弹幕'''
    pass
    print('随机抽取弹幕开始',end='')
    random_num=-1
    dis=[]
    while random_num==-1:
        a=random.randint(0,fenci_num-1)
        if sum_word(vector[a]) >5:
            random_num=a
    print('---------->完成\n','计算所抽取弹幕对应向量的欧氏距离开始',end='')
    for i in range(len(vector)):
        if word[i]!=word[random_num]:
            d=distance(vector[random_num],vector[i],snum)
            dis.append([random_num,i,d])
    new_dis=sorted(dis,key=lambda dis:dis[2])#sort by d
    print('---------->完成')
    print('距离最近的弹幕:\n')
    print('弹幕:\n',word[new_dis[0][0]],'and',word[new_dis[0][1]])
    print('对应向量:\n',vector[new_dis[0][0]],'and',vector[new_dis[0][1]])
    print('***')
    print('距离最远的弹幕:\n')
    print('弹幕:\n',word[new_dis[-1][0]],'and',word[new_dis[-1][1]])
    print('对应向量:\n',vector[new_dis[-1][0]],'and',vector[new_dis[-1][1]])
    return new_dis

def word_cloud(sortword):
    '''对统计词频得到的前50可视化'''
    pass
    dic={}
    sum=0
    for item in sortword:
        if sum>50:
            break
        dic[item[0]]=item[1]
        sum+=1
    wcd=WordCloud('C:/Windows/Fonts/simkai.ttf')
    wcd.generate_from_frequencies(dic)
    plt.imshow(wcd)
    plt.axis('off')
    plt.show()
  
def main():
    '''主函数'''
    word=danmukureade('E:/code-Python/week2/danmuku.csv')
    fenci_list,after=fenci(word,'E:/code-Python/week2/stopwords_list.txt')
    sortword=statistic(after)
    special,num=special_build(sortword)
    vector=vector_build(fenci_list,special,num)
    dis=similar_compare(word,num,len(fenci_list),vector)
    word_cloud(sortword)
    return 0

main()