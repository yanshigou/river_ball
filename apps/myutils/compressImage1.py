# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/8/28"


from PIL import Image

path = 'D:\\traffic\\traffic_mgmt\\apps\\myutils\\1039_20190604_080238_983_50.45.6.119_渝DJD020_0_1039_蓝.jpg'
img_name = path.split('\\')[-1]
name_list = img_name.split('_')
if name_list[-1][0] == '蓝':
    car_type = '02'
elif name_list[-1][0] == '黄':
    car_type = '01'
elif name_list[-1][0] == '绿':
    car_type = '02'
else:
    car_type = '02'
split_name = name_list[1] + name_list[2] + name_list[3] + '_' + name_list[4] + "_" + name_list[5] + '_' + car_type + '_10395.jpg'
name = "D:\\traffic\\traffic_mgmt\\media" + "\\compress\\" + '10395_' + split_name
print(name)
im = Image.open(path)
print(im.format, im.size, im.mode)
# 原取证图 3840 * 2656
size = 1920, 1328
im.thumbnail(size)
rgb_im = im.convert('RGB')
rgb_im.save(name, 'JPEG')
print(im.format, im.size, im.mode)


