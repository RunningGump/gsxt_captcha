# encoding=utf-8
import jieba
from itertools import permutations
import requests
from lxml import etree
import threading
# jieba.load_userdict('word.txt') #加载自定义词典
import time

flags = []
all_related = []
# 获得汉字所有排列方式
def _permutation(str, r = None): 
    word_list = list(permutations(str, r))
    for i in range(len(word_list)):
        word_list[i] = ''.join(word_list[i])
    return word_list

# 将文件数据转换为字典
def file2dict(filename):
    with open(filename) as f:
        array_lines = f.readlines()
    returnDict = {}
    # 以下三行解析文件数据到列表
    for line in array_lines:
        line = line.strip()
        listFromLine = line.split()
        returnDict[listFromLine[0]] = int(listFromLine[1])
    return returnDict

	
# 对字典根据key排序
def sortedDictValues(di): 
    return [(k,di[k]) for k in sorted(di.keys())]


# 输入词列表，返回结巴分词内词频最高的词
def highest_frequency(possible_words):
    word_dict = file2dict('dict.txt')
    possible_dict = {}
    for possible_word in possible_words:
        possible_dict[word_dict[possible_word]] = possible_word
    sortedList = sortedDictValues(possible_dict)
    return sortedList[-1][1]


# 结巴分词 + 搜索引擎 识别语序
def recog_order(str):
    l = len(str) # l表示词语汉字个数
    word_list = _permutation(str) # 获得排列
    possible_words = []
    for word in word_list:
        seg_list = jieba.lcut(word, cut_all=True ) # 全模式
        index = find_longest(seg_list) 
        if len(seg_list[index]) == l:
            possible_words.append(seg_list[index])
    if len(possible_words) ==1:
        return possible_words[0]
    elif len(possible_words) >1:
        return highest_frequency(possible_words)
    else:
        return search_engine_recog(str)


# 结巴分词 识别语序
def recog_order_jieba(str):
    l = len(str) # l表示词语汉字个数
    word_list = _permutation(str) # 获得排列
    # print(word_list)
    possible_words = []
    for word in word_list:
        seg_list = jieba.lcut(word, cut_all=True ) # 全模式
        # print(seg_list)
        index = find_longest(seg_list) 
        # print(index)
        if len(seg_list[index]) == l:
            possible_words.append(seg_list[index])
    # print(possible_words)
    if len(possible_words) ==1:
        return possible_words[0]
    elif len(possible_words) >1:
        return highest_frequency(possible_words)
    else:
        return 0


# 寻找列表中最长的词
def find_longest(list):
    l = 0
    index = 0
    for i,word in enumerate(list):
        if len(word) > l:
            l = len(word)
            index = i 
    return index


# 搜索引擎搜索关键字,返回相关列表
def search_engine(word):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
    }
    r = requests.get('https://www.baidu.com/s?wd=' + word, headers=headers)
    html = etree.HTML(r.text)

    related_words1 = html.xpath('//*[@id="rs"]/table//tr//th/a/text()')

    related_words2 = html.xpath('//div[@id="content_left"]//a//em/text()')

    related_words = related_words1 + related_words2
    # print(related_words)
    return related_words


# 调用一次线程
def search(word):
    related_words = search_engine(word)
    global all_related
    all_related = all_related + related_words


# 通过搜索引擎识别语序
def search_engine_recog(str):
    word_list = _permutation(str) # 获得排列
    # print(word_list)
    global flags 
    flags = [0] * len(word_list)
    threads = []

    for word in word_list: # 遍历所有可能的排列组合
        thread = threading.Thread(target=search, args=[word])
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    global all_related
    # print(all_related)
    for i,word in enumerate(word_list):
        flag = 0
        for related_word in all_related: 
            if word in related_word:
                    flag = flag + 1
        flags[i] = flag
    # print(flags)
    all_related = []
    # sorted_flags = sorted(flags, reverse=True)
    index = flags.index(max(flags))
    # print (sorted_flags)
    return word_list[index]

def reverse(str):
    return str[::-1]



if __name__ == '__main__':
    word = '现无中意发'
    # reversed_word = reverse(word)
    print('开始识别语序了')
    # print(search_engine_recog(word))
    start = time.time()
    rec_word = search_engine_recog(word)
    print(rec_word, time.time() - start)
    # search_engine(word)



# # # 结巴分词识别语序
# # def recog_order(str):
# #     l = len(str) # l表示词语汉字个数
# #     word_list = _permutation(str) # 获得排列
# #     for word in word_list:
# #         # print('#'*50)
# #         seg_list = jieba.lcut(word, cut_all=True ) # 全模式
# #         index = find_longest(seg_list) 
# #         if len(seg_list[index]) == l:
# #             return seg_list[index]
# #     return str


# # # 寻找列表中最长的词
# # def find_longest(list):
# #     l = 0
# #     index = 0
# #     for i,word in enumerate(list):
# #         if len(word) > l:
# #             l = len(word)
# #             index = i 
# #     return index








