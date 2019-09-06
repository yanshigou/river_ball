from django.shortcuts import render
from django.views import View
from myutils.mixin_utils import LoginRequiredMixin
from myutils.utils import create_history_record, gps_conversion
from .models import DevicesInfo
from data_info.models import LocationInfo
from .forms import DevicesInfoForm
from django.http import JsonResponse
from river_ball.settings import MEDIA_ROOT


class DevicesInfoView(LoginRequiredMixin, View):

    def get(self, request):
        all_devices = DevicesInfo.objects.all()
        create_history_record(request.user, '查询所有设备')
        return render(request, 'devices.html', {
            "all_devices": all_devices,
        })


class DeviceAddView(LoginRequiredMixin, View):
    """
    新增设备
    """

    def get(self, request):
        return render(request, 'device_form_add.html', {})

    def post(self, request):
        print(request.POST)
        device_form = DevicesInfoForm(request.POST)
        if device_form.is_valid():
            device_form.save()
            create_history_record(request.user, '新增设备 %s' % request.POST.get('imei'))
            return JsonResponse({"status": "success"})

        return JsonResponse({
            "status": "fail",
            "errors": "设备IMEI号唯一且必填"
        })


class DeviceView(LoginRequiredMixin, View):
    """
    查看设备详情
    """

    def get(self, request, device_id):
        device_info = DevicesInfo.objects.get(id=device_id)
        return render(request, "device_view.html", {
            "device_info": device_info
        })


class DeviceModifyView(LoginRequiredMixin, View):
    """
    修改设备信息
    """

    def get(self, request, device_id):
        device_info = DevicesInfo.objects.filter(id=device_id)[0]
        return render(request, "device_form_modify.html", {
            "device_info": device_info,
        })

    def post(self, request, device_id):
        deviceinfo = DevicesInfo.objects.get(id=device_id)
        device_form = DevicesInfoForm(request.POST, instance=deviceinfo)
        if device_form.is_valid():
            device_form.save()
            create_history_record(request.user, '修改设备 %s 的信息' % deviceinfo.imei)
            return JsonResponse({"status": "success"})
        print(device_form.errors)
        if 'area' in device_form.errors:
            return JsonResponse({
                "status": "fail",
                "msg": "请重新选择片区！"
            })
        return JsonResponse({
            "status": "fail"
        })


class DeviceDelView(LoginRequiredMixin, View):
    """
    删除设备
    """

    def post(self, request):
        device_id = request.POST.get('device_id', "")
        print(device_id)
        device = DevicesInfo.objects.filter(id=device_id)
        infos = LocationInfo.objects.filter(imei_id=device_id)
        print(infos)
        if infos:
            return JsonResponse({"status": "fail", "msg": "该设备下有数据，禁止删除。"})
        device_imei = device[0].imei
        device.delete()
        create_history_record(request.user, '删除设备 %s' % device_imei)
        return JsonResponse({"status": "success"})


class ShowMapView(View):
    def get(self, request):
        file = MEDIA_ROOT + '\\all_devices_info.txt'
        all_devices = DevicesInfo.objects.all()
        print(all_devices)
        f = open(file, 'w+', encoding='utf-8')
        for device in all_devices:
            imei = device.imei
            location = LocationInfo.objects.filter(imei__imei=imei).order_by('-time')
            if location:
                location = location[0]
            else:
                continue
            longitude = location.longitude
            latitude = location.latitude
            imei = location.imei.imei
            imei_id = str(location.imei.id)
            # # 百度坐标转换为高德坐标
            # if longitude and latitude:
            #     if len(latitude) > 4 and len(longitude) > 3:
            #         lon, lat = bd09_to_gcj02(float(longitude), float(latitude))
            #         a = str(lon) + ',' + str(lat) + ',' + imei + ',' + imei_id + '\n'
            #         f.write(a)
            longitude, latitude = gps_conversion(longitude, latitude)
            a = str(longitude) + ',' + str(latitude) + ',' + imei + ',' + imei_id + '\n'
            f.write(a)
        f.close()
        return render(request, "map.html", {})
