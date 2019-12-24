# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from django.conf.urls import url
from .views import DevicesInfoView, DeviceAddView, DeviceView, DeviceModifyView, DeviceDelView, ShowMapView, \
    AppLastLocation, test11, AppDeviceAddView, AppCompanyView, AppPermissionView, AppDeviceDelView, \
    DeviceActiveView, AppDeviceActiveView, DeviceInfoApiView, AllDeviceInfoApi, QueryFreqApiView, ShowMap2View, \
    DevicesRegisterInfoView, DevicesRegisterExcelView

urlpatterns = [
    url(r'^info/$', DevicesInfoView.as_view(), name='devices_info'),
    url(r'^allDevices/$', DevicesRegisterInfoView.as_view(), name='all_devices'),
    url(r'^deviceModify/(?P<device_id>\d+)/$', DeviceModifyView.as_view(), name='device_modify'),
    url(r'^deviceView/(?P<device_id>\d+)/$', DeviceView.as_view(), name='device_view'),
    url(r'^deviceAdd/$', DeviceAddView.as_view(), name='device_add'),
    url(r'^deviceRegisterExcel/$', DevicesRegisterExcelView.as_view(), name='device_add_excel'),
    url(r'^appCompany/$', AppCompanyView.as_view()),
    url(r'^appPermission/$', AppPermissionView.as_view()),
    url(r'^appDeviceAdd/$', AppDeviceAddView.as_view()),
    url(r'^appDeviceDel/$', AppDeviceDelView.as_view()),
    # url(r'^deviceAddExcel/$', DeviceAddExcelView.as_view(), name='device_add_excel'),
    url(r'^deviceDel/$', DeviceDelView.as_view(), name='device_del'),
    url(r'^map/$', ShowMap2View.as_view(), name='show_map'),
    url(r'^map222/$', test11.as_view(), name='show_map222'),

    url(r'^deviceActive/$', DeviceActiveView.as_view(), name='device_active'),
    url(r'^appDeviceActive/$', AppDeviceActiveView.as_view()),

    url(r'^deviceInfoApi/$', DeviceInfoApiView.as_view()),
    url(r'^allDeviceInfoApi/$', AllDeviceInfoApi.as_view()),
    url(r'^lastLocationApi/$', AppLastLocation.as_view()),

    url(r'^queryFreq/$', QueryFreqApiView.as_view()),
]
