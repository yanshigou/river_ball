# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from .models import LocationInfo
from django import forms
from rest_framework import serializers


class LocationInfoForm(forms.ModelForm):
    class Meta:
        model = LocationInfo
        fields = ["imei", 'time', 'up_time', 'get_time', 'longitude', 'latitude', 'altitude', 'speed', 'direction',
                  'accuracy', 'power', 'satellites', 'real_satellites']


class LocationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationInfo
        fields = '__all__'
