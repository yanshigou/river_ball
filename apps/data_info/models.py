# -*- coding: utf-8 -*-
from django.db import models
from devices.models import DevicesInfo


class DevicesOneNetInfo(models.Model):
    dev_id = models.CharField(max_length=30, verbose_name='OneNetID')
    imei = models.ForeignKey(DevicesInfo, verbose_name='IMEI')


# 原始数据
class LocationInfo(models.Model):
    imei = models.ForeignKey(DevicesInfo, verbose_name='设备号')
    time = models.DateTimeField(verbose_name='采集时间')
    up_time = models.DateTimeField(verbose_name='上传时间')
    get_time = models.DateTimeField(verbose_name='收到时间', auto_now_add=True)
    longitude = models.CharField(max_length=30, verbose_name='经度')
    latitude = models.CharField(max_length=30, verbose_name='纬度')
    altitude = models.CharField(max_length=10, verbose_name='海拔米', null=True, blank=True)
    speed = models.CharField(max_length=10, verbose_name='速度公里/小时')
    direction = models.CharField(max_length=10, verbose_name='方向', null=True, blank=True)
    accuracy = models.CharField(max_length=10, verbose_name='测量精度', null=True, blank=True)
    power = models.CharField(max_length=10, verbose_name='剩余电量', null=True, blank=True)
    satellites = models.CharField(max_length=10, verbose_name='搜星数量', null=True, blank=True)
    real_satellites = models.CharField(max_length=10, verbose_name='实际使用卫星数量', null=True, blank=True)
    EW_hemisphere = models.CharField(max_length=2, verbose_name='东西半球', null=True, blank=True)
    NS_hemisphere = models.CharField(max_length=2, verbose_name='南北半球', null=True, blank=True)

    class Meta:
        verbose_name = "原始数据信息表"
        verbose_name_plural = verbose_name
        unique_together = ('time', 'longitude', 'latitude')



class TXT(models.Model):
    info = models.CharField(max_length=30, verbose_name='备注', default='')
    filename = models.FileField(upload_to='txt', verbose_name='文件名')
    starttime = models.DateTimeField(null=True, blank=True, verbose_name='上传时间')
