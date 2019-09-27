# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from django import forms
from devices.models import DevicesInfo


class DevicesInfoForm(forms.ModelForm):
    class Meta:
        model = DevicesInfo
        fields = ["imei", 'desc', 'company']
