from django.shortcuts import render
from django.views import View
from myutils.mixin_utils import LoginRequiredMixin
from datetime import datetime, timedelta
from myutils.utils import create_history_record, gps_amap, gps_conversion
from .models import LocationInfo, TXT
from devices.models import DevicesInfo
from django.http import JsonResponse, HttpResponseRedirect
from .forms import TXTInfoForm, LocationInfoSerializer
from rest_framework.views import APIView
from django.core.urlresolvers import reverse
from river_ball.settings import MEDIA_ROOT
import os


class SelectDevice(LoginRequiredMixin, View):
    def get(self, request):
        all_devices = DevicesInfo.objects.all()
        return render(request, 'select_device.html', {
            "all_devices": all_devices
        })


class LocationInfoView(LoginRequiredMixin, View):
    def get(self, request, imei_id):
        now_time = datetime.now()
        start_time = datetime.strftime(now_time, '%Y-%m-%d') + " 00:00:00"
        location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time,
                                                     time__lte=now_time).order_by('-time')
        if location_infos:
            imei = location_infos[0].imei.imei
            create_history_record(request.user, '查询设备号%s数据' % imei)
            a = location_infos.values()
            for i in a:
                i['imei'] = imei
                i['speed'] = float(i['speed']) * 0.5144444
            print(a)
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
        location_infos = LocationInfo.objects.filter(imei__id=imei_id, time__gte=start_time,
                                                     time__lte=end_time).order_by('-time')
        if location_infos:
            create_history_record(request.user, '查询设备号%s数据' % location_infos[0].imei.imei)
        return render(request, 'location_infos.html', {
            "imei_id": imei_id,
            "location_data": location_infos,
            "start_time": start_time,
            "end_time": end_time
        })


# 设备信息上传
class UploadLocationInfoView(APIView):
    def post(self, request):
        try:
            imei = request.data.get('imei')
            imei_id = DevicesInfo.objects.get(imei=imei).id
            request.data['imei'] = imei_id
            print(request.data)
            location_sers = LocationInfoSerializer(data=request.data)
            if location_sers.is_valid():
                location_sers.save()
                return JsonResponse({"status": "success"})
            print(location_sers.errors)
            return JsonResponse({"status": "fail", "errors": str(location_sers.errors)})
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
        location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time, time__lte=now_time).order_by(
            'time')
        deivce = DevicesInfo.objects.filter(id=imei_id)
        if deivce:
            imei = deivce[0].imei
        else:
            imei = ""
        for i in location:
            time_list.append(datetime.strftime(i.time + timedelta(hours=8), '%Y%m%d %H:%M:%S'))
            # time_list.append("")
            print(i.speed)
            speed_list.append(float(i.speed) * 0.5144444)
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
        end_time = request.POST.get('end_time', '')
        location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time, time__lte=end_time).order_by(
            'time')
        deivce = DevicesInfo.objects.filter(id=imei_id)
        if deivce:
            imei = deivce[0].imei
        else:
            imei = ""
        for i in location:
            time_list.append(datetime.strftime(i.time + timedelta(hours=8), '%Y%m%d %H:%M:%S'))
            speed_list.append(float(i.speed) * 0.5144444)
        print(time_list)
        print(speed_list)
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
        print(start_time)
        print(end_time)
        location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time, time__lte=end_time).order_by(
            'time')
        lng = list()
        lat = list()
        for i in location:
            longitude, latitude = gps_conversion(i.longitude, i.latitude)
            lng.append(longitude)
            lat.append(latitude)
        return render(request, 'track.html', {
            "lng": lng, "lat": lat
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
        path2 = MEDIA_ROOT + "\\" + str(file.filename)
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
            src_filename = MEDIA_ROOT + "\\" + str(filename)
            if os.path.exists(src_filename):
                os.remove(src_filename)
                print('del %s ok' % src_filename)
                return JsonResponse({"status": "success"})
        except Exception as e:
            print(e)
            return JsonResponse({"status": "fail", 'msg': "删除失败"})
