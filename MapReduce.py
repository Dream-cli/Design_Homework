import os
import time
import jieba
from multiprocessing import Process, Pipe


def freq_stat(data, stopwords):
    word_list = list(word for word in jieba.lcut(data)
                     if word not in stopwords)
    freq_dict = {}
    for word in word_list:
        freq_dict[word] = freq_dict.get(word, 0) + 1
    return freq_dict


def assign(to_map, file_path):
    for path in os.listdir(file_path):
        to_map.send(file_path + '\\' + path)


def map(from_ass, to_re, stopwords):
    while True:
        try:
            path = from_ass.recv()
            with open(path, mode='r', encoding='utf-8') as infile:
                text = infile.read()
            to_re.send(freq_stat(text, stopwords))
        except EOFError:
            from_ass.close()
            break


def reduce(from_map):
    freq_stat_dic = {}
    count = 1
    while True:
        try:
            dic = from_map.recv()
            print('\rProcessed %d...' % count, end='')
            count += 1
            for key in dic.keys():
                freq_stat_dic[key] = freq_stat_dic.get(key, 0) + 1
        except EOFError:
            from_map.close()
            with open('D:\\data\\map\\frequant_stat.txt',
                      'w',
                      encoding='utf-8') as outfile:
                for key in freq_stat_dic.keys():
                    print(key, ':', freq_stat_dic[key], file=outfile)
            break


if __name__ == '__main__':
    start = time.time()
    NUM_MAP = 75
    stopword_path = 'E:\\code-Python\\week2\\stopwords_list.txt'
    content_path = "D:\\data\\map\\docs"
    with open(stopword_path, mode='r', encoding='utf-8') as file:
        stopwords = [s.rstrip() for s in file.readlines()]
        stopwords.append(" ")

    maps = []
    map_re_recv, map_re_send = Pipe(False)
    ass_map_recv, ass_map_send = Pipe(False)
    for i in range(NUM_MAP):
        maps.append(Process(target=map,
                            args=(ass_map_recv, map_re_send, stopwords)))
    assignment = Process(target=assign, args=(ass_map_send, content_path))
    assignment.start()
    reducer = Process(target=reduce, args=(map_re_recv, ))
    reducer.start()
    for submap in maps:
        submap.start()
    assignment.join()
    ass_map_send.close()
    for submap in maps:
        submap.join()
    map_re_send.close()
    reducer.join()
    print('\nFinished!')

    end = time.time()
    logging = end - start
    with open('D:\\data\\map\\longging_time.txt', mode='a',
              encoding='utf-8') as outfile:
        print(f'num of map_process\t{NUM_MAP}\trun time\t{logging}',
              file=outfile)
