import base64
import urllib.parse


def push_xml_to_sx_services(sbbh, hphm, wfsj="", wfdz="", hpzl="", wfxw="", zpstr1="", zpstr2=""):
    """
    :param sbbh: 设备编号 320200000000020001
    :param hphm: 号牌号码
    :param wfsj: 违法时间
    :param wfdz: 违法地址
    :param hpzl: 号牌种类
    :param wfxw: 违法行为
    :param zpstr1: 照片1 不能为空
    :param zpstr2: 照片2
    :return:
    """
    xml = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>"]
    xml.append("<root><surscreen>")
    xml.append("<sbbh>%s</sbbh>" % sbbh)
    xml.append("<wfsj>%s</wfsj>" % wfsj)
    xml.append("<wfdz>%s</wfdz>" % urllib.parse.quote(wfdz))
    xml.append("<hpzl>%s</hpzl>" % hpzl)
    xml.append("<zqmj>308437</zqmj>")
    xml.append("<clfl>3</clfl>")
    xml.append("<wfxw>%s</wfxw>" % wfxw)
    xml.append("<zpsl>2</zpsl>")
    xml.append("<hphm>%s</hphm>" % urllib.parse.quote(hphm))
    xml.append("<zpstr1>%s</zpstr1>" % urllib.parse.quote(zpstr1, safe=''))
    # xml.append("<zpstr1>%s</zpstr1>" % zpstr1)
    xml.append("<zpstr2>%s</zpstr2>" % urllib.parse.quote(zpstr2, safe=''))
    # xml.append("<zpstr2>%s</zpstr2>" % zpstr2)
    xml.append("</surscreen></root>")
    xml_doc = ''.join(xml)
    # print(xml_doc)
    return xml_doc


if __name__ == '__main__':
    f = open("G:\dzt\资料\交警\测试文件夹\\1039_20190426_230146_021_50.45.11.233_川C3D220_0_10395_蓝.jpg",
             'rb')
    f1 = open("G:\dzt\资料\交警\测试文件夹\\2_20190604_080238_983_50.45.6.119_渝A12345_0_1039_蓝_短信.jpg",
              'rb')
    qz_image = base64.b64encode(f.read())
    sms_image = base64.b64encode(f1.read())
    xml = push_xml_to_sx_services("320200000000020001", "渝DJD020", "2019-09-02 17:52:39", "杨家坪", "02", "10395",
                                  qz_image.decode(), sms_image.decode())
    f.close()
    print(xml)
    f2 = open('test3.xml', 'w')
    f2.write(xml)
