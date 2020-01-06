# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2020/1/2"
from math import radians, cos, sin, asin, sqrt


# 公式计算两点间距离（m）


def geodistance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)])  # 经纬度转换成弧度
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    distance = 2 * asin(sqrt(a)) * 6371 * 1000  # 地球平均半径，6371km
    distance = round(distance / 1000, 3)
    return distance * 1000  # 、//公里  米


if __name__ == '__main__':
    distance = geodistance("106.566983", "29.56835", "106.56635", "29.563227")
    print(distance)
    print(type(distance))
