# -*- coding: utf-8 -*- #不能忘记！
from darknet import load_net, load_meta, detect
import cv2
import time

# 返回整数时间戳
def timestamp():
    return int(time.time()*10000)
def fix(x, y, x_plus_w, y_plus_h ):
    x = 0 if x < 0 else x
    y = 0 if y < 0 else y
    x_plus_w = 384 if x_plus_w > 384 else x_plus_w
    y_plus_h = 344 if y_plus_h > 344 else y_plus_h
    return x, y, x_plus_w, y_plus_h


# 切割汉字
def seg_one_img(img_path, rets):
    img = cv2.imread(img_path) 
    hanzi_list = []
    for ret in rets:
        per_dict = {}
        if ret[1] > 0.5:
            coordinate = ret[2]
            center = (int(coordinate[0]*344), int(coordinate[1]*384))
            origin = (coordinate[0] - coordinate[2]/2, 
                    coordinate[1] - coordinate[3]/2)

            x = int(origin[0]*344 - 2)
            x_plus_w =int((origin[0] + coordinate[2])*344 + 4)
            y = int(origin[1]*384 - 2)
            y_plus_h = int((origin[1] + coordinate[3])*384 + 4)
            x, y, x_plus_w, y_plus_h = fix(x,y,x_plus_w,y_plus_h)
            try:
                hanzi_img = img[y:y_plus_h, x:x_plus_w]
                normal_img = cv2.resize(hanzi_img, (65,65), 
                        interpolation=cv2.INTER_CUBIC) # 将截取的图片规范化为65*65*3
                path = 'hanzi_img/{}.jpg'.format(timestamp())
                cv2.imwrite(path, normal_img)
                per_dict[path] = center
                hanzi_list.append(per_dict)
            except:
                print('#'*20)
                print('存在不规则的图片')
    return hanzi_list


def load_dtc_module(cfg, weights, data):
    net = load_net(cfg, weights, 0)
    meta = load_meta(data)
    return net,meta 



def seg_all_img(path_file, net, meta):
    # 打开存储图片存储路径的文件，并读取所有行赋值给列表lines
    with open(path_file, 'r') as f:
        lines= f.readlines()
    # 遍历所有图片，进行扣字
    for line in lines:
        img_path = line.strip()  # 从文件读取的路径后面有一个换行符'\n'
        rets = detect(net, meta, img_path) 
        seg_one_img(img_path, rets)


                
if __name__=='__main__':
    # 加载模型
    # net, meta = load_dtc_module("../cfg/yolo-origin.cfg", "../jiyan/backup/yolo-origin.backup" , "../cfg/yolo-origin.data")
    net, meta = load_dtc_module(b"../cfg/yolo-origin.cfg", b"../yolo-origin.weights" ,b"../cfg/yolo-origin.data")

    # 切割所有图片
    seg_all_img('/home/geng/darknet/jiyan/all_images.txt', net, meta)

    # 切割一张图片
    # img_path = '../11.jpg'
    # rets = detect(net,meta,img_path)
    # seg_one_img(img_path, rets)




