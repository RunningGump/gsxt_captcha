import xml.etree.ElementTree as ET
import pickle
import os
from os import listdir, getcwd
from os.path import join

classes = ["hanzi"]

cwd = os.getcwd() # 返回当前的目录
IMG_DIR = cwd.replace("tools", "jiyan/valid") 

def convert(size, box):
    dw = 1./(size[0])
    dh = 1./(size[1])
    x = (box[0] + box[1])/2.0 - 1
    y = (box[2] + box[3])/2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

# 将.xml转化为.txt格式
def convert_annotation(src):
    in_file = open("%s/%s" %(IMG_DIR, src))
    dst = "%s/%s" %(IMG_DIR, src.replace("xml", "txt"))
    out_file = open(dst, 'w')
    tree=ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')

wd = getcwd()


# 若是.jpeg则保存图片路径;若是.xml则将其转换.txt
def run():
    list_file = open("valid.txt", "w") #train.txt用来保存图片的路径
    files = os.listdir(IMG_DIR) # 返回指定的文件夹包含的文件或文件夹的名字的列表
    for f in files:
        if f.endswith(".jpg"):
            list_file.write('%s/%s\n' %(IMG_DIR, f))
        if f.endswith(".xml"):
            convert_annotation(f)
    list_file.close()

if __name__ == '__main__':
    run()
