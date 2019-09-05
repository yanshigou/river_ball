# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from django.conf.urls import url
from .views import LocationInfoView, SelectDevice, UploadLocationInfoView, StatisticalToOneView, LocationTrackView
from .views import UploadTXT, Uploaded, ShowTXTView, DelFile


urlpatterns = [
    url(r'^selectDevice/$', SelectDevice.as_view(), name='select_device'),
    url(r'^locationInfo/(?P<imei_id>\d+)/$', LocationInfoView.as_view(), name='location_info'),
    url(r'^upload/$', UploadLocationInfoView.as_view()),
    url(r'^statistical/(?P<imei_id>\d+)/$', StatisticalToOneView.as_view(), name='statistical'),
    url(r'^track/(?P<imei_id>\d+)/(?P<start_time>.*)/(?P<end_time>.*)$', LocationTrackView.as_view(), name='track'),
    url(r'^uploadFile/$', UploadTXT.as_view(), name='uploadTXT'),
    url(r'^uploadedFile/$', Uploaded.as_view(), name='uploaded'),
    url(r'^ShowTrack/(?P<file_id>\d+)/$', ShowTXTView.as_view(), name='show_txt'),
    url(r'^delFile/$', DelFile.as_view(), name='delFile'),

]
