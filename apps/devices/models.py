# -*- coding: utf-8 -*-
from django.db import models
from users.models import CompanyModel


class DevicesRegister(models.Model):
    device_imei = models.CharField(max_length=20, verbose_name='序列号', unique=True)
    device_code = models.CharField(max_length=20, verbose_name='设备编码', unique=True, null=True, blank=True)
    company = models.ForeignKey(CompanyModel, verbose_name='所属公司', null=True, blank=True)

    class Meta:
        verbose_name = "设备注册表"
        verbose_name_plural = verbose_name


class DeviceExcelInfo(models.Model):
    excelInfo = models.CharField(max_length=30, verbose_name='文件备注')
    excelFile = models.FileField(upload_to='device_excel/%Y/%m', verbose_name='Excel文件名')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')


class DevicesInfo(models.Model):
    imei = models.CharField(max_length=20, verbose_name='设备号', unique=True)
    desc = models.CharField(max_length=100, verbose_name='昵称', unique=True)
    company = models.ForeignKey(CompanyModel, verbose_name='所属公司')
    time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    freq = models.CharField(max_length=3, default=5, verbose_name="上传频率/s")

    class Meta:
        unique_together = ('imei', 'desc')
        verbose_name = "设备表"
        verbose_name_plural = verbose_name


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
