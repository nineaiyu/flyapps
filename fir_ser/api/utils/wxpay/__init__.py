#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2021/4/15

import socket
import time
import uuid
import hashlib
import xml.etree.ElementTree as ET
import requests


def get_nonce_str():
    """
    获取随机字符串
    :return:
    """
    return str(uuid.uuid4()).replace('-', '')


def dict_to_order_xml(dict_data):
    """
    dict to order xml
    ASCII码从小到大排序
    :param dict_data:
    :return:
    """
    xml = ["<xml>"]
    for k in sorted(dict_data):
        xml.append("<{0}>{1}</{0}>".format(k, dict_data.get(k)))
    xml.append("</xml>")
    return "".join(xml)


def dict_to_xml(dict_data):
    xml = ["<xml>"]
    for k, v in dict_data.items():
        xml.append("<{0}>{1}</{0}>".format(k, v))
    xml.append("</xml>")
    return "".join(xml)


def xml_to_dict(xml_data):
    """
    xml to dict
    :param xml_data:
    :return:
    """
    xml_dict = {}
    root = ET.fromstring(xml_data)
    for child in root:
        xml_dict[child.tag] = child.text
    return xml_dict


class WxPay(object):
    """
    https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=7_4&index=3
    """

    def __init__(self, app_id, mch_id, notify_url, merchant_key):
        self.url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/native'
        self.app_id = app_id  # 微信分配的小程序ID
        self.mch_id = mch_id  # 商户号
        self.notify_url = notify_url  # 通知地址
        self.spbill_create_ip = socket.gethostbyname(socket.gethostname())  # 获取本机ip
        self.merchant_key = merchant_key  # 商户KEY，修改为自己的

    def create_sign(self, pay_data):
        """
        生成签名
        https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=4_3
        :param pay_data:
        :return:
        """

        # 拼接stringA
        string_a = '&'.join(["{0}={1}".format(k, pay_data.get(k)) for k in sorted(pay_data)])
        # 拼接key
        string_sign_temp = '{0}&key={1}'.format(string_a, self.merchant_key).encode('utf-8')
        # md5签名
        sign = hashlib.md5(string_sign_temp).hexdigest()
        return sign.upper()

    def get_pay_info(self, pay_data):
        """
        支付统一下单
        :return:
        """
        # 调用签名函数

        post_data = {
            'appid': self.app_id,  # 小程序ID
            'mch_id': self.mch_id,  # 商户号
            'description': pay_data.get('description'),  # 商品描述
            'out_trade_no': pay_data.get('out_trade_no'),  # 商户订单号
            'time_expire': pay_data.get('time_expire'),  # 交易结束时间 示例值：2018-06-08T10:34:56+08:00
            'attach': pay_data.get('attach'),  # 附加数据，在查询API和支付通知中原样返回，可作为自定义参数使用
            'notify_url': self.notify_url,  # 通知地址
            'amount': {
                'total': pay_data.get('total'),  # 订单总金额，单位为分。示例值：100
                'currency': 'CNY'
            }
        }
        sign = self.create_sign(post_data)
        post_data['sign'] = sign

        xml = dict_to_xml(post_data)

        # 统一下单接口请求
        r = requests.post(self.url, data=xml.encode("utf-8"))
        r.encoding = "utf-8"
        res = xml_to_dict(r.text)
        err_code_des = res.get('err_code_des')
        # 出错信息
        if err_code_des:
            return {'code': 40001, 'msg': err_code_des}
        prepay_id = res.get('prepay_id')

        return self.re_sign(post_data, prepay_id)

    def re_sign(self, post_data, prepay_id):
        """
        再次对返回的数据签名
        https://pay.weixin.qq.com/wiki/doc/api/wxa/wxa_api.php?chapter=7_7&index=3
        :param post_data:
        :param prepay_id:
        :return:
        """
        pay_sign_data = {
            'appId': self.app_id,  # 注意大小写与统一下单不一致
            'timeStamp': post_data.get('out_trade_no'),
            'nonceStr': post_data.get('nonce_str'),
            'package': 'prepay_id={0}'.format(prepay_id),
            'signType': 'MD5',
        }
        pay_sign = self.create_sign(pay_sign_data)
        pay_sign_data['paySign'] = pay_sign
        return pay_sign_data
