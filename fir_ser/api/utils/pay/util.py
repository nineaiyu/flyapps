#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2021/4/18

from fir_ser.settings import PAY_CONFIG
from api.utils.pay.ali import Alipay
from api.utils.pay.wx import Weixinpay


def get_pay_obj_form_name(pay_name):
    for pay_info in PAY_CONFIG:
        if pay_name == pay_info.get('NAME', '') and pay_info.get('ENABLED', False):
            auth_info = pay_info.get('AUTH', None)
            p_type = pay_info.get('TYPE', '')
            if auth_info:
                if p_type == 'ALI':
                    return Alipay(pay_name, p_type, auth_info)
                elif p_type == 'WX':
                    return Weixinpay(pay_name, p_type, auth_info)
                else:
                    pass


def get_enable_pay_choices():
    pay_choices = []
    for pay_info in PAY_CONFIG:
        if pay_info.get('ENABLED', False):
            pay_choices.append({'type': pay_info.get('TYPE'), 'name': pay_info.get('NAME', '')})
    return pay_choices


def get_payment_type(p_type):
    if p_type == 'ALI':
        return 1
    elif p_type == 'WX':
        return 0
