from django.db import models
from devices.models import DevicesInfo


# 原始数据
class LocationInfo(models.Model):
    imei = models.ForeignKey(DevicesInfo, verbose_name='设备号')
    time = models.DateTimeField(verbose_name='采集时间')
    up_time = models.DateTimeField(verbose_name='上传时间')
    get_time = models.DateTimeField(verbose_name='收到时间')
    longitude = models.CharField(max_length=10, verbose_name='经度')
    latitude = models.CharField(max_length=10, verbose_name='纬度')
    altitude = models.CharField(max_length=10, verbose_name='海拔米')
    speed = models.CharField(max_length=10, verbose_name='速度公里/小时')
    direction = models.CharField(max_length=10, verbose_name='方向')
    accuracy = models.CharField(max_length=10, verbose_name='测量精度')
    power = models.CharField(max_length=10, verbose_name='剩余电量')
    satellites = models.CharField(max_length=10, verbose_name='搜星数量')
    real_satellites = models.CharField(max_length=10, verbose_name='实际使用卫星数量')

    class Meta:
        verbose_name = "原始数据信息表"
        verbose_name_plural = verbose_name
