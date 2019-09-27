# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/4"
from django.conf.urls import url
from .views import DevicesInfoView, DeviceAddView, DeviceView, DeviceModifyView, DeviceDelView, ShowMapView, \
    ShowMap2View, AppLastLocation, test11


urlpatterns = [
    url(r'^info/$', DevicesInfoView.as_view(), name='devices_info'),
    url(r'^deviceModify/(?P<device_id>\d+)/$', DeviceModifyView.as_view(), name='device_modify'),
    url(r'^deviceView/(?P<device_id>\d+)/$', DeviceView.as_view(), name='device_view'),
    url(r'^deviceAdd/$', DeviceAddView.as_view(), name='device_add'),
    # url(r'^deviceAddExcel/$', DeviceAddExcelView.as_view(), name='device_add_excel'),
    url(r'^deviceDel/$', DeviceDelView.as_view(), name='device_del'),
    url(r'^map/$', ShowMapView.as_view(), name='show_map'),
    url(r'^map222/$', test11.as_view(), name='show_map222'),
    url(r'^appLastLocation/$', AppLastLocation.as_view()),
    # url(r'^map2/$', ShowMap2View.as_view(), name='show_map2'),
    # url(r'^mapOne/(?P<device_id>\d+)/$', ShowOneToMapView.as_view(), name='show_one_to_map'),
    # url(r'^map2/$', ShowMapView2.as_view(), name='show_map2'),
    # url(r'^point/$', point.as_view(), name='point'),
    #
    # url(r'^test/$', SelectTestView.as_view(), name='test'),
    # url(r'^test2/$', SelectTest2View.as_view(), name='test2'),
    #
    # url(r'^allDevices/$', AllDevicesView.as_view(), name='all_devices'),
    # url(r'^statusModify/$', DeviceStatusModifyView.as_view(), name='status_Modify'),
    # url(r'^deviceOfflineExport/$', DeviceOfflineView.as_view(), name='device_offline_export'),
    # url(r'^deviceInfoExport/$', DeviceInfoExportView.as_view(), name='device_info_export'),
    # url(r'^ledInfoExport/$', LEDInfoExportView.as_view(), name='led_info_export'),
]