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
from .forms import LocationInfoSerializer, DevicesInfoSerializer, TestRecordForm
from rest_framework.views import APIView
from django.core.urlresolvers import reverse
import re
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import connection
import json
from django.db.models import Q


class DeviceDataInfoView(LoginRequiredMixin, View):
    def get(self, request):
        permission = request.user.permission
        print(permission)
        if permission == 'superadmin':
            all_devices = DevicesInfo.objects.all()
        else:
            try:
                company = request.user.company.company_name
                print(company)
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


class RecordInfoView(LoginRequiredMixin, View):
    def get(self, request):
        permission = request.user.permission
        print(permission)
        now_time = datetime.now().replace(microsecond=0)
        start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        if permission == 'superadmin':
            all_test_record = TestRecord.objects.all().values()
            for record in all_test_record:
                imei_id_list = (record['devices_id']).split(',')
                devices = DevicesInfo.objects.filter(id__in=imei_id_list)
                if devices:
                    record['devices_id'] = ",".join(i.desc for i in devices)
                    record['company_id'] = devices[0].company.company_name
                else:
                    record['devices_id'] = ""
                    record['company_id'] = ""

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
                all_test_record = TestRecord.objects.filter(company__company_name=company).values()
                for record in all_test_record:
                    imei_id_list = (record['devices_id']).split(',')
                    devices = DevicesInfo.objects.filter(id__in=imei_id_list)
                    record['devices_id'] = ",".join(i.desc for i in devices)
            else:
                all_test_record = ""
        return render(request, 'select2_device.html', {
            "all_test_record": all_test_record,
            "start_time": start_time,
            "end_time": now_time
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


class LocationPaginatorInfoView(LoginRequiredMixin, View):
    def get(self, request, imei_id):

        permission = request.user.permission
        print(permission)
        now_time = datetime.now().replace(microsecond=0)
        start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        if permission != 'superadmin':
            device = DevicesInfo.objects.filter(id=imei_id)
            try:
                company = request.user.company.company_name
                device_company = device[0].company.company_name
                # print(company)
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('select_device'))
            if company and device and device_company == company:
                return render(request, 'location_paginator.html', {
                    "imei_id": imei_id,
                    "start_time": start_time,
                    "end_time": now_time
                })
            else:
                return HttpResponseRedirect(reverse('select_device'))
        else:
            return render(request, 'location_paginator.html', {
                "imei_id": imei_id,
                "start_time": start_time,
                "end_time": now_time
            })

    def post(self, request, imei_id):
        start_time = request.POST.get('start_time', '')
        end_time = request.POST.get('end_time', '')
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        draw = request.POST.get('draw', "1")
        start = request.POST.get('start', "0")
        length = request.POST.get('length', "10")
        page = request.POST.get('page', "1")
        print(draw, start, length, page)

        location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                     time__lte=end_time2).order_by('-time')
        page2 = request.POST.get('page', '1')
        # print(len(all_wt_data))
        paginator = Paginator(location_infos, length)
        try:
            location_page = paginator.page(page2)
        except PageNotAnInteger:
            location_page = paginator.page(1)
        except EmptyPage:
            location_page = paginator.page(paginator.num_pages)
        print(location_page)
        data = []
        for i in location_page:

            data_time = i.time
            if data_time:
                data_time = datetime.strftime(data_time + timedelta(hours=8), '%Y-%m-%d %H:%M:%S')

            data_spped = i.speed
            if data_spped:
                data_spped = float('%0.2f' % (float(data_spped) * 0.5144444))

            data_longitude = i.longitude
            data_latitude = i.latitude
            if data_longitude and data_latitude:
                data_longitude, data_latitude = gps_conversion(data_longitude, data_latitude)

            data_power = i.power
            if data_power and len(data_power) > 4:
                data_power = float('%0.2f' % (float(data_power[3:]) * 0.001))

            data.append({
                "imei": i.imei.imei,
                "data_time": data_time,
                "lon_lat": str(data_longitude) + ',' + str(data_latitude),
                "altitude": i.altitude,
                "speed": data_spped,
                "direction": i.direction,
                "accuracy": i.accuracy,
                "power": data_power,
                "satellites": i.satellites,
            })
        return JsonResponse({
            "draw": draw,
            "recordsTotal": location_infos.count(),
            "recordsFiltered": location_infos.count(),
            "data": data
        })


def time_difference(location_infos, n):
    if n == 0:
        return timedelta(seconds=0)
    # if (location_infos[n].time - location_infos[n-1].time).seconds > 6:
    #     print(location_infos[n].time, location_infos[n-1].time)
    return location_infos[n].time - location_infos[n - 1].time


class LocationDistanceView(APIView):
    def post(self, request):
        start_time = request.data.get('start_time', '')
        end_time = request.data.get('end_time', '')
        imei_id = request.data.get('imei_id', '')
        invalid_speed = request.data.get('invalid_speed', 0.5)
        if invalid_speed:
            invalid_speed = float(invalid_speed)
        else:
            invalid_speed = 0
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        location_infos = LocationInfo.objects.filter(
            imei__id=imei_id, time__gte=start_time2, time__lte=end_time2).exclude(
            Q(speed__isnull=True) | Q(speed="")).order_by('time')
        len_location_infos = len(location_infos)
        total_nums = 0
        average_speed = 0
        is_continue = True
        first_time = None
        last_time = None
        speed_list = list()
        max_list = list()
        if location_infos:
            try:
                for i in range(len_location_infos):
                    speed = location_infos[i].speed
                    speed = float('%0.2f' % (float(speed) * 0.5144444))
                    speed_list.append(speed)
                    # 去掉首位速度小于改值这个值需要商讨确定
                    if speed <= invalid_speed and is_continue:
                        first_time = location_infos[i].time
                        continue
                    # TODO 这里有bug，并不知道多个点没有移动定性固定值不行
                    # elif i+2000 > len_location_infos and speed <= invalid_speed:
                    #     continue
                    # print(i)
                    last_time = location_infos[i].time
                    is_continue = False
                    time_diff = time_difference(location_infos, i).seconds
                    # print(speed)
                    # print(time_diff)
                    total_nums += speed * time_diff

                if not first_time:
                    first_time = location_infos[0].time
                if not last_time:
                    last_time = location_infos[len(location_infos) - 1].time
                sec = (last_time - first_time).seconds
                if sec != 0:
                    average_speed = total_nums / sec
                else:
                    average_speed = total_nums / 1
                first_time = datetime.strftime(first_time + timedelta(hours=8), "%Y-%m-%d %H:%M:%S")
                last_time = datetime.strftime(last_time + timedelta(hours=8), "%Y-%m-%d %H:%M:%S")
                max_speed = max(speed_list)

                max_speed_index = speed_list.index(max_speed)
                max_speed_lon, max_speed_lat = gps_conversion(location_infos[max_speed_index].longitude,
                                                              location_infos[max_speed_index].latitude)
                max_speed_time = datetime.strftime(location_infos[max_speed_index].time + timedelta(hours=8),
                                                   "%Y-%m-%d %H:%M:%S")
                # print(max_speed, max_speed_index, max_speed_time, max_speed_lon, max_speed_lat)
                max_list.append({
                    "max_speed": max_speed, "max_speed_time": max_speed_time,
                    "max_speed_lon": max_speed_lon, "max_speed_lat": max_speed_lat
                })
                while True:
                    speed_list[max_speed_index] = 0
                    if max(speed_list) == max_speed:
                        max_speed_index = speed_list.index(max_speed)
                        max_speed_lon, max_speed_lat = gps_conversion(location_infos[max_speed_index].longitude,
                                                                      location_infos[max_speed_index].latitude)
                        max_speed_time = datetime.strftime(location_infos[max_speed_index].time + timedelta(hours=8),
                                                           "%Y-%m-%d %H:%M:%S")
                        # print(max_speed, max_speed_index, max_speed_time, max_speed_lon, max_speed_lat)
                        max_list.append({
                            "max_speed": max_speed, "max_speed_time": max_speed_time,
                            "max_speed_lon": max_speed_lon, "max_speed_lat": max_speed_lat
                        })
                    else:
                        break
                # print(max_list)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return JsonResponse({
                    "total_nums": '%.2f' % total_nums,
                    "total_nums2": '%.1f' % (total_nums / 1000),
                    "first_time": first_time,
                    "last_time": last_time,
                    "average_speed": '%.2f' % average_speed,
                    "status": "fail",
                    # "max_speed": max_speed,
                    # "max_speed_lon": max_speed_lon,
                    # "max_speed_lat": max_speed_lat,
                    # "max_speed_time": max_speed_time,
                    "max_list": max_list,
                    "msg": str(e)
                })
        return JsonResponse({
            "total_nums": '%.2f' % total_nums,
            "total_nums2": '%.1f' % (total_nums / 1000),
            "average_speed": '%.2f' % average_speed,
            "first_time": first_time,
            "last_time": last_time,
            # "max_speed": max_speed,
            # "max_speed_lon": max_speed_lon,
            # "max_speed_lat": max_speed_lat,
            # "max_speed_time": max_speed_time,
            "max_list": max_list,
            "status": "success"
        })


class RecordLocationInfoView(LoginRequiredMixin, View):
    def get(self, request, record_id):

        permission = request.user.permission
        print(permission)
        print(record_id)
        test_record = TestRecord.objects.get(id=record_id)

        delta = timedelta(hours=8)
        start_time = test_record.start_time
        end_time = test_record.end_time
        device_list_str = test_record.devices_id
        devices_list = device_list_str.split(',')

        sql = "select time,  GROUP_CONCAT(imei_id) as imeis, GROUP_CONCAT(speed) as speeds from  \
            data_info_locationinfo where imei_id in(" + device_list_str + ") \
            and time >='" + (start_time - delta).strftime("%Y%m%d%H%M%S") + "'  \
            and time <='" + (end_time - delta).strftime("%Y%m%d%H%M%S") + "'    \
            group by time order by time;"
        # print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
            # print(data)
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
            # print(sendrec)
            sendlist.append(sendrec)
        devs = DevicesInfo.objects.filter(id__in=devices_list)
        devlist = DevicesInfoSerializer(devs, many=True)
        # print(a)
        return render(request, 'record_location_infos.html', {
            "location_data": sendlist,
            "start_time": start_time,
            "end_time": end_time,
            "desc_list": devlist.data
        })


class RecordLocationPaginatorView(LoginRequiredMixin, View):
    def get(self, request, record_id):
        permission = request.user.permission
        # print(permission)
        if permission == "superadmin":
            test_record = TestRecord.objects.get(id=record_id)
        else:
            company_id = request.user.company_id
            try:
                test_record = TestRecord.objects.get(id=record_id, company_id=company_id)
            except TestRecord.DoesNotExist as e:
                return HttpResponseRedirect(reverse('select2_device'))
        start_time = test_record.start_time
        end_time = test_record.end_time
        device_list_str = test_record.devices_id
        devices_list = device_list_str.split(',')

        devs = DevicesInfo.objects.filter(id__in=devices_list)
        devlist = DevicesInfoSerializer(devs, many=True)
        # print(a)
        return render(request, 'record_location_paginator.html', {
            "start_time": start_time,
            "end_time": end_time,
            "desc_list": devlist.data,
            "record_id": record_id
        })

    def post(self, request, record_id):

        # permission = request.user.permission
        # print(permission)
        test_record = TestRecord.objects.get(id=record_id)

        delta = timedelta(hours=8)
        start_time = test_record.start_time
        end_time = test_record.end_time
        device_list_str = test_record.devices_id
        devices_list = device_list_str.split(',')

        draw = request.POST.get('draw', "1")
        start = request.POST.get('start', "0")
        length = request.POST.get('length', "10")
        page = request.POST.get('page', "1")
        print(draw, start, length, page)

        sql = "select time,  GROUP_CONCAT(imei_id) as imeis, GROUP_CONCAT(speed) as speeds from  \
            data_info_locationinfo where imei_id in(" + device_list_str + ") \
            and time >='" + (start_time - delta).strftime("%Y%m%d%H%M%S") + "'  \
            and time <='" + (end_time - delta).strftime("%Y%m%d%H%M%S") + "'    \
            group by time order by time;"
        # print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
            # print(data)

        page2 = request.POST.get('page', '1')
        # print(len(all_wt_data))
        paginator = Paginator(data, length)
        try:
            data_page = paginator.page(page2)
        except PageNotAnInteger:
            data_page = paginator.page(1)
        except EmptyPage:
            data_page = paginator.page(paginator.num_pages)

        sendlist = list()

        for rec in data_page:
            dc = len(devices_list)
            sendrec = [""] * (dc + 1)
            rectime = rec[0] + delta
            recimeis = rec[1].split(',')
            recspeeds = rec[2].split(',')
            sendrec[0] = rectime.strftime("%Y-%m-%d %H:%M:%S")
            cc = 0
            for dd in devices_list:
                ii = 0
                for im in recimeis:
                    if dd == im:
                        sendrec[cc + 1] = str(float('%0.2f' % (float(recspeeds[ii]) * 0.5144444)))
                    ii = ii + 1
                cc = cc + 1
            # print(sendrec)
            sendlist.append(sendrec)

        return JsonResponse({
            "draw": draw,
            "recordsTotal": len(data),
            "recordsFiltered": len(data),
            "data": sendlist
        })


class RecordLocationDistanceView(APIView):
    def post(self, request):
        try:
            record_id = request.data.get('record_id')
            # invalid_speed = request.data.get('invalid_speed', 0.5)
            print(record_id)
            # if invalid_speed:
            #     invalid_speed = float(invalid_speed)
            # else:
            #     invalid_speed = 0
            test_record = TestRecord.objects.get(id=record_id)
            delta = timedelta(hours=8)
            start_time = test_record.start_time - delta
            end_time = test_record.end_time - delta
            device_list_str = test_record.devices_id
            devices_list = device_list_str.split(',')
            data_list = list()
            for imei_id in devices_list:
                location_infos = LocationInfo.objects.filter(
                    imei__id=imei_id, time__gte=start_time, time__lte=end_time).exclude(
                    Q(speed__isnull=True) | Q(speed="")).order_by('time')
                len_location_infos = len(location_infos)
                total_nums = 0
                average_speed = 0
                # is_continue = True
                first_time = None
                last_time = None
                speed_list = list()
                max_list = list()
                if location_infos:
                    try:
                        for i in range(len_location_infos):
                            speed = location_infos[i].speed
                            speed = float('%0.2f' % (float(speed) * 0.5144444))
                            speed_list.append(speed)
                            # 去掉首位速度小于改值这个值需要商讨确定
                            # if speed <= invalid_speed and is_continue:
                            #     first_time = location_infos[i].time
                            #     continue
                            # TODO 这里有bug，并不知道多个点没有移动定性固定值不行
                            # elif i+2000 > len_location_infos and speed <= invalid_speed:
                            #     continue
                            # print(i)
                            last_time = location_infos[i].time
                            # is_continue = False
                            time_diff = time_difference(location_infos, i).seconds
                            # print(speed)
                            # print(time_diff)
                            total_nums += speed * time_diff

                        if not first_time:
                            first_time = location_infos[0].time
                        if not last_time:
                            last_time = location_infos[len(location_infos) - 1].time
                        average_speed = total_nums / (last_time - first_time).seconds
                        first_time = datetime.strftime(first_time + timedelta(hours=8), "%Y-%m-%d %H:%M:%S")
                        last_time = datetime.strftime(last_time + timedelta(hours=8), "%Y-%m-%d %H:%M:%S")
                        max_speed = max(speed_list)

                        max_speed_index = speed_list.index(max_speed)
                        max_speed_lon, max_speed_lat = gps_conversion(location_infos[max_speed_index].longitude,
                                                                      location_infos[max_speed_index].latitude)
                        max_speed_time = datetime.strftime(location_infos[max_speed_index].time + timedelta(hours=8),
                                                           "%Y-%m-%d %H:%M:%S")
                        # print(max_speed, max_speed_index, max_speed_time, max_speed_lon, max_speed_lat)
                        max_list.append({
                            "max_speed": max_speed, "max_speed_time": max_speed_time,
                            "max_speed_lon": max_speed_lon, "max_speed_lat": max_speed_lat
                        })
                        while True:
                            speed_list[max_speed_index] = 0
                            if max(speed_list) == max_speed:
                                max_speed_index = speed_list.index(max_speed)
                                max_speed_lon, max_speed_lat = gps_conversion(location_infos[max_speed_index].longitude,
                                                                              location_infos[max_speed_index].latitude)
                                max_speed_time = datetime.strftime(
                                    location_infos[max_speed_index].time + timedelta(hours=8),
                                    "%Y-%m-%d %H:%M:%S")
                                # print(max_speed, max_speed_index, max_speed_time, max_speed_lon, max_speed_lat)
                                max_list.append({
                                    "max_speed": max_speed, "max_speed_time": max_speed_time,
                                    "max_speed_lon": max_speed_lon, "max_speed_lat": max_speed_lat
                                })
                            else:
                                break
                        # print(max_list)
                    except Exception as e:
                        data_list.append({
                            "status": "fail",
                            "device_data": {
                                "total_nums": '%.2f' % total_nums,
                                "total_nums2": '%.1f' % (total_nums / 1000),
                                "average_speed": '%.2f' % average_speed,
                                "first_time": first_time,
                                "last_time": last_time,
                                # "max_speed": max_speed,
                                # "max_speed_lon": max_speed_lon,
                                # "max_speed_lat": max_speed_lat,
                                # "max_speed_time": max_speed_time,
                                "max_list": max_list
                            },
                            "desc": location_infos[0].imei.desc,
                            "device_id": str(location_infos[0].imei.id),
                            "msg": str(e)
                        })

                    data_list.append({
                        "status": "success",
                        "device_data": {
                            "total_nums": '%.2f' % total_nums,
                            "total_nums2": '%.1f' % (total_nums / 1000),
                            "average_speed": '%.2f' % average_speed,
                            "first_time": first_time,
                            "last_time": last_time,
                            # "max_speed": max_speed,
                            # "max_speed_lon": max_speed_lon,
                            # "max_speed_lat": max_speed_lat,
                            # "max_speed_time": max_speed_time,
                            "max_list": max_list
                        },
                        "device_id": str(location_infos[0].imei.id),
                        "desc": location_infos[0].imei.desc
                    })
            return JsonResponse({
                "status": "success",
                "data_list": data_list
            })
        except Exception as e:
            return JsonResponse({
                "status": "fail",
                "msg": str(e)
            })


class RecordTrackView(LoginRequiredMixin, View):
    def get(self, request, record_id):

        permission = request.user.permission
        print(permission)
        print(record_id)

        if permission == "superadmin":
            test_record = TestRecord.objects.get(id=record_id)
        else:
            company_id = request.user.company_id
            try:
                test_record = TestRecord.objects.get(id=record_id, company_id=company_id)
            except TestRecord.DoesNotExist as e:
                return HttpResponseRedirect(reverse('select2_device'))
        # test_record = TestRecord.objects.get(id=record_id)

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
                group by time order by time;"
        # print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
            # print(data)
        sendlist = list()
        for rec in data:
            # dc = len(devices_list)
            sendrec = [""] * (len(devices_list) * 3 + 1)
            rectime = rec[0] + delta
            recimeis = rec[1].split(',')
            reclongitudes = rec[2].split(',')
            reclatitude = rec[3].split(',')
            recspeeds = rec[4].split(',')
            sendrec[0] = rectime.strftime("%Y-%m-%d %H:%M:%S")
            cc = 1
            for dd in devices_list:
                ii = 0
                for im in recimeis:
                    if dd == im:
                        sendrec[cc], sendrec[cc + 1] = gps_conversion(str(reclongitudes[ii]), str(reclatitude[ii]))
                        sendrec[cc + 2] = str(float('%0.2f' % (float(recspeeds[ii]) * 0.5144444)))
                    ii = ii + 1
                cc = cc + 3
            # print(sendrec)
            sendlist.append(sendrec)
        devs = DevicesInfo.objects.filter(id__in=devices_list)
        devlist = DevicesInfoSerializer(devs, many=True)
        # s_e_point = [str(sendlist[0][1]), str(sendlist[0][2])]
        # for i in enumerate(devices_list):
        #     print(i)
        #     if sendlist[0][1 + 3 * i[0]] != "":
        #         s_e_point = [str(sendlist[0][1 + i[0] * 3]), str(sendlist[0][2 + i[0] * 3])]
        #         break
        # print(sendlist[0])
        # print(s_e_point)
        # json_name = datetime.now().strftime('%Y%m%d%H%M%S')
        # filename = 'media/path/' + json_name + '.json'
        json_list = list()
        devcount = 0
        for dev in devlist.data:
            path_list = list()
            # speed_list = list()
            # print(sendlist)
            for ix in enumerate(sendlist):
                if sendlist[ix[0]][1 + devcount * 3] != "" and sendlist[ix[0]][1 + devcount * 3] != "0":
                    path_list.append([sendlist[ix[0]][1 + devcount * 3], sendlist[ix[0]][2 + devcount * 3]])
            if len(path_list) > 0:
                dict_path = dict()
                dict_path["name"] = dev["desc"]
                json_list.append(dict_path)
                dict_path["path"] = path_list
            devcount = devcount + 1
        # print(json_list)
        return render(request, 'recordtrack.html', {
            "json_data": json.dumps(json_list),
            "start_time": start_time,
            "end_time": end_time,
            "desc_list": json.dumps(devlist.data)
        })


class RecordStatisticalView(LoginRequiredMixin, View):

    def get(self, request, record_id):
        permission = request.user.permission
        print(permission)
        print(record_id)
        if permission == "superadmin":
            test_record = TestRecord.objects.get(id=record_id)
        else:
            company_id = request.user.company_id
            try:
                test_record = TestRecord.objects.get(id=record_id, company_id=company_id)
            except TestRecord.DoesNotExist as e:
                return HttpResponseRedirect(reverse('select2_device'))
        # test_record = TestRecord.objects.get(id=record_id)

        delta = timedelta(hours=8)
        start_time = test_record.start_time
        end_time = test_record.end_time
        device_list_str = test_record.devices_id
        devices_list = device_list_str.split(',')

        sql = "select time,  GROUP_CONCAT(imei_id) as imeis, GROUP_CONCAT(speed) as speeds from  \
            data_info_locationinfo where imei_id in(" + device_list_str + ") \
            and time >='" + (start_time - delta).strftime("%Y%m%d%H%M%S") + "'  \
            and time <='" + (end_time - delta).strftime("%Y%m%d%H%M%S") + "'    \
            group by time order by time;"
        # print(sql)
        with connection.cursor() as cursor:
            cursor.execute(sql)
            data = cursor.fetchall()
            # print(data)
        sendlist = list()

        for rec in data:
            dc = len(devices_list)
            sendrec = [""] * (dc + 1)
            rectime = rec[0] + delta
            recimeis = rec[1].split(',')
            recspeeds = rec[2].split(',')
            sendrec[0] = rectime.strftime("%Y-%m-%d %H:%M:%S")
            cc = 0
            for dd in devices_list:
                ii = 0
                for im in recimeis:
                    if dd == im:
                        sendrec[cc + 1] = str(float('%0.2f' % (float(recspeeds[ii]) * 0.5144444)))
                    ii = ii + 1
                cc = cc + 1
            # print(sendrec)
            sendlist.append(sendrec)
        devs = DevicesInfo.objects.filter(id__in=devices_list)
        devlist = DevicesInfoSerializer(devs, many=True)
        print(len(sendlist))
        create_history_record(request.user, '查看图形统计')
        return render(request, 'statistical.html', {
            "location_data": sendlist,
            "start_time": start_time,
            "end_time": end_time,
            "desc_list": json.dumps(devlist.data)
        })


class AppLocationInfoView(APIView):
    """
    共用单个设备数据查询
    """

    def post(self, request):
        try:
            username = request.META.get('HTTP_USERNAME')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            start_time = request.data.get('start_time')
            end_time = request.data.get('end_time')
            imei_id = request.data.get('imei_id')
            start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            if permission == "superadmin":
                location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                             time__lte=end_time2).order_by('-time')
            else:
                company_id = user.company_id
                location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                             time__lte=end_time2, imei__company_id=company_id).order_by(
                    '-time')
            page = request.data.get('page', '1')
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
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户"
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
            print(start_time)
            print(end_time)
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
                    # daijian 191112 导出原始坐标
                    # if i['longitude'] and i['latitude']:
                    #     i['longitude'], i['latitude'] = gps_conversion(i['longitude'], i['latitude'])
                    if i['power'] and len(i['power']) > 4:
                        i['power'] = float('%0.2f' % (float(i['power'][3:]) * 0.001))
                    data = [
                        i['imei'], i['time'], i['longitude'], i['latitude'], i['direction'], i['speed'], i['altitude'],
                        i['accuracy'],
                        i['power'], i['satellites']
                    ]

                    location_datas.append(data)
                if location_datas:
                    # print("excel")
                    # print(location_datas)
                    now = datetime.now()
                    name = datetime.strftime(now, '%m-%d-%H-%M-%S')
                    stime = datetime.strftime(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'), '%m%d%H%M')
                    etime = datetime.strftime(datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'), '%m%d%H%M')
                    filename = 'media/excel/' + imei + '_' + stime + '_' + etime + '.xlsx'
                    file = '测流数据' + stime + '.xlsx'
                    export_excel(location_datas, '测流数据', filename)
                    create_history_record(request.user, '测流数据导出Excel：%s' % file)
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
                re_data_list = re.findall(r"\$G[N,P]RMC[^#]*##\$G[N,P]GGA[^#]*##[^#]*##", value, re.S)
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
                            if len(d) > 10 and (d_list[0] == '$GNRMC' or d_list[0] == '$GPRMC'):
                                # print('$GNRMC', d_list)
                                time = datetime.strptime((d_list[9] + d_list[1][:6]), '%d%m%y%H%M%S')
                                longitude = d_list[5]
                                latitude = d_list[3]
                                speed = d_list[7]
                                direction = d_list[8]
                                EW_hemisphere = d_list[6]
                                NS_hemisphere = d_list[4]
                            elif len(d) > 10 and (d_list[0] == '$GNGGA' or d_list[0] == '$GPGGA'):
                                # print('$GNGGA', d_list)
                                satellites = d_list[7]
                                accuracy = d_list[8]
                                altitude = d_list[9]
                            elif 'VOL' in d_list[0] or 'CHG' in d_list[0] or 'FUL' in d_list[0]:
                                # print('power', d_list)
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

        permission = request.user.permission
        print(permission)
        if permission == "superadmin":
            location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2,
                                                   time__lte=end_time2).order_by('time')
        else:
            try:
                device = DevicesInfo.objects.filter(id=imei_id)
                company = request.user.company.company_name
                device_company = device[0].company.company_name
            except TestRecord.DoesNotExist as e:
                return HttpResponseRedirect(reverse('select_device'))
            if company and device and device_company == company:
                location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2,
                                                       time__lte=end_time2).order_by('time')
            else:
                return HttpResponseRedirect(reverse('select_device'))
        json_list = list()
        location_list = list()
        speed_list = list()
        dict_path = dict()
        if len(location) > 0:
            dict_path["name"] = location[0].imei.desc
            for i in location:
                if i.longitude and i.latitude:
                    longitude, latitude = gps_conversion(i.longitude, i.latitude)
                    location_list.append([longitude, latitude])
                    speed_list.append([(i.time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"), float(i.speed) * 0.5144444])

            dict_path["path"] = location_list
            dict_path["speed"] = speed_list
            json_list.append(dict_path)
        if location:
            s_e_point = gps_conversion(location[0].longitude, location[0].latitude)
        else:
            s_e_point = [106.53233, 29.522584]
        return render(request, 'track.html', {
            "json_data": json_list, "s_e_point": s_e_point
        })


class AppStartTestRecordView(APIView):
    def post(self, request):
        try:
            username = request.META.get('HTTP_USERNAME')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            if permission == "superadmin":
                company_id = request.data.get('company_id')
            else:
                company_id = user.company_id
            start_time = request.data.get('start_time')
            devices_id = request.data.get('devices_id')
            remarks = request.data.get('remarks', '')
            wind = request.data.get('wind', '')
            warning_speed = request.data.get('warning_speed')
            TestRecord.objects.create(start_time=start_time, devices_id=devices_id, remarks=remarks,
                                      company_id=company_id, wind=wind, warning_speed=warning_speed)
            create_history_record(username, '开始测量记录 %s' % TestRecord.remarks)
            return JsonResponse({
                "error_no": 0
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class AppEndTestRecordView(APIView):
    def post(self, request):
        try:
            username = request.META.get('HTTP_USERNAME')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            record_id = request.data.get('record_id')
            if permission != "superadmin":
                company_id = user.company_id
                record_id = TestRecord.objects.get(company_id=company_id, id=record_id).id

            record = TestRecord.objects.get(id=record_id)
            record.end_time = datetime.now()
            record.save()
            create_history_record(username, '结束测量记录 %s' % TestRecord.remarks)
            return JsonResponse({
                "error_no": 0
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户"
            })
        except TestRecord.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个记录"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class TestRecordDoneView(View):
    """
    测量数据-已完成查询
    """

    def post(self, request):
        try:
            username = request.META.get('HTTP_USERNAME')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            if permission == 'superadmin':
                all_test_record = TestRecord.objects.all()
                record_list = list()
                if all_test_record:
                    for record in all_test_record:
                        if not record.end_time:
                            continue
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
                create_history_record(username, '查询已完成的测量记录')
                return JsonResponse({
                    "error_no": 0,
                    "all_test_record": record_list,
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
                            if not record.end_time:
                                continue
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
                    create_history_record(username, '查询已完成的测量记录')
                    return JsonResponse({
                        "error_no": 0,
                        "all_test_record": record_list
                    })
        except TestRecord.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个记录"
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class TestRecordDoneDelView(View):
    def post(self, request):
        try:
            username = request.META.get('HTTP_USERNAME')
            user = UserProfile.objects.get(username=username)
            try:
                record_id = request.data.get('record_id')
            except Exception as e:
                record_id = request.POST.get('record_id')
            permission = user.permission
            if permission == 'superadmin':
                test_record = TestRecord.objects.get(id=record_id)
                print(test_record)
                test_record.delete()
                create_history_record(username, '删除已完成的测量记录 %s' % test_record.remarks)
                return JsonResponse({
                    "error_no": 0,
                    "status": "success"
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
                    test_record = TestRecord.objects.get(id=record_id, company__company_name=company)
                    test_record.delete()
                    create_history_record(username, '删除已完成的测量记录 %s' % test_record.remarks)
                    return JsonResponse({
                        "error_no": 0,
                        "status": "success"
                    })
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户",
                "msg": "没有这个用户"
            })
        except TestRecord.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个记录",
                "msg": "没有这个记录"
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户",
                "msg": "没有这个用户"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e),
                "msg": str(e)
            })


class TestRecordNotDoneView(View):
    """
    测量数据-正在测量查询
    """

    def post(self, request):
        try:
            username = request.META.get('HTTP_USERNAME')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            print(permission)
            if permission == 'superadmin':
                all_test_record = TestRecord.objects.all()
                record_list = list()
                if all_test_record:
                    for record in all_test_record:
                        if record.end_time:
                            continue
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
                create_history_record(username, '查询正在测量的记录')
                return JsonResponse({
                    "error_no": 0,
                    "all_test_record": record_list,
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
                            if record.end_time:
                                continue
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
                    create_history_record(username, '查询正在测量的记录')
                    return JsonResponse({
                        "error_no": 0,
                        "all_test_record": record_list
                    })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户"
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
            username = request.META.get('HTTP_USERNAME')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            test_id = request.query_params.get('test_id')
            if permission == "superadmin":
                test_record = TestRecord.objects.get(id=test_id)
            else:
                company_id = user.company_id
                test_record = TestRecord.objects.get(id=test_id, company_id=company_id)

            delta = timedelta(hours=8)
            start_time = test_record.start_time
            end_time = test_record.end_time
            device_list_str = test_record.devices_id
            devices_list = device_list_str.split(',')

            sql = "select time,  GROUP_CONCAT(imei_id) as imeis, GROUP_CONCAT(speed) as speeds from  \
                data_info_locationinfo where imei_id in(" + device_list_str + ") \
                and time >='" + (start_time - delta).strftime("%Y%m%d%H%M%S") + "'  \
                and time <='" + (end_time - delta).strftime("%Y%m%d%H%M%S") + "'    \
                group by time order by time;"
            # print(sql)
            with connection.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                # print(data)
            sendlist = list()
            # for rec in data:
            #     dc = len(devices_list)
            #     sendrec = [""] * (dc + 1)
            #     rectime = rec[0] + delta
            #     recimeis = rec[1].split(',')
            #     recspeeds = rec[2].split(',')
            #     sendrec[0] = rectime
            #     cc = 0
            #     for dd in devices_list:
            #         ii = 0
            #         for im in recimeis:
            #             if dd == im:
            #                 sendrec[cc + 1] = str(float('%0.2f' % (float(recspeeds[ii]) * 0.5144444)))
            #             ii = ii + 1
            #         cc = cc + 1
            #     sendlist.append(sendrec)

            page = request.query_params.get('page', '1')
            count = request.query_params.get('count', 100)
            print(page)
            paginator = Paginator(data, count)
            try:
                data_page = paginator.page(page)
            except PageNotAnInteger:
                data_page = paginator.page(1)
            except EmptyPage:
                data_page = paginator.page(paginator.num_pages)
            for rec in data_page:
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
            create_history_record(username, '查询测量记录 %s 流速详情' % test_record.remarks)
            return JsonResponse({
                "error_no": 0,
                "all_test_record": sendlist,
                "start_time": start_time,
                "end_time": end_time,
                "total": paginator.num_pages
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户"
            })
        except TestRecord.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个记录"
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
            username = request.META.get('HTTP_USERNAME')
            user = UserProfile.objects.get(username=username)
            permission = user.permission
            test_id = request.query_params.get('test_id')
            if permission == "superadmin":
                test_record = TestRecord.objects.get(id=test_id)
            else:
                company_id = user.company_id
                test_record = TestRecord.objects.get(id=test_id, company_id=company_id)

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
                group by time order by time;"
            with connection.cursor() as cursor:
                cursor.execute(sql)
                data = cursor.fetchall()
                # print(data)
            sendlist = list()
            # for rec in data:
            #     sendrec = [""] * (len(devices_list) * 3 + 1)
            #     rectime = rec[0] + delta
            #     recimeis = rec[1].split(',')
            #     reclongitudes = rec[2].split(',')
            #     reclatitude = rec[3].split(',')
            #     recspeeds = rec[4].split(',')
            #     sendrec[0] = rectime
            #     cc = 1
            #     print(rec)
            #     for device in devices_list:
            #         ii = 0
            #         for imei in recimeis:
            #             if device == imei:
            #                 sendrec[cc], sendrec[cc + 1] = gps_conversion(str(reclongitudes[ii]), str(reclatitude[ii]))
            #                 sendrec[cc + 2] = str(float('%0.2f' % (float(recspeeds[ii]) * 0.5144444)))
            #                 print(reclongitudes[ii] + "," + reclatitude[ii] + "," + recspeeds[ii])
            #             ii = ii + 1
            #         cc = cc + 3
            #     print(sendrec)
            #     sendlist.append(sendrec)

            page = request.query_params.get('page', '1')
            count = request.query_params.get('count', 100)
            print(page)
            paginator = Paginator(data, count)
            try:
                data_page = paginator.page(page)
            except PageNotAnInteger:
                data_page = paginator.page(1)
            except EmptyPage:
                data_page = paginator.page(paginator.num_pages)
            for rec in data_page:
                sendrec = [""] * (len(devices_list) * 3 + 1)
                rectime = rec[0] + delta
                recimeis = rec[1].split(',')
                reclongitudes = rec[2].split(',')
                reclatitude = rec[3].split(',')
                recspeeds = rec[4].split(',')
                sendrec[0] = rectime
                cc = 1
                # print(rec)
                for device in devices_list:
                    ii = 0
                    for imei in recimeis:
                        if device == imei:
                            sendrec[cc], sendrec[cc + 1] = gps_conversion(str(reclongitudes[ii]), str(reclatitude[ii]))
                            sendrec[cc + 2] = str(float('%0.2f' % (float(recspeeds[ii]) * 0.5144444)))
                            # print(reclongitudes[ii] + "," + reclatitude[ii] + "," + recspeeds[ii])
                        ii = ii + 1
                    cc = cc + 3
                # print(sendrec)
                sendlist.append(sendrec)
            create_history_record(username, '查询测量记录 %s 经纬度详情' % test_record.remarks)
            return JsonResponse({
                "error_no": 0,
                "all_test_record": sendlist,
                "start_time": start_time,
                "end_time": end_time,
                "total": paginator.num_pages
            })
        except UserProfile.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个用户"
            })
        except TestRecord.DoesNotExist:
            return JsonResponse({
                "error_no": -2,
                "info": "没有这个记录"
            })
        except Exception as e:
            print(e)
            return JsonResponse({
                "error_no": -1,
                "info": str(e)
            })


class PointMapView(APIView):
    def get(self, request):
        lon, lat = request.query_params.get('lon'), request.query_params.get('lat')
        speed = request.query_params.get('speed')
        time = request.query_params.get('time')
        # print(lon, lat)
        return render(request, "point_map.html", {
            "lon": lon,
            "lat": lat,
            "speed": speed,
            "time": time,
        })


class RecordInfoModifyView(LoginRequiredMixin, View):
    """
    修改测量记录信息
    """

    def get(self, request, record_id):
        permission = request.user.permission
        print(permission)
        if permission == 'superadmin':
            record_info = TestRecord.objects.get(id=record_id)
            devices = DevicesInfo.objects.all().values()
            for i in devices:
                i['id'] = str(i['id'])
            return render(request, "record_modify.html", {
                "record_info": record_info,
                "devices": devices,
            })
        else:
            try:
                company_id = request.user.company.id
                record_info = TestRecord.objects.get(id=record_id, company_id=company_id)
                devices = DevicesInfo.objects.all().values()
                for i in devices:
                    i['id'] = str(i['id'])
                return render(request, "record_modify.html", {
                    "record_info": record_info,
                    "devices": devices,
                })

            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('select2_device'))

    def post(self, request, record_id):
        record_info = TestRecord.objects.get(id=record_id)
        request_post = request.POST.copy()
        devices_id_list = request_post.getlist('devices_id')
        request_post['devices_id'] = ",".join(devices_id_list)
        # print(request_post)
        record_form = TestRecordForm(request_post, instance=record_info)
        if record_form.is_valid():
            record_form.save()
            create_history_record(request.user, '修改测量记录 %s 的信息 为 %s ' % (record_info.remarks, request.POST.get('remarks')))
            return JsonResponse({"status": "success"})
        return JsonResponse({
            "status": "fail"
        })


class CalculateFlowTrackView(LoginRequiredMixin, View):
    """
    轨迹回放
    """

    def get(self, request, imei_id, start_time, end_time):
        # now_time = datetime.now()
        # start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)

        permission = request.user.permission
        print(permission)
        if permission == "superadmin":
            location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2,
                                                   time__lte=end_time2).order_by('time')
        else:
            try:
                device = DevicesInfo.objects.filter(id=imei_id)
                company = request.user.company.company_name
                device_company = device[0].company.company_name
            except TestRecord.DoesNotExist as e:
                return HttpResponseRedirect(reverse('select_device'))
            if company and device and device_company == company:
                location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2,
                                                       time__lte=end_time2).order_by('time')
            else:
                return HttpResponseRedirect(reverse('select_device'))
        json_list = list()
        location_list = list()
        speed_list = list()
        dict_path = dict()
        if len(location) > 0:
            dict_path["name"] = location[0].imei.desc
            for i in location:
                if i.longitude and i.latitude:
                    longitude, latitude = gps_conversion(i.longitude, i.latitude)
                    location_list.append([longitude, latitude])
                    speed_list.append([(i.time + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"), float(i.speed) * 0.5144444])

            dict_path["path"] = location_list
            dict_path["speed"] = speed_list
            json_list.append(dict_path)
        if location:
            s_e_point = gps_conversion(location[0].longitude, location[0].latitude)
        else:
            s_e_point = [106.53233, 29.522584]
        return render(request, 'flow_track.html', {
            "json_data": json_list, "s_e_point": s_e_point
        })
