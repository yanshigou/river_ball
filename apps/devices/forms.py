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
