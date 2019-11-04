# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from django.conf.urls import url
from .views import LocationInfoView, SelectDevice, UploadLocationInfoView, StatisticalToOneView, LocationTrackView
from .views import OneNetDataView, AppSelectDevice, AppLocationInfoView, ExportLocationInfoView, \
    Select2Device, AppStartTestRecordView, AppEndTestRecordView, AppTestRecordView, \
    AppTestRecordSpeedListApiView, AppTestRecordLocationListApiView

urlpatterns = [
    url(r'^selectDevice/$', SelectDevice.as_view(), name='select_device'),
    url(r'^select2Device/$', Select2Device.as_view(), name='select2_device'),
    url(r'^appSelectDevice/$', AppSelectDevice.as_view()),
    url(r'^locationInfo/(?P<imei_id>\d+)/$', LocationInfoView.as_view(), name='location_info'),
    url(r'^ExportLocationInfo/$', ExportLocationInfoView.as_view(), name='export_location_info'),
    url(r'^appLocationInfo/$', AppLocationInfoView.as_view()),
    url(r'^upload/$', UploadLocationInfoView.as_view()),
    url(r'^rawData/$', OneNetDataView.as_view()),
    url(r'^statistical/(?P<imei_id>\d+)/$', StatisticalToOneView.as_view(), name='statistical'),
    url(r'^track/(?P<imei_id>\d+)/(?P<start_time>.*)/(?P<end_time>.*)$', LocationTrackView.as_view(), name='track'),
    url(r'^appStartTestRecord/$', AppStartTestRecordView.as_view()),
    url(r'^appEndTestRecord/$', AppEndTestRecordView.as_view()),
    url(r'^appTestRecord/$', AppTestRecordView.as_view()),
    url(r'^appTestRecordSpeedData/$', AppTestRecordSpeedListApiView.as_view()),
    url(r'^appTestRecordLocationData/$', AppTestRecordLocationListApiView.as_view()),
    # url(r'^uploadFile/$', UploadTXT.as_view(), name='uploadTXT'),
    # url(r'^uploadedFile/$', Uploaded.as_view(), name='uploaded'),
    # url(r'^ShowTrack/(?P<file_id>\d+)/$', ShowTXTView.as_view(), name='show_txt'),
    # url(r'^delFile/$', DelFile.as_view(), name='delFile'),

]



