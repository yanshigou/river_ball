# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views import View
from myutils.mixin_utils import LoginRequiredMixin
from myutils.utils import create_history_record, gps_conversion, one_net_register
from .models import DevicesInfo, CompanyModel
from data_info.models import LocationInfo, DevicesOneNetInfo
from .forms import DevicesInfoForm
from django.http import JsonResponse
from river_ball.settings import MEDIA_ROOT
from datetime import datetime, timedelta
from data_info.views import HttpResponseRedirect, reverse


class DevicesInfoView(LoginRequiredMixin, View):

    def get(self, request):
        # all_devices = DevicesInfo.objects.all()
        permission = request.user.permission
        print(permission)
        if permission == 'superadmin':
            all_devices = DevicesOneNetInfo.objects.all()
        else:
            try:
                company = request.user.company.company_name
                # print(company)
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('devices_info'))
            if company:
                all_devices = DevicesOneNetInfo.objects.filter(imei__company__company_name=company)
            else:
                all_devices = ""
        create_history_record(request.user, '查询所有设备')
        return render(request, 'devices.html', {
            "all_devices": all_devices,
        })


class DeviceAddView(LoginRequiredMixin, View):
    """
    新增设备
    """

    def get(self, request):
        permission = request.user.permission
        print(permission)
        if permission == 'superadmin':
            company_id = CompanyModel.objects.all()
            return render(request, 'device_form_add.html', {"company_id": company_id})
        else:
            try:
                company_id = request.user.company.id
            except Exception as e:
                print(e)
                return render(request, 'devices.html', {
                    "all_devices": "",
                })
        return render(request, 'device_form_add.html', {"company_id": company_id})

    def post(self, request):
        # print(request.POST)
        device_form = DevicesInfoForm(request.POST)
        if device_form.is_valid():
            device_form.save()
            imei, dev_id = one_net_register(request.POST.get('imei'))
            imei_id = DevicesInfo.objects.get(imei=imei).id
            if imei and dev_id:
                DevicesOneNetInfo.objects.create(imei_id=imei_id, dev_id=dev_id)
                create_history_record(request.user, '新增设备 %s, OneNet ID %s' % (request.POST.get('imei'), dev_id))
                return JsonResponse({"status": "success"})
            return JsonResponse({"status": "fail", "errors": "OneNet注册出错, 请删除设备重新注册"})
        print(device_form.errors)
        return JsonResponse({
            "status": "fail",
            "errors": "设备IMEI号和描述唯一且必填"
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
        # print(device_form.errors)
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
        # print(device_id)
        device = DevicesInfo.objects.filter(id=device_id)
        infos = LocationInfo.objects.filter(imei_id=device_id)
        # print(infos)
        if infos:
            return JsonResponse({"status": "fail", "msg": "该设备下有数据，禁止删除。"})
        device_imei = device[0].imei
        device.delete()
        create_history_record(request.user, '删除设备 %s' % device_imei)
        return JsonResponse({"status": "success"})


class ShowMapView(View):
    def get(self, request):
        file = MEDIA_ROOT + '/all_devices_info.txt'
        permission = request.user.permission
        print(permission)
        if permission == 'superadmin':
            all_devices = DevicesInfo.objects.all()
        else:
            try:
                company = request.user.company.company_name
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('devices_info'))
            if company:
                all_devices = DevicesInfo.objects.filter(company__company_name=company)
            else:
                all_devices = []
        # all_devices = DevicesInfo.objects.all()
        # print(all_devices)
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
            speed = location.speed
            time = location.time
            if time:
                now_time = datetime.now()
                if now_time + timedelta(minutes=-1) > (time + timedelta(hours=8)):
                    status = "离线"
                else:
                    status = "在线"
            else:
                status = "离线"
            if longitude and latitude and speed:
                speed = float('%0.2f' % (float(speed) * 0.5144444))
                # print(speed)
                longitude, latitude = gps_conversion(longitude, latitude)
                a = str(longitude) + ',' + str(latitude) + ',' + imei + ',' + str(speed) + "," + status + '\n'
                f.write(a)
        f.close()
        return render(request, "map.html")

    def post(self, request):
        # file = MEDIA_ROOT + '/all_devices_info.txt'
        permission = request.user.permission
        print(permission)
        if permission == 'superadmin':
            all_devices = DevicesInfo.objects.all()
        else:
            try:
                company = request.user.company.company_name
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('devices_info'))
            if company:
                all_devices = DevicesInfo.objects.filter(company__company_name=company)
            else:
                all_devices = []
        # all_devices = DevicesInfo.objects.all()
        # print(all_devices)
        # f = open(file, 'w+', encoding='utf-8')
        a = ""
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
            speed = location.speed
            time = location.time
            if time:
                now_time = datetime.now()
                if now_time + timedelta(minutes=-1) > (time + timedelta(hours=8)):
                    status = "离线"
                else:
                    status = "在线"
            else:
                status = "离线"
            if longitude and latitude and speed:
                speed = float('%0.2f' % (float(speed) * 0.5144444))
                # print(speed)
                longitude, latitude = gps_conversion(longitude, latitude)
                a += str(longitude) + ',' + str(latitude) + ',' + imei + ',' + str(speed) + "," + status + '\n'
                # f.write(a)
        # f.close()
        return JsonResponse({"status": "success", "str_data": a})


class test11(LoginRequiredMixin, View):
    def get(self, request):
        all_devices = DevicesInfo.objects.all()
        data = []
        for device in all_devices:
            imei = device.imei
            location = LocationInfo.objects.filter(imei__imei=imei).order_by('-time')
            if location:
                location_values = location.values()[0]
            else:
                continue
            if location_values['time']:
                now_time = datetime.now()
                if now_time + timedelta(minutes=-1) > (location_values['time'] + timedelta(hours=8)):
                    status = "离线"
                else:
                    status = "在线"
                location_values['time'] = datetime.strftime(location_values['time'] + timedelta(hours=8), "%Y-%m-%d %H:%M:%S")
            else:
                status = "离线"
            if location_values['longitude'] and location_values['latitude'] and location_values['speed']:
                location_values['speed'] = float('%0.2f' % (float(location_values['speed']) * 0.5144444))
                # print(speed)
                location_values['longitude'], location_values['latitude'] = gps_conversion(location_values['longitude'], location_values['latitude'])
            # print(location_values)
            data.append(location_values)
        # print(data)
        return render(request, '111.html', {"data": data})


class ShowMap2View(View):
    def get(self, request):
        return render(request, "map_show.html", {})


class AppLastLocation(View):
    def post(self, request):
        try:
            imei_list = request.POST.get('imei_list', "")
            imei_list = imei_list.split(',')
            # print(imei_list)
            data_list = list()
            for imei in imei_list:
                location = LocationInfo.objects.filter(imei__imei=imei).order_by('-time')
                if location:
                    location = location[0]
                else:
                    continue
                longitude = location.longitude
                latitude = location.latitude
                imei = location.imei.imei
                desc = location.imei.desc
                speed = location.speed
                time = location.time
                if speed:
                    speed = float('%0.2f' % (float(speed) * 0.5144444))
                if time:
                    now_time = datetime.now()
                    if now_time + timedelta(minutes=-1) > (time + timedelta(hours=8)):
                        status = "offline"
                    else:
                        status = "online"
                    time = datetime.strftime(time + timedelta(hours=8), "%Y-%m-%d %H:%M:%S")
                else:
                    status = "offline"

                if longitude and latitude:
                    longitude, latitude = gps_conversion(longitude, latitude)
                    data = {
                        "longitude": longitude,
                        "latitude": latitude,
                        "imei": imei,
                        "desc": desc,
                        "speed": speed,
                        "time": time,
                        "status": status
                    }
                    data_list.append(data)
            return JsonResponse({
                "error_no": 0,
                "data": data_list
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })
