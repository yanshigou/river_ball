# -*- coding: utf-8 -*-
__author__ = "dzt"
__date__ = "2019/6/24"
from datetime import datetime
import xml.etree.ElementTree as ET
from suds.client import Client
import urllib
import base64

jkxlh_02 = "7A1E1D0C030703050915020100020902000608000401178BA5356D72692E636E"
jkxlh_01 = "7A1E1D0C030703050915020100020902000608000401178BA5356D72692E636E"  # 测试接口序列号
endpoint = "http://50.1.26.84:9084/rminf/services/RmOutAccess?wsdl"  # 其他基础数据 测试接口
methodName = "writeObjectOut"
methodName2 = "queryObjectOut"

rminf = 'http://50.1.26.84:9084/rminf'  # 暂未知


# 向集成平台推送 非现场违法待筛选写入
def push_xml_to_sx_services(sbbh, hphm, zpstr1="", zpstr2=""):
    """
    :param sbbh: 设备编号 320200000000020001
    :param zpsl: 照片数量
    :param hphm: 号牌号码
    :param zpstr1: 照片1 不能为空
    :param zpstr2: 照片2
    :param zpstr3: 照片3
    :return:
    """
    xml = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>"]
    xml.append("<root><surscreen>")
    xml.append("<sbbh>%s</sbbh>" % sbbh)
    xml.append("<zpsl>2</zpsl>")
    xml.append("<hphm>%s</hphm>" % urllib.parse.quote(hphm))
    xml.append("<zpstr1>%s</zpstr1>" % zpstr1)
    xml.append("<zpstr2>%s</zpstr2>" % zpstr2)
    xml.append("<zpstr3></zpstr3>")
    xml.append("</surscreen></root>")

    xml_doc = ''.join(xml)
    # print(xml_doc)
    client = Client(endpoint)
    res = client.service.writeObjectOut("60", jkxlh_01, "60W01", xml_doc)
    return res


# 向集成平台推送 非现场违法待审核写入
def push_xml_to_sh_services(sbbh, clfl, hpzl, hphm, wfsj, wfxw, zpsl, zpstr1="", zpstr2="", zpstr3=""):
    """
    :param sbbh: 设备编号 320200000000020001
    :param clfl: 车辆分类 3
    :param hpzl: 号牌种类
    :param hphm: 号牌号码
    :param wfsj: 违法时间
    :param wfxw: 违法行为
    :param zpsl: 照片数量
    :param zpstr1: 照片1 不能为空
    :param zpstr2: 照片2
    :param zpstr3: 照片3
    :return:
    """
    xml = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>"]
    xml.append("<root><surexamine>")
    xml.append("<sbbh>%s</sbbh>" % urllib.parse.quote(sbbh))
    xml.append("<clfl>%s</clfl>" % urllib.parse.quote(clfl))
    xml.append("<hpzl>%s</hpzl>" % urllib.parse.quote(hpzl))
    xml.append("<hphm>%s</hphm>" % urllib.parse.quote(hphm))
    xml.append("<wfsj>%s</wfsj>" % wfsj)
    xml.append("<wfxw>%s</wfxw>" % urllib.parse.quote(wfxw))
    xml.append("<zpsl>%s</zpsl>" % urllib.parse.quote(zpsl))
    xml.append("<zpstr1>%s</zpstr1>" % zpstr1)
    xml.append("<zpstr2>%s</zpstr2>" % zpstr2)
    xml.append("<zpstr3>%s</zpstr3>" % zpstr3)
    xml.append("</surexamine></root>")

    xml_doc = ''.join(xml)
    # print(xml_doc)
    client = Client(endpoint)
    res = client.service.writeObjectOut("60", jkxlh_02, "60W02", xml_doc)
    return res


def xml_to_dict(xml_str):
    result = dict()
    xml = ET.fromstring(xml_str)
    for table in xml.getiterator('head'):
        for child in table:
            # print(child.tag, child.text)
            if child.text:
                result[child.tag] = urllib.parse.unquote(child.text)
    return result


if __name__ == '__main__':
    hphm = "渝DJD020"
    f = open('D:\\traffic\\traffic_mgmt\\apps\\myutils\\1039_20190604_080238_983_50.45.6.119_渝DJD020_0_1039_蓝.jpg', 'rb')
    f2 = open('D:\\traffic\\traffic_mgmt\\apps\\myutils\\1039_20190604_080238_983_50.45.6.119_渝DJD020_0_1039_蓝_短信.jpg', 'rb')
    # f = open('G:\\dzt\\traffic_mgmt\\apps\\myutils\\1039_20190604_080238_983_50.45.6.119_渝DJD020_0_1039_蓝.jpg', 'rb')
    # f2 = open('G:\\dzt\\traffic_mgmt\\apps\\myutils\\1039_20190604_080238_983_50.45.6.119_渝DJD020_0_1039_蓝_短信.jpg', 'rb')
    qzimage = base64.b64encode(f.read())
    dximage = base64.b64encode(f2.read())

    f.close()
    f2.close()


    # res = push_xml_to_sh_services("501300000000048235", "3", hpzl, hphm, date, '1039', '2', qzimage, dximage, eventimage)
    res = push_xml_to_sx_services("501300000000048235", hphm, qzimage, dximage)
    print(res)
    res_dict = xml_to_dict(res)
    print(res_dict)

