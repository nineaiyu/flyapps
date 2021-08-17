#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/22


from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json


class AliMsgSender(object):

    def __init__(self, access_key, secret_key, sing_name, template_code, region_id='cn-hangzhou'):
        self.regionid = region_id
        self.sing_name = sing_name
        self.template_code = template_code
        self.client = AcsClient(access_key, secret_key, region_id)

    def send_msg(self, template_code, phone, code):
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')
        request.add_query_param('RegionId', self.regionid)
        request.add_query_param('PhoneNumbers', phone)
        request.add_query_param('SignName', self.sing_name)
        request.add_query_param('TemplateCode', template_code)
        request.add_query_param('TemplateParam', {'code': code})
        response = self.client.do_action_with_exception(request)
        data = json.loads(response)
        if data.get('Code') == 'OK':
            return True, data.get('Message')
        else:
            return False, data.get('Message')

    def send_msg_by_act(self, phone, code, act):
        if act not in self.template_code.keys():
            return False, f'act {act} not found'
        return self.send_msg(self.template_code.get(act), phone, code)
