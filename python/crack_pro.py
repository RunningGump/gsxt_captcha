# -*- coding: utf-8 -*-
from darknet import load_net, load_meta, detect, classify, load_image
from segment import seg_one_img, load_dtc_module
from recog_order import search_engine_recog, recog_order, recog_order_jieba
import time
import cv2
from PIL import Image
import numpy as np
import copy
import os
from itertools import permutations
from functools import reduce

# 求多个列表的组合
def combination(*lists): 
    total = reduce(lambda x, y: x * y, map(len, lists)) 
    retList = [] 
    for i in range(0, total): 
        step = total 
        tempItem = [] 
        for l in lists: 
            step /= len(l) 
            tempItem.append(l[int(i/step % len(l))]) 
        retList.append(tuple(tempItem)) 
    return retList 

# 加载模块
def load_classify_module(cfg, weights, data):
    net = load_net(cfg, weights, 0)
    meta = load_meta(data)
    return net, meta   

# 使用新字典记录坐标,注意字典是无序的！！
def recordCoordinate(wordList, hanziList):
    center = {}
    for i in range(len(wordList)):
        center[wordList[i]] = [center for center in hanziList[i].values()][0]
    return center

# 破解函数
def crack(img_path, dtc_modu, classify_modu, k):
    # 定位汉字,返回多个矩形框
    print('\n'*2 + '定位汉字' + '\n' + '*'*80)
    d = time.time()
    rets = detect(dtc_modu[0], dtc_modu[1], img_path.encode()) 
    print('定位汉字耗时{}'.format(time.time() - d))
    l = len(rets)
    # 设置阈值
    if l > k:
        return 0


    # 切割图片，返回切割后的汉字图片
    print('\n'*2 + '切割图片' + '\n' + '*'*80)
    s = time.time()
    hanzi_list = seg_one_img(img_path, rets)
    # print(hanzi_list)mmmmmmmmmmmmmm
    print('切割图片耗时{}'.format(time.time() - s))


    # 汉字识别，返回汉字字符串
    print('\n'*2 + '汉字识别' + '\n' + '*'*80)
    r = time.time()
    all_hanzi_lists = [] # 存储所有汉字的列表
    # 提取路径存入列表
    paths = []
    for per in hanzi_list:
        paths.extend([i for i in per.keys()])

    for path in paths: # 对切割的汉字图片进行遍历
        hanzis = []
        img = load_image(path.encode(), 0 , 0)
        res = classify(classify_modu[0], classify_modu[1], img)
        print(res[0:5])
        if res[0][1] < 0.95:
            for hz in res[0:5]: # 对识别的top5进行遍历
                hanzi = ('\\' + hz[0].decode('utf-8')).encode('utf-8').decode('unicode_escape') 
                hanzis.append(hanzi)
        else:
            hanzi = ('\\' + res[0][0].decode('utf-8')).encode('utf-8').decode('unicode_escape')
            hanzis.append(hanzi)

        all_hanzi_lists.append(hanzis)  
    # print(all_hanzi_lists)mmmmmmmmmmmmmmmmmmmmmmmmmm
    hanzi_combination =  combination(*all_hanzi_lists)
    # print(hanzi_combination)
    hanzi_combination_connect = []
    for words in hanzi_combination:
        hanzi_combination_connect.append(''.join(words))
    # print(hanzi_combination_connect)mmmmmmmmmmmmmmmmmmmmm
    print('汉字识别耗时{}'.format(time.time() - r))


    # 识别语序
    hanzi_center = []
    jieba_flag = 0
    o = time.time()
    print('\n'*2 + '语序识别' + '\n' + '*'*80)
    for words in hanzi_combination_connect: # 对每一个组合进行结巴分词
        # 此处对汉字的坐标进行记忆
        hanzi_center = recordCoordinate(words, hanzi_list)

        # print(hanzi_center, 'jiaba')mmmmmmmmmmmmm
        o = time.time()
        rec_word_possible = recog_order_jieba(words)
        if rec_word_possible: # 如果遇到正确的词，则标志位置1
            jieba_flag = 1 
            break
    if jieba_flag:
        rec_word = rec_word_possible
    else:
        hanzi_center = recordCoordinate(hanzi_combination_connect[0], hanzi_list)
        # print(hanzi_center, 'engine')mmmmmmmmmmmmmmm
        rec_word = search_engine_recog(hanzi_combination_connect[0])
    print('语序识别结果:{}'.format(rec_word))
    print('语序识别耗时{}'.format(time.time() - o))


    # 按正确语序输出坐标
    print('\n'*2 + '最终结果' + '\n' + '*'*80)
    centers = []
    for i in rec_word:
        centers.append(hanzi_center[i])
    print('正确语序的坐标：{}'.format(centers))
    print('总耗时{}'.format(time.time() - d))
    ##  调用时需要返回坐标
    return(rec_word)


if __name__ == '__main__':

    # 加载汉字定位模型
    print('\n'*2 + '加载模型' + '\n' + '*'*80)
    dtc_modu = load_dtc_module(b'../cfg/yolo-origin.cfg',
                                b'../jiyan/backup/yolo-origin.weights', b'../cfg/yolo-origin.data') 
    # 加载汉字识别模型
    classify_modu = load_classify_module(b"../cfg/chinese_character.cfg", 
                        b"../chinese_classify/backup/chinese_character.backup", b"../cfg/chinese.data")
    # crack('crack.jpg', dtc_modu, classify_modu,5)

    cwd = os.getcwd()
    IMG_DIR = cwd.replace("python", "python/valid/")
    with open('valid.txt')as f:
        lines = f.readlines()
    right = 0
    num = len(lines)
    for line in lines:
        line = line.strip()
        rec_word = crack(IMG_DIR + line[:24], dtc_modu, classify_modu, 5)
        if rec_word == line[26:]:
            right = right + 1
        elif rec_word == 0:
            num = num - 1
        else:
            print('#'*20 + line[26:]+' ' + rec_word)
    print('正确率={}'.format(right/num))



