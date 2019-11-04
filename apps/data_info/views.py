# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views import View
from myutils.mixin_utils import LoginRequiredMixin
from datetime import timedelta
from myutils.utils import create_history_record, gps_conversion, export_excel, device_is_active
from .models import LocationInfo, DevicesOneNetInfo, TestRecord
from users.models import UserProfile
from devices.models import DevicesInfo
from django.http import JsonResponse, HttpResponseRedirect
from .forms import LocationInfoSerializer, DevicesInfoSerializer
from rest_framework.views import APIView
from django.core.urlresolvers import reverse
import re
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection


class SelectDevice(LoginRequiredMixin, View):
    def get(self, request):
        permission = request.user.permission
        print(permission)
        if permission == 'superadmin':
            all_devices = DevicesInfo.objects.all()
        else:
            try:
                company = request.user.company.company_name
                # print(company)
            except Exception as e:
                print(e)
                return render(request, 'select_device.html', {
                    "all_devices": "",
                })
            if company:
                all_devices = DevicesInfo.objects.filter(company__company_name=company)
            else:
                all_devices = ""
        return render(request, 'select_device.html', {
            "all_devices": all_devices
        })


class Select2Device(LoginRequiredMixin, View):
    def get(self, request):
        permission = request.user.permission
        print(permission)
        now_time = datetime.now().replace(microsecond=0)
        start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        if permission == 'superadmin':
            all_test_record = TestRecord.objects.all()
        else:
            try:
                company = request.user.company.company_name
                # print(company)
            except Exception as e:
                print(e)
                return render(request, 'select2_device.html', {
                    "all_devices": "",
                    "start_time": start_time,
                    "end_time": now_time
                })
            if company:
                all_test_record = TestRecord.objects.filter(company__company_name=company)
            else:
                all_test_record = ""
        return render(request, 'select2_device.html', {
            "all_test_record": all_test_record,
            "start_time": start_time,
            "end_time": now_time
        })

    def post(self, request):
        start_time = request.POST.get('start_time', '')
        end_time = request.POST.get('end_time', '')
        record_id = request.POST.getlist('checkbox', '')
        print(start_time)
        print(end_time)
        return JsonResponse({
            "error_no": 0
        })


class AppSelectDevice(View):
    def get(self, request):
        try:
            all_devices = DevicesInfo.objects.all()
            d_sers = DevicesInfoSerializer(all_devices, many=True)
            return JsonResponse({
                "error_no": 0,
                "data": d_sers.data
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class LocationInfoView(LoginRequiredMixin, View):
    def get(self, request, imei_id):

        permission = request.user.permission
        print(permission)
        now_time = datetime.now().replace(microsecond=0)
        start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time = now_time + timedelta(hours=-8)
        if permission != 'superadmin':
            device = DevicesInfo.objects.filter(id=imei_id)
            try:
                company = request.user.company.company_name
                device_company = device[0].company.company_name
                # print(company)
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('devices_info'))
            if company and device and device_company == company:
                location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                             time__lte=end_time).order_by('-time')
                if location_infos:
                    imei = location_infos[0].imei.imei
                    create_history_record(request.user, '查询设备号%s数据' % imei)
                    a = location_infos.values()
                    for i in a:
                        i['imei'] = imei
                        if i['time']:
                            i['time'] = i['time'] + timedelta(hours=8)
                        if i['speed']:
                            i['speed'] = float('%0.2f' % (float(i['speed']) * 0.5144444))
                        if i['longitude'] and i['latitude']:
                            i['longitude'], i['latitude'] = gps_conversion(i['longitude'], i['latitude'])
                        if i['power'] and len(i['power']) > 4:
                            i['power'] = float('%0.2f' % (float(i['power'][3:]) * 0.001))
                    # print(a)
                    return render(request, 'location_infos.html', {
                        "imei_id": imei_id,
                        "imei": imei,
                        "location_data": a,
                        "start_time": start_time,
                        "end_time": now_time
                    })
                return render(request, 'location_infos.html', {
                    "imei_id": imei_id,
                    "imei": "",
                    "location_data": location_infos,
                    "start_time": start_time,
                    "end_time": now_time
                })
            else:
                return HttpResponseRedirect(reverse('devices_info'))
        else:
            location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                         time__lte=end_time).order_by('-time')
            if location_infos:
                imei = location_infos[0].imei.imei
                create_history_record(request.user, '查询设备号%s数据' % imei)
                a = location_infos.values()
                for i in a:
                    i['imei'] = imei
                    if i['time']:
                        i['time'] = i['time'] + timedelta(hours=8)
                    if i['speed']:
                        i['speed'] = float('%0.2f' % (float(i['speed']) * 0.5144444))
                    if i['longitude'] and i['latitude']:
                        i['longitude'], i['latitude'] = gps_conversion(i['longitude'], i['latitude'])
                    if i['power'] and len(i['power']) > 4:
                        i['power'] = float('%0.2f' % (float(i['power'][3:]) * 0.001))
                # print(a)
                return render(request, 'location_infos.html', {
                    "imei_id": imei_id,
                    "imei": imei,
                    "location_data": a,
                    "start_time": start_time,
                    "end_time": now_time
                })
            return render(request, 'location_infos.html', {
                "imei_id": imei_id,
                "imei": "",
                "location_data": location_infos,
                "start_time": start_time,
                "end_time": now_time
            })

    def post(self, request, imei_id):
        start_time = request.POST.get('start_time', '')
        end_time = request.POST.get('end_time', '')
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        permission = request.user.permission
        print(permission)
        if permission != 'superadmin':
            device = DevicesInfo.objects.filter(id=imei_id)
            try:
                company = request.user.company.company_name
                device_company = device[0].company.company_name
                # print(company)
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('devices_info'))
            if company and device and device_company == company:
                location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                             time__lte=end_time2).order_by('-time')
                if location_infos:
                    imei = location_infos[0].imei.imei
                    create_history_record(request.user, '查询设备号%s数据' % location_infos[0].imei.imei)
                    a = location_infos.values()
                    for i in a:
                        i['imei'] = imei
                        if i['time']:
                            i['time'] = i['time'] + timedelta(hours=8)
                        if i['speed']:
                            i['speed'] = float('%0.2f' % (float(i['speed']) * 0.5144444))
                        if i['longitude'] and i['latitude']:
                            i['longitude'], i['latitude'] = gps_conversion(i['longitude'], i['latitude'])
                        if i['power'] and len(i['power']) > 4:
                            i['power'] = float('%0.2f' % (float(i['power'][3:]) * 0.001))
                    # print(a)
                    return render(request, 'location_infos.html', {
                        "imei_id": imei_id,
                        "imei": imei,
                        "location_data": a,
                        "start_time": start_time,
                        "end_time": end_time
                    })
                return render(request, 'location_infos.html', {
                    "imei_id": imei_id,
                    "imei": "",
                    "location_data": location_infos,
                    "start_time": start_time,
                    "end_time": end_time
                })
            else:
                return HttpResponseRedirect(reverse('devices_info'))
        else:
            location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                         time__lte=end_time2).order_by('-time')
            if location_infos:
                imei = location_infos[0].imei.imei
                create_history_record(request.user, '查询设备号%s数据' % location_infos[0].imei.imei)
                a = location_infos.values()
                for i in a:
                    i['imei'] = imei
                    if i['time']:
                        i['time'] = i['time'] + timedelta(hours=8)
                    if i['speed']:
                        i['speed'] = float('%0.2f' % (float(i['speed']) * 0.5144444))
                    if i['longitude'] and i['latitude']:
                        i['longitude'], i['latitude'] = gps_conversion(i['longitude'], i['latitude'])
                    if i['power'] and len(i['power']) > 4:
                        i['power'] = float('%0.2f' % (float(i['power'][3:]) * 0.001))
                # print(a)
                return render(request, 'location_infos.html', {
                    "imei_id": imei_id,
                    "imei": imei,
                    "location_data": a,
                    "start_time": start_time,
                    "end_time": end_time
                })
            return render(request, 'location_infos.html', {
                "imei_id": imei_id,
                "imei": "",
                "location_data": location_infos,
                "start_time": start_time,
                "end_time": end_time
            })


class AppLocationInfoView(View):
    def post(self, request):
        try:
            start_time = request.POST.get('start_time', '')
            end_time = request.POST.get('end_time', '')
            imei_id = request.POST.get('imei_id', '')
            username = request.POST.get('username', '')
            start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                         time__lte=end_time2).order_by('-time')
            page = request.POST.get('page', '1')
            print(page)
            paginator = Paginator(location_infos, 20)
            try:
                location_info_page = paginator.page(page)
            except PageNotAnInteger:
                location_info_page = paginator.page(1)
            except EmptyPage:
                location_info_page = paginator.page(paginator.num_pages)
            if location_info_page:
                imei = location_infos[0].imei.imei
                create_history_record(username, 'app查询设备号%s数据' % imei)
                a = LocationInfoSerializer(location_info_page, many=True).data
                for i in a:
                    i['imei'] = imei
                    if i['time']:
                        i['time'] = datetime.strftime(
                            datetime.strptime(i['time'], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=8), "%Y-%m-%d %H:%M:%S")
                    if i['speed']:
                        i['speed'] = float('%0.2f' % (float(i['speed']) * 0.5144444))
                    if i['longitude'] and i['latitude']:
                        i['longitude'], i['latitude'] = gps_conversion(i['longitude'], i['latitude'])
                    if i['power'] and len(i['power']) > 4:
                        i['power'] = float('%0.2f' % (float(i['power'][3:]) * 0.001))
                data = {
                    "imei_id": imei_id,
                    "imei": imei,
                    "location_data": a,
                    "start_time": start_time,
                    "end_time": end_time,
                    "total": paginator.num_pages
                }
                return JsonResponse({
                    "error_no": 0,
                    "data": data
                })
            data = {
                "imei_id": imei_id,
                "imei": "",
                "location_data": LocationInfoSerializer(location_infos, many=True).data,
                "start_time": start_time,
                "end_time": end_time,
                "total": paginator.num_pages
            }
            return JsonResponse({
                "error_no": 0,
                "data": data
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class ExportLocationInfoView(View):
    def post(self, request):
        try:
            start_time = request.POST.get('start_time', '')
            end_time = request.POST.get('end_time', '')
            imei_id = request.POST.get('imei_id', '')
            # print(start_time)
            # print(end_time)
            # print(imei_id)
            start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            # print(start_time2)
            # print(end_time2)
            location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                         time__lte=end_time2).order_by('-time')
            if location_infos:
                imei = location_infos[0].imei.imei
                create_history_record(request.user, 'app查询设备号%s数据' % location_infos[0].imei.imei)
                a = LocationInfoSerializer(location_infos, many=True).data
                location_datas = list()
                for i in a:
                    i['imei'] = imei
                    if i['time']:
                        i['time'] = datetime.strftime(
                            datetime.strptime(i['time'], "%Y-%m-%dT%H:%M:%S") + timedelta(hours=8), "%Y-%m-%d %H:%M:%S")
                    if i['speed']:
                        i['speed'] = float('%0.2f' % (float(i['speed']) * 0.5144444))
                    if i['longitude'] and i['latitude']:
                        i['longitude'], i['latitude'] = gps_conversion(i['longitude'], i['latitude'])
                    if i['power'] and len(i['power']) > 4:
                        i['power'] = float('%0.2f' % (float(i['power'][3:]) * 0.001))
                    data = [
                        i['imei'], i['time'], i['longitude'], i['latitude'], i['altitude'], i['speed'], i['accuracy'],
                        i['power'], i['satellites'], i['direction']
                    ]

                    location_datas.append(data)
                if location_datas:
                    # print("excel")
                    # print(location_datas)
                    now = datetime.now()
                    name = datetime.strftime(now, '%m-%d-%H-%M-%S')
                    filename = 'media/excel/location_data_' + name + '.xlsx'
                    file = '流速球数据' + name + '.xlsx'
                    export_excel(location_datas, '流速球数据', filename)
                    create_history_record(request.user, '流速球数据导出Excel：%s' % file)
                    return JsonResponse({
                        "status": "success",
                        "media_url": "/" + filename,
                        "file": file
                    })
                return JsonResponse({
                    "status": 'fail'
                })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


# 设备信息上传
class UploadLocationInfoView(APIView):
    def post(self, request):
        try:
            imei = request.data.get('imei')
            imei_id = DevicesInfo.objects.get(imei=imei).id
            request.data['imei'] = imei_id
            # print(request.data)
            location_sers = LocationInfoSerializer(data=request.data)
            if location_sers.is_valid():
                location_sers.save()
                return JsonResponse({"status": "success"})
            # print(location_sers.errors)
            return JsonResponse({"status": "fail", "errors": str(location_sers.errors)})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "error": str(e)})


# OneNet回传信息
class OneNetDataView(APIView):
    def post(self, request):
        try:
            # print("oneNet")
            # print(request.data)
            current_data = request.data.get('current_data')[0]
            dev_id = current_data.get('dev_id')
            one_net = DevicesOneNetInfo.objects.filter(dev_id=dev_id)
            if one_net:
                imei_id = one_net[0].imei.id
                if not device_is_active(imei_id):
                    return JsonResponse({"status": "error", "error": 'device is_active False'})

            else:
                return JsonResponse({"status": "error", "error": 'device not exist'})
            user_id = current_data.get('user_id')
            ds_id = current_data.get('ds_id')
            value = current_data.get('value')
            up_time = current_data.get('at')
            if ds_id == 'liusuqiu':
                re_data_list = re.findall(r"\$GNRMC[^#]*##\$GNGGA[^#]*##[^#]*##", value, re.S)
                # print('re_data_list', re_data_list)
                if re_data_list:
                    for v in re_data_list:
                        data_list = v.split('##')
                        # print('data_list', data_list)
                        direction = ""
                        EW_hemisphere = ""
                        NS_hemisphere = ""
                        satellites = ""
                        accuracy = ""
                        altitude = ""
                        power = ""
                        for d in data_list:
                            d_list = d.split(',')
                            if len(d) > 10 and d_list[0] == '$GNRMC':
                                print('$GNRMC', d_list)
                                time = datetime.strptime((d_list[9] + d_list[1][:6]), '%d%m%y%H%M%S')
                                longitude = d_list[5]
                                latitude = d_list[3]
                                speed = d_list[7]
                                direction = d_list[8]
                                EW_hemisphere = d_list[6]
                                NS_hemisphere = d_list[4]
                            elif len(d) > 10 and d_list[0] == '$GNGGA':
                                print('$GNGGA', d_list)
                                satellites = d_list[7]
                                accuracy = d_list[8]
                                altitude = d_list[9]
                            elif 'VOL' in d_list[0] or 'CHG' in d_list[0] or 'FUL' in d_list[0]:
                                print('power', d_list)
                                power = d_list[0]

                        location_sers = LocationInfoSerializer(data={
                            "imei": imei_id, "time": time, "up_time": up_time, "longitude": longitude,
                            "latitude": latitude,
                            "altitude": altitude, "speed": speed, "direction": direction, "accuracy": accuracy,
                            "satellites": satellites, "real_satellites": satellites, "EW_hemisphere": EW_hemisphere,
                            "NS_hemisphere": NS_hemisphere, "power": power
                        })
                        # print(location_sers)
                        if location_sers.is_valid():
                            location_sers.save()
                        else:
                            # print(location_sers.errors)
                            print('is_valid error')
                    return JsonResponse({"status": "success"})

            return JsonResponse({"status": "fail"})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "error": str(e)})


class StatisticalToOneView(LoginRequiredMixin, View):
    """
    图形统计
    """

    def get(self, request, imei_id):
        time_list = list()
        speed_list = list()
        now_time = datetime.now()
        start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time = now_time + timedelta(hours=-8)
        permission = request.user.permission
        print(permission)
        if permission != 'superadmin':
            device = DevicesInfo.objects.filter(id=imei_id)
            try:
                company = request.user.company.company_name
                device_company = device[0].company.company_name
                # print(company)
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('select_device'))
            print(device_company)
            print(company)
            if company and device and device_company == company:
                location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2,
                                                       time__lte=end_time).order_by(
                    'time')
                deivce = DevicesInfo.objects.filter(id=imei_id)
                if deivce:
                    imei = deivce[0].imei
                else:
                    imei = ""
                for i in location:
                    time_list.append(datetime.strftime(i.time + timedelta(hours=8), '%Y%m%d %H:%M:%S'))
                    # time_list.append("")
                    # print(i.speed) float('%0.2f' % (float(i['speed']) * 0.5144444))
                    speed_list.append(float('%0.2f' % (float(i.speed) * 0.5144444)))
                create_history_record(request.user, '查看图形统计')
                return render(request, 'statistical_one.html', {
                    "imei": imei,
                    # "district": district,
                    # "all_wt_datas": all_wt_datas,
                    "time_list": time_list,
                    "speed_list": speed_list,
                    # "all_address_count2": all_address_count2,
                    # "all_address_count3": all_address_count3,
                    # "all_address_count4": all_address_count4,
                    "start_time": start_time,
                    "end_time": now_time
                })
            else:
                return HttpResponseRedirect(reverse('select_device'))
        else:
            location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2, time__lte=end_time).order_by(
                'time')
            deivce = DevicesInfo.objects.filter(id=imei_id)
            if deivce:
                imei = deivce[0].imei
            else:
                imei = ""
            for i in location:
                time_list.append(datetime.strftime(i.time + timedelta(hours=8), '%Y%m%d %H:%M:%S'))
                # time_list.append("")
                # print(i.speed) float('%0.2f' % (float(i['speed']) * 0.5144444))
                speed_list.append(float('%0.2f' % (float(i.speed) * 0.5144444)))
            create_history_record(request.user, '查看图形统计')
            return render(request, 'statistical_one.html', {
                "imei": imei,
                # "district": district,
                # "all_wt_datas": all_wt_datas,
                "time_list": time_list,
                "speed_list": speed_list,
                # "all_address_count2": all_address_count2,
                # "all_address_count3": all_address_count3,
                # "all_address_count4": all_address_count4,
                "start_time": start_time,
                "end_time": now_time
            })

    def post(self, request, imei_id):
        time_list = list()
        speed_list = list()
        start_time = request.POST.get('start_time', '')
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time = request.POST.get('end_time', '')
        end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)

        permission = request.user.permission
        print(permission)
        if permission != 'superadmin':
            device = DevicesInfo.objects.filter(id=imei_id)
            try:
                company = request.user.company.company_name
                device_company = device[0].company.company_name
                # print(company)
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('select_device'))
            print(device_company)
            print(company)
            if company and device and device_company == company:
                location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2,
                                                       time__lte=end_time2).order_by(
                    'time')
                deivce = DevicesInfo.objects.filter(id=imei_id)
                if deivce:
                    imei = deivce[0].imei
                else:
                    imei = ""
                for i in location:
                    time_list.append(datetime.strftime(i.time + timedelta(hours=8), '%Y%m%d %H:%M:%S'))
                    speed_list.append(float('%0.2f' % (float(i.speed) * 0.5144444)))
                # print(time_list)
                # print(speed_list)
                create_history_record(request.user, '查看图形统计')
                return render(request, 'statistical_one.html', {
                    "imei": imei,
                    # "district": district,
                    # "all_wt_datas": all_wt_datas,
                    "time_list": time_list,
                    "speed_list": speed_list,
                    # "all_address_count2": all_address_count2,
                    # "all_address_count3": all_address_count3,
                    # "all_address_count4": all_address_count4,
                    "start_time": start_time,
                    "end_time": end_time
                })
            else:
                return HttpResponseRedirect(reverse('select_device'))
        else:
            location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2,
                                                   time__lte=end_time2).order_by(
                'time')
            deivce = DevicesInfo.objects.filter(id=imei_id)
            if deivce:
                imei = deivce[0].imei
            else:
                imei = ""
            for i in location:
                time_list.append(datetime.strftime(i.time + timedelta(hours=8), '%Y%m%d %H:%M:%S'))
                speed_list.append(float('%0.2f' % (float(i.speed) * 0.5144444)))
            # print(time_list)
            # print(speed_list)
            create_history_record(request.user, '查看图形统计')
            return render(request, 'statistical_one.html', {
                "imei": imei,
                # "district": district,
                # "all_wt_datas": all_wt_datas,
                "time_list": time_list,
                "speed_list": speed_list,
                # "all_address_count2": all_address_count2,
                # "all_address_count3": all_address_count3,
                # "all_address_count4": all_address_count4,
                "start_time": start_time,
                "end_time": end_time
            })


class LocationTrackView(LoginRequiredMixin, View):
    """
    轨迹回放
    """

    def get(self, request, imei_id, start_time, end_time):
        # now_time = datetime.now()
        # start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2, time__lte=end_time2).order_by(
            'time')
        lng = list()
        lat = list()
        for i in location:
            if i.longitude and i.latitude:
                longitude, latitude = gps_conversion(i.longitude, i.latitude)
                lng.append(longitude)
                lat.append(latitude)
        if location:
            s_e_point = gps_conversion(location[0].longitude, location[0].latitude)
            # print(s_e_point)
        else:
            s_e_point = [106.53233, 29.522584]
        return render(request, 'track.html', {
            "lng": lng, "lat": lat, "s_e_point": s_e_point
        })


class AppStartTestRecordView(View):
    def post(self, request):
        try:
            start_time = request.POST.get('start_time', '')
            devices_id = request.POST.get('devices_id', '')
            remarks = request.POST.get('remarks', '')
            username = request.POST.get('username', '')
            wind = request.POST.get('wind', '')
            warning_speed = request.POST.get('warning_speed', '')
            company_id = request.POST.get('company_id', '')
            TestRecord.objects.create(start_time=start_time, devices_id=devices_id, remarks=remarks,
                                      company_id=company_id, wind=wind, warning_speed=warning_speed)
            return JsonResponse({
                "error_no": 0
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class AppEndTestRecordView(View):
    def post(self, request):
        try:
            username = request.POST.get('username')
            record_id = request.POST.get('record_id')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            print(permission)
            if permission == 'superadmin':
                record = TestRecord.objects.get(id=record_id)
                record.end_time = datetime.now()
                record.save()
            else:
                try:
                    company_id = user.company.id
                    record = TestRecord.objects.get(id=record_id, company_id=company_id)
                    record.end_time = datetime.now()
                    record.save()
                except Exception as e:
                    print(e)
                    return JsonResponse({
                        "error_no": -1,
                        "info": str(e)
                    })

            return JsonResponse({
                "error_no": 0
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class AppTestRecordView(View):
    def post(self, request):
        try:
            username = request.POST.get('username')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            print(permission)
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            if permission == 'superadmin':
                all_test_record = TestRecord.objects.filter(start_time__gte=start_time, start_time__lte=end_time)
                record_list = list()
                if all_test_record:
                    for record in all_test_record:
                        devices_id_list = record.devices_id.split(',')
                        desc_list = list()
                        imei_list = list()
                        for i in devices_id_list:
                            d = DevicesInfo.objects.get(id=i)
                            desc = d.desc
                            imei = d.imei
                            desc_list.append(desc)
                            imei_list.append(imei)
                        data = {
                            "recode_id": record.id,
                            "remarks": record.remarks,
                            "devices_id": ','.join(desc_list),
                            "imei_list": ','.join(imei_list),
                            "start_time": record.start_time,
                            "end_time": record.end_time,
                            "wind": record.wind,
                            "warning_speed": record.warning_speed,
                            "company": record.company.company_name
                        }
                        record_list.append(data)
                    print(record_list)
                return JsonResponse({
                    "error_no": 0,
                    "all_test_record": record_list,
                    "start_time": start_time,
                    "end_time": end_time
                })
            else:
                try:
                    company = user.company.company_name
                    # print(company)
                except Exception as e:
                    print(e)
                    return JsonResponse({
                        "error_no": -1,
                        "info": str(e)
                    })
                if company:
                    all_test_record = TestRecord.objects.filter(company__company_name=company)
                    record_list = list()
                    if all_test_record:
                        for record in all_test_record:
                            devices_id_list = record.devices_id.split(',')
                            desc_list = list()
                            imei_list = list()
                            for i in devices_id_list:
                                d = DevicesInfo.objects.get(id=i)
                                desc = d.desc
                                imei = d.imei
                                desc_list.append(desc)
                                imei_list.append(imei)
                            data = {
                                "recode_id": record.id,
                                "remarks": record.remarks,
                                "devices_id": ','.join(desc_list),
                                "imei_list": ','.join(imei_list),
                                "start_time": record.start_time,
                                "end_time": record.end_time,
                                "wind": record.wind,
                                "warning_speed": record.warning_speed,
                                "company": record.company.company_name
                            }
                            record_list.append(data)
                        print(record_list)
                    return JsonResponse({
                        "error_no": 0,
                        "all_test_record": record_list,
                        "start_time": start_time,
                        "end_time": end_time
                    })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


# daijian 191030
class AppTestRecordSpeedListApiView(APIView):
    def get(self, request):
        try:
            test_id = request.query_params.get('test_id')
            start_ind = request.query_params.get("start_ind")
            read_count = request.query_params.get("read_count")
            if int(start_ind) < 0:
                start_ind = 0
            if int(read_count) < 0:
                read_count = 0
            print(test_id, start_ind, read_count)
            test_record = TestRecord.objects.get(id=test_id)

            delta = timedelta(hours=8)
            start_time = test_record.start_time
            end_time = test_record.end_time
            device_list_str = test_record.devices_id
            devices_list = device_list_str.split(',')

            sql = "select time,  GROUP_CONCAT(imei_id) as imeis, GROUP_CONCAT(speed) as speeds from  \
                data_info_locationinfo where imei_id in(" + device_list_str + ") \
                and time >='" + (start_time - delta).strftime("%Y%m%d%H%M%S") + "'  \
                and time <='" + (end_time - delta).strftime("%Y%m%d%H%M%S") + "'    \
                group by time order by time desc;"
            print(sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                print(data)
            sendlist = list()
            for rec in data:
                dc = len(devices_list)
                sendrec = [""] * (dc + 1)
                rectime = rec[0] + delta
                recimeis = rec[1].split(',')
                recspeeds = rec[2].split(',')
                sendrec[0] = rectime
                cc = 0
                for dd in devices_list:
                    ii = 0
                    for im in recimeis:
                        if dd == im:
                            sendrec[cc + 1] = str(float('%0.2f' % (float(recspeeds[ii]) * 0.5144444)))
                        ii = ii + 1
                    cc = cc + 1
                sendlist.append(sendrec)

            return JsonResponse({
                "error_no": 0,
                "all_count": len(sendlist),
                "all_test_record": sendlist[int(start_ind):int(start_ind + read_count)],
                "start_time": start_time,
                "end_time": end_time
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class AppTestRecordLocationListApiView(APIView):
    def get(self, request):
        try:
            test_id = request.query_params.get('test_id')
            print(test_id)
            test_record = TestRecord.objects.get(id=test_id)
            delta = timedelta(hours=8)
            start_time = test_record.start_time
            end_time = test_record.end_time
            device_list_str = test_record.devices_id
            devices_list = device_list_str.split(',')

            sql = "select time,  GROUP_CONCAT(imei_id) as imeis, GROUP_CONCAT(longitude) as longitudes,\
                 GROUP_CONCAT(latitude) as latitudes,GROUP_CONCAT(speed) as speeds from  \
                data_info_locationinfo where imei_id in(" + device_list_str + ") \
                and time >='" + (start_time - delta).strftime("%Y%m%d%H%M%S") + "'  \
                and time <='" + (end_time - delta).strftime("%Y%m%d%H%M%S") + "'    \
                group by time order by time desc;"
            print(sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                # print(data)
            sendlist = list()
            for rec in data:
                sendrec = [""] * (len(devices_list) * 3 + 1)
                rectime = rec[0] + delta
                recimeis = rec[1].split(',')
                reclongitudes = rec[2].split(',')
                reclatitude = rec[3].split(',')
                recspeeds = rec[4].split(',')
                sendrec[0] = rectime
                cc = 1
                print(rec)
                for device in devices_list:
                    ii = 0
                    for imei in recimeis:
                        if device == imei:
                            sendrec[cc], sendrec[cc + 1] = gps_conversion(str(reclongitudes[ii]), str(reclatitude[ii]))
                            sendrec[cc + 2] = str(float('%0.2f' % (float(recspeeds[ii]) * 0.5144444)))
                            print(reclongitudes[ii] + "," + reclatitude[ii] + "," + recspeeds[ii])
                        ii = ii + 1
                    cc = cc + 3
                print(sendrec)
                sendlist.append(sendrec)

            return JsonResponse({
                "error_no": 0,
                "all_test_record": sendlist,
                "start_time": start_time,
                "end_time": end_time
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })