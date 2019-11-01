import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json
plt.ion()
pic_list = os.listdir('./old_img')
for pic in pic_list:
    img = mpimg.imread('/home/geng/darknet/chinese_classify/old_img/' + pic)
    plt.imshow(img)
    character = input('输入正确的汉字：')
    plt.close()
    unicod = json.dumps(character)
    print(unicod)
    os.rename('./old_img/' + pic, 
            './new_img/' + pic[0:15] + unicod[2:7] + '.jpg')




