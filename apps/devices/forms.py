# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from django import forms
from devices.models import DevicesInfo
from rest_framework import serializers


class DevicesInfoForm(forms.ModelForm):
    class Meta:
        model = DevicesInfo
        fields = ["imei", 'desc', 'company', 'freq']


class DevicesInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevicesInfo
        fields = '__all__'


class DeviceActiveForm(forms.ModelForm):
    class Meta:
        model = DevicesInfo
        fields = ["is_active"]


class DeviceExcelForm(forms.Form):
    excelInfo = forms.CharField(label='文件备注', min_length=1)
    excelFile = forms.FileField(label='上传Excel文件')
