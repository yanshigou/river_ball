from django.shortcuts import render
from django.views import View
from myutils.mixin_utils import LoginRequiredMixin
from datetime import datetime, timedelta
from myutils.utils import create_history_record, gps_amap, gps_conversion, check_one_net_data, export_excel
from .models import LocationInfo, TXT, DevicesOneNetInfo
from devices.models import DevicesInfo
from django.http import JsonResponse, HttpResponseRedirect
from .forms import TXTInfoForm, LocationInfoSerializer, DevicesInfoSerializer
from rest_framework.views import APIView
from django.core.urlresolvers import reverse
from river_ball.settings import MEDIA_ROOT
import os
import re
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class SelectDevice(LoginRequiredMixin, View):
    def get(self, request):
        all_devices = DevicesInfo.objects.all()
        return render(request, 'select_device.html', {
            "all_devices": all_devices
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
        now_time = datetime.now().replace(microsecond=0)
        start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
        end_time = now_time + timedelta(hours=-8)
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
        # try:
            start_time = request.POST.get('start_time', '')
            end_time = request.POST.get('end_time', '')
            imei_id = request.POST.get('imei_id', '')
            username = request.POST.get('username', '')
            start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time2,
                                                         time__lte=end_time2).order_by('-time')
            # all_count = location_infos.count()
            # page = all_count // 20
            # if page <= 1:
            #     page = 1
            # else:
            #     page += 1
            # print('count', all_count)
            # print('count2', page)
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
        # except Exception as e:
        #     print(e)
        #     return JsonResponse({
        #         "error_no": -1,
        #         "info": str(e)
        #     })


class AppExportLocationInfoView(View):
    def post(self, request):
        try:
            start_time = request.POST.get('start_time', '')
            end_time = request.POST.get('end_time', '')
            imei_id = request.POST.get('imei_id', '')
            print(start_time)
            print(end_time)
            print(imei_id)
            start_time2 = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            end_time2 = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") + timedelta(hours=-8)
            print(start_time2)
            print(end_time2)
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
                    print("excel")
                    print(location_datas)
                    now = datetime.now()
                    name = datetime.strftime(now, '%m-%d-%H-%M-%S')
                    filename = 'media/excel/流速球数据' + name + '.xlsx'
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
            print(location_sers.errors)
            return JsonResponse({"status": "fail", "errors": str(location_sers.errors)})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "error", "error": str(e)})


# OneNet回传信息
class OneNetDataView(APIView):
    def post(self, request):
        try:
            print("oneNet")
            # print(request.data)
            current_data = request.data.get('current_data')[0]
            dev_id = current_data.get('dev_id')
            one_net = DevicesOneNetInfo.objects.filter(dev_id=dev_id)
            if one_net:
                imei_id = one_net[0].imei.id
            else:
                return JsonResponse({"status": "error", "error": 'device not exist'})
            user_id = current_data.get('user_id')
            ds_id = current_data.get('ds_id')
            value = current_data.get('value')
            up_time = current_data.get('at')
            if ds_id == 'liusuqiu':
                re_data_list = re.findall(r"\$GNRMC[^#]*##\$GNGGA[^#]*##[^#]*##", value, re.S)
                print('re_data_list', re_data_list)
                if re_data_list:
                    for v in re_data_list:
                        data_list = v.split('##')
                        print('data_list', data_list)
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
                            print(location_sers.errors)
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
        location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time2, time__lte=end_time2).order_by(
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
            print(s_e_point)
        else:
            s_e_point = [106.53233, 29.522584]
        return render(request, 'track.html', {
            "lng": lng, "lat": lat, "s_e_point": s_e_point
        })


class UploadTXT(LoginRequiredMixin, View):
    """
    上传GPS文件
    """

    def get(self, request):
        form = TXTInfoForm()
        return render(request, 'upload.html', {"form": form})

    def post(self, request):
        form = TXTInfoForm(request.POST, request.FILES)
        if form.is_valid():
            # 获取表单数据
            info = form.cleaned_data['info']
            filename = form.cleaned_data['filename']
            time = datetime.now()

            f = TXT()
            f.filename = filename
            f.info = info
            f.starttime = time
            f.save()
            return HttpResponseRedirect(reverse("uploaded"))
        return HttpResponseRedirect(reverse("uploadTXT"))


class Uploaded(LoginRequiredMixin, View):
    def get(self, request):
        all_txt = TXT.objects.all()
        return render(request, 'uploaded.html', {
            'all_txt': all_txt
        })


class ShowTXTView(LoginRequiredMixin, View):
    """
    GPS文件轨迹展示
    """

    def get(self, request, file_id):
        file = TXT.objects.get(id=file_id)
        path2 = MEDIA_ROOT + "/" + str(file.filename)
        print(path2)
        lng = []
        lat = []
        locations = []
        if os.path.exists(path2):
            f = open(path2, "r")
            for line in f.readlines():
                arrline = line.split("  ")
                lnglat = [float(arrline[1]), float(arrline[2])]
                locations.append(lnglat)
            f.close()
            print(len(locations))
            # 批量转换经纬度 个数限制
            if len(locations) <= 40:
                res = gps_amap(locations)
                print(res.json())
                if res.status_code != 200:
                    return JsonResponse({"status": "fail"})
                amap_locations = res.json().get('locations')
                str_locations = amap_locations.split(";")
                for x in str_locations:
                    lnglat = x.split(",")
                    lng.append(float(lnglat[0]))
                    lat.append(float(lnglat[1]))
                return render(request, 'track.html', {"lng": lng, "lat": lat})
            for i in range(40, len(locations), 40):
                res = gps_amap(locations[i - 40:i])
                if res.status_code != 200:
                    break
                amap_locations = res.json().get('locations')
                str_locations = amap_locations.split(";")
                for x in str_locations:
                    lnglat = x.split(",")
                    lng.append(float(lnglat[0]))
                    lat.append(float(lnglat[1]))
            return render(request, 'track.html', {"lng": lng, "lat": lat})

        # return render(request, 'point.html', {"lng": lng, "lat": lat})
        return JsonResponse({"status": "fail"})


# 删除文件
class DelFile(LoginRequiredMixin, View):
    def post(self, request):
        try:
            file_id = request.POST.get('file_id')
            txt = TXT.objects.get(id=file_id)
            filename = txt.filename
            txt.delete()
            print(filename)
            src_filename = MEDIA_ROOT + "/" + str(filename)
            if os.path.exists(src_filename):
                os.remove(src_filename)
                print('del %s ok' % src_filename)
                return JsonResponse({"status": "success"})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "fail", 'msg': "删除失败"})
