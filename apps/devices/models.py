# -*- coding: utf-8 -*-
from django.db import models
from users.models import CompanyModel

# Create your models here.


class DevicesInfo(models.Model):
    imei = models.CharField(max_length=20, verbose_name='设备号', unique=True)
    desc = models.CharField(max_length=100, verbose_name='描述', unique=True)
    company = models.ForeignKey(CompanyModel, verbose_name='所属公司')


class DeviceSettingsInfo(models.Model):
    imei = models.ForeignKey(DevicesInfo, verbose_name='设备号')
    work_mode = models.CharField(max_length=10, default=0, verbose_name='工作模式')
    manual_mode = models.CharField(max_length=10, default=0, verbose_name='手动工作模式')
    led_mode = models.CharField(max_length=10, default=0, verbose_name='LED控制')
    longitude = models.CharField(max_length=10, verbose_name='指定经度')
    latitude = models.CharField(max_length=10, verbose_name='指定纬度')
    speed = models.CharField(max_length=10, verbose_name='指定速度公里/小时')

    class Meta:
        verbose_name = "设备设置信息"
        verbose_name_plural = verbose_name
