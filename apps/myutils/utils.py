# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/5/10"
from users.models import HistoryRecord, Message
import math


# 操作记录
def create_history_record(user, content, r_type=True):
    try:
        HistoryRecord.objects.create(username_id=user, operation_content=content, r_type=r_type)
        return True
    except Exception as e:
        print(e)
        return False


# 消息提醒
def make_message(username, content, m_type):
    Message.objects.create(username_id=username, content=content, m_type=m_type)
    return True


# 坐标转换

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]
