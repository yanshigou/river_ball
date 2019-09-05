from django.shortcuts import render
from django.views import View
from myutils.mixin_utils import LoginRequiredMixin
from datetime import datetime
from myutils.utils import create_history_record
from .models import LocationInfo
from devices.models import DevicesInfo
from django.http import JsonResponse
from .forms import LocationInfoForm, LocationInfoSerializer
from rest_framework.views import APIView


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
            create_history_record(request.user, '查询设备号%s数据' % location_infos[0].imei.imei)
        return render(request, 'location_infos.html', {
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
        location = LocationInfo.objects.filter(imei_id=imei_id, time__gte=start_time, time__lte=now_time).order_by('-time')
        for i in location:
            time_list.append(datetime.strftime(i.time, '%Y%m%d %H:%M:%S'))
            speed_list.append(i.speed)
        print(time_list)
        print(speed_list)
        create_history_record(request.user, '查看图形统计')
        return render(request, 'statistical_one.html', {
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
        district_val = request.POST.get('district', '')
        area_val = request.POST.get('area', '')
        address = request.POST.getlist('address', '')
        # car_type = request.POST.get('car_type', '')
        # sms = request.POST.get('sms', '')
        # rk = request.POST.get('rk', '')
        start_time = request.POST.get('start_time', '')
        end_time = request.POST.get('end_time', '')
        car_id = request.POST.get('car_id', '')
        # print(district_val)
        # print(area_val)
        # print(address)
        # print(car_type)
        # print(sms)
        # print(rk)
        # print(start_time)
        # print(end_time)
        # print(car_id)
        print(district_val)
        print(area_val)
        print(address)
        if len(address) < 2:
            address = request.POST.get('address', '')
            address = address.split(',')
            print(address)
            print(type(address))
        else:
            address = ",".join(address)
            address = list(set(address.split(',')))
            print('address', address)
            print(type(address))

        all_wt_data = WTDataInfo.objects.filter(wf_time__gte=start_time, wf_time__lte=end_time).order_by('-wf_time')
        if district_val != '全部区域':
            all_wt_data = all_wt_data.filter(ip__district=district_val)
            district_text = DistrictInfo.objects.get(id=district_val).district
            area_list = AreaInfo.objects.filter(district_id=district_val)
        else:
            district_val = '全部区域'
            district_text = "全部区域"
            area_list = ""

        if area_val != '全部片区':
            if area_val != '全部片区':
                if not area_val.isdigit():
                    return HttpResponseRedirect(reverse("WT_statistical"))
            all_wt_data = all_wt_data.filter(ip__area=area_val)
            area_text = AreaInfo.objects.get(id=area_val).area
            address_list = DevicesInfo.objects.filter(area_id=area_val)
        else:
            area_val = '全部片区'
            area_text = '全部片区'
            address_list = ""
        if address != [''] and ("全部地址" not in address or len(address) >= 2):
            if "全部地址" in address:
                address.remove('全部地址')
            all_wt_data = all_wt_data.filter(ip__address__in=address)
            address_val = ",".join(address)
        else:
            address_list = DevicesInfo.objects.all().values('address')
            address = '全部地址'
            address_val = '全部地址'

        district = DistrictInfo.objects.all()

        # if car_type != '全部车型':
        #     all_wt_data = all_wt_data.filter(car_type=car_type)
        # if sms != '全部选项':
        #     all_wt_data = all_wt_data.filter(sms_result__contains=sms)
        # if rk != '全部选项':
        #     all_wt_data = all_wt_data.filter(push_result__contains=rk)
        # if car_id != '':
        #     all_wt_data = all_wt_data.filter(car_id__icontains=car_id)

        print(all_wt_data)

        all_address = []
        all_address_count = []
        all_address_count2 = []
        all_address_count3 = []
        all_address_count4 = []
        if address != '全部地址':
            all_address_set = DevicesInfo.objects.filter(address__in=address).values('address')
            for i in address:
                if i == "全部地址":
                    continue
                all_address.append(i)
                count = all_wt_data.filter(ip__address=i).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                count2 = all_wt_data.filter(ip__address=i).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).exclude(
                    Q(image="") | Q(image__isnull=True)).count()
                count3 = all_wt_data.filter(ip__address=i).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).exclude(
                    Q(sms_image="") | Q(sms_image__isnull=True)).count()
                count4 = all_wt_data.filter(ip__address=i, push_result="成功").exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                all_address_count.append(count)
                all_address_count2.append(count2)
                all_address_count3.append(count3)
                all_address_count4.append(count4)
        elif (address == '全部地址' or address == "") and area_val != '全部片区':
            all_address_set = DevicesInfo.objects.filter(area_id=area_val).values('address')
            for i in all_address_set:
                if i['address'] == "全部地址":
                    continue
                all_address.append(i['address'])
                count = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                count2 = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).exclude(
                    Q(image="") | Q(image__isnull=True)).count()
                count3 = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).exclude(
                    Q(sms_image="") | Q(sms_image__isnull=True)).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                count4 = all_wt_data.filter(ip__address=i['address'], push_result="成功").exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                all_address_count.append(count)
                all_address_count2.append(count2)
                all_address_count3.append(count3)
                all_address_count4.append(count4)
        elif (address == '全部地址' or address == "") and area_val == '全部片区' and district_val != "全部区域":
            all_address_set = DevicesInfo.objects.filter(district_id=district_val).values('address')
            for i in all_address_set:
                if i['address'] == "全部地址":
                    continue
                all_address.append(i['address'])
                count = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                count2 = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).exclude(
                    Q(image="") | Q(image__isnull=True)).count()
                count3 = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).exclude(
                    Q(sms_image="") | Q(sms_image__isnull=True)).count()
                count4 = all_wt_data.filter(ip__address=i['address'], push_result="成功").exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                all_address_count.append(count)
                all_address_count2.append(count2)
                all_address_count3.append(count3)
                all_address_count4.append(count4)
        else:
            all_address_set = DevicesInfo.objects.all().values('address')
            for i in all_address_set:
                all_address.append(i['address'])
                if i['address'] == "全部地址":
                    continue
                count = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                count2 = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).exclude(
                    Q(image="") | Q(image__isnull=True)).count()
                count3 = all_wt_data.filter(ip__address=i['address']).exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).exclude(
                    Q(sms_image="") | Q(sms_image__isnull=True)).count()
                count4 = all_wt_data.filter(ip__address=i['address'], push_result="成功").exclude(
                    Q(event_image="") | Q(event_image__isnull=True)).count()
                all_address_count.append(count)
                all_address_count2.append(count2)
                all_address_count3.append(count3)
                all_address_count4.append(count4)
        create_history_record(request.user, '违停数据统计查询')
        return render(request, 'wt_statistical2.html', {
            "all_wt_datas": all_wt_data,
            "all_address": all_address,
            "all_address_count": all_address_count,
            "all_address_count2": all_address_count2,
            "all_address_count3": all_address_count3,
            "all_address_count4": all_address_count4,
            "district_list": district,
            "district_val": district_val,
            "district_text": district_text,
            "area_list": area_list,
            "area_val": area_val,
            "area_text": area_text,
            "address_list": all_address_set,
            "address": address,
            "address_val": address_val,
            # "car_types_data": [
            #     {"value": '全部车型', "label": "全部车型"},
            #     {"value": '01', "label": "大型汽车"},
            #     {"value": '02', "label": "小型汽车"},
            #     {"value": '03', "label": "使馆汽车"},
            #     {"value": '04', "label": "领馆汽车"},
            #     {"value": '05', "label": "境外汽车"},
            #     {"value": '06', "label": "外籍汽车"},
            #     {"value": '07', "label": "普通摩托车"},
            #     {"value": '08', "label": "轻便摩托车"},
            #     {"value": '09', "label": "使馆摩托车"},
            #     {"value": '10', "label": "领馆摩托车"},
            #     {"value": '11', "label": "境外摩托车"},
            #     {"value": '12', "label": "外籍摩托车"},
            #     {"value": '13', "label": "低速车"},
            #     {"value": '14', "label": "拖拉机"},
            #     {"value": '15', "label": "挂车"},
            #     {"value": '16', "label": "教练汽车"},
            #     {"value": '17', "label": "教练摩托车"},
            #     {"value": '18', "label": "试验汽车"},
            #     {"value": '19', "label": "新能源汽车"},
            # ],
            # "car_types_condition": [car_type],
            # "car_types_condition_val": [car_type],
            # "sms_data": [
            #     {"value": '全部选项', "label": "全部选项"},
            #     {"value": '成功', "label": "成功"},
            #     {"value": '失败', "label": "失败"},
            #     {"value": '超时', "label": "超时"},
            #     # {"value": '非', "label": "非【渝】车牌"},
            #
            # ],
            # "sms_condition": [sms],
            # "sms_condition_val": [sms],
            # "rk_data": [
            #     {"value": '全部选项', "label": "全部选项"},
            #     {"value": '成功', "label": "成功"},
            #     {"value": '失败', "label": "失败"},
            #     {"value": '暂未入库', "label": "暂未入库"},
            #     # {"value": '非', "label": "非入库对象"},
            # ],
            # "rk_condition": [rk],
            # "rk_condition_val": [rk],
            "start_time": start_time,
            "end_time": end_time,
            "car_id": car_id
        })