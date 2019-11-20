# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/9/5"
import requests
import json
import base64


def test():
    url = 'http://192.168.31.54:8000/dataInfo/upload/'
    data_dict = {
        "imei": "13370763530",
        "time": "2019-09-05 17:32:18",
        "up_time": "2019-09-05 17:32:18",
        "longitude": "106.52533",
        "latitude": "29.51934",
        "altitude": "1",
        "speed": "253",
        "direction": "1",
        "accuracy": "1",
        "power": "1",
        "satellites": "1",
        "real_satellites": "1"
    }
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, data=json.dumps(data_dict), headers=headers)
    print(res)
    print(res.json())


IS_DEBUG_JPUSH = True
jpushurl = "https://api.jpush.cn/v3/push"
jpush_appkey = "e1b7e3c9f81b8b8ba1878f5a"
jpush_master_secret = "89964f45f3007a8b696df6b5"


def jpush_function_extra(username, kind, summary, content):
    """
    :param username: 别名
    :param kind: 定义类型（1-预警速度）
    :param summary: 通知标题
    :param content: 通知内容
    :return:
    """
    base64_auth_string = base64.b64encode((jpush_appkey + ":" + jpush_master_secret).encode("utf-8"))
    # print(base64_auth_string)
    # print(str(base64_auth_string, 'utf-8'))
    headers = {'content-type': 'application/json', "Authorization": "Basic " + str(base64_auth_string, 'utf-8')}
    msg = {
        "platform": "all",
        "audience":
            {"alias": [username]}
        ,
        "notification": {
            "ios": {
                "alert": summary,
                "sound": "default",
                # "badge": "+1",
                "content-available": True,
                "extras": {
                    "kind": kind,
                    "content": content
                }
            },
            "android": {
                "alert": summary,
                # "title": "智守护",
                "builder_id": 1,
                "extras": {
                    "kind": kind,
                    "content": content
                }
            }
        },
        "options": {
            "apns_production": IS_DEBUG_JPUSH,
            "apns_collapse_id": "cmx"
        }
    }
    return requests.post(jpushurl, data=json.dumps(msg), headers=headers)


if __name__ == '__main__':
    res = jpush_function_extra("13883562563", "1", "预警速度测试", "预警速度测试内容")
    print(res)
    print(res.json())
