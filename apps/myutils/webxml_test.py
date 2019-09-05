# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/7/3"
import requests
import json
from datetime import datetime
import re
import xml.etree.ElementTree as ET
from suds.client import Client
from suds.xsd.doctor import ImportDoctor, Import

xml = ["<?xml version=\"1.0\" encoding=\"utf-8\"?>"]
"""
https://www.cnblogs.com/liulinghua90/p/5823021.html
"""

def xml_to_dict(xml_str):
    result = dict()
    xml = ET.fromstring(xml_str)
    for table in xml.getiterator('head'):
        for child in table:
            # print(child.tag, child.text)
            result[child.tag] = child.text
    return json.dumps(result)


if __name__ == '__main__':
    xml.append(
        "<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\"><soap:Body>")
    xml.append("<getMobileCodeInfo xmlns=\"http://WebXml.com.cn/\">")
    xml.append("<mobileCode>13370763530</mobileCode>")
    xml.append("<userID></userID>")
    xml.append("</getMobileCodeInfo>")
    xml.append("</soap:Body></soap:Envelope>")
    xml_doc = ''.join(xml)
    # print(xml_doc)
    SMS = Client('http://ws.webxml.com.cn/WebServices/MobileCodeWS.asmx?wsdl')
    print(SMS)
    print(SMS.service.getMobileCodeInfo('13370763530', ''))

    yzm = Client('http://www.webxml.com.cn/WebServices/RandomFontsWebService.asmx?wsdl')
    print(yzm)
    print(yzm.service.getCharFonts(2))
    print(yzm.service.getChineseFonts(2))

    qq = Client('http://www.webxml.com.cn/webservices/qqOnlineWebService.asmx?wsdl')
    print(qq)
    print(qq.service.qqCheckOnline('16546548'))

    tq = Client('http://www.webxml.com.cn/WebServices/IpAddressSearchWebService.asmx?wsdl')
    print(tq)
    print(tq.service.getCountryCityByIp('47.106.174.128'))

    user_url = "http://120.24.235.105:8080/finance-user_info-war-1.0/ws/financeUserInfoFacade.ws?wsdl"  # 这里是你的webservice访问地址
    client = Client(user_url)  # Client里面直接放访问的URL，可以生成一个webservice对象
    print(client)



