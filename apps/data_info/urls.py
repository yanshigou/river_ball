# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from django.conf.urls import url
from .views import LocationInfoView, SelectDevice, UploadLocationInfoView, StatisticalToOneView, LocationTrackView
from .views import OneNetDataView, AppSelectDevice, AppLocationInfoView, ExportLocationInfoView, \
    Select2Device, AppStartTestRecordView, AppEndTestRecordView, TestRecordDoneView, TestRecordNotDoneView, \
    AppTestRecordSpeedListApiView, AppTestRecordLocationListApiView, RecordLocationInfoView, \
    RecordTrackView, RecordStatisticalView

urlpatterns = [
    url(r'^selectDevice/$', SelectDevice.as_view(), name='select_device'),
    url(r'^select2Device/$', Select2Device.as_view(), name='select2_device'),
    url(r'^appSelectDevice/$', AppSelectDevice.as_view()),
    url(r'^locationInfo/(?P<imei_id>\d+)/$', LocationInfoView.as_view(), name='location_info'),
    url(r'^ExportLocationInfo/$', ExportLocationInfoView.as_view(), name='export_location_info'),
    url(r'^upload/$', UploadLocationInfoView.as_view()),
    url(r'^rawData/$', OneNetDataView.as_view()),
    url(r'^statistical/(?P<imei_id>\d+)/$', StatisticalToOneView.as_view(), name='statistical'),
    url(r'^track/(?P<imei_id>\d+)/(?P<start_time>.*)/(?P<end_time>.*)$', LocationTrackView.as_view(), name='track'),

    url(r'^recordLocationInfo/(?P<record_id>\d+)/$', RecordLocationInfoView.as_view(), name='record_location_info'),
    url(r'^recordTrack/(?P<record_id>\d+)/$', RecordTrackView.as_view(), name='record_track'),
    url(r'^recordStatistical/(?P<record_id>\d+)/$', RecordStatisticalView.as_view(), name='record_statistical'),

    url(r'^appStartTestRecord/$', AppStartTestRecordView.as_view()),
    url(r'^appEndTestRecord/$', AppEndTestRecordView.as_view()),
    url(r'^testRecordDone/$', TestRecordDoneView.as_view()),
    url(r'^testRecordNotDone/$', TestRecordNotDoneView.as_view()),
    url(r'^testRecordSpeedData/$', AppTestRecordSpeedListApiView.as_view()),
    url(r'^testRecordLocationData/$', AppTestRecordLocationListApiView.as_view()),
    url(r'^locationInfo/$', AppLocationInfoView.as_view()),

]
