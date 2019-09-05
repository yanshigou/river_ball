# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from django.conf.urls import url
from .views import LocationInfoView, SelectDevice, UploadLocationInfoView, StatisticalToOneView


urlpatterns = [
    url(r'^selectDevice/$', SelectDevice.as_view(), name='select_device'),
    url(r'^locationInfo/(?P<imei_id>\d+)/$', LocationInfoView.as_view(), name='location_info'),
    url(r'^upload/$', UploadLocationInfoView.as_view()),
    url(r'^statistical/(?P<imei_id>\d+)/$', StatisticalToOneView.as_view(), name='statistical'),

]
