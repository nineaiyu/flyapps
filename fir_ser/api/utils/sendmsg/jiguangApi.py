#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/22

import requests
import json


class JiGuangMsgSender(object):
    BASE_URL = 'https://api.sms.jpush.cn/v1/'

    def __init__(self, app_key, master_secret, sign_id, template_code):
        self.template_code = template_code
        self.sign_id = sign_id
        self.session = requests.Session()
        self.session.auth = (app_key, master_secret)

    def _post(self, end_point, body):
        return self._request('POST', end_point, body)

    def _request(self, method, end_point, body=None):
        uri = self.BASE_URL + end_point
        if body is not None:
            body = json.dumps(body)
        r = self.session.request(method, uri, data=body)
        if 0 == len(r.content):
            return r.status_code
        else:
            return r.json()

    def send_msg(self, template_code, phone, code):
        body = {
            'mobile': phone,
            'temp_id': template_code,
            'temp_para': {'code': code},
            'sign_id': self.sign_id
        }
        response = self._post('messages', body)
        if response.get('msg_id', None):
            return True, response.get('msg_id')
        else:
            return False, response.get('error')

    def send_msg_by_act(self, phone, code, act):
        if act not in self.template_code.keys():
            return False, f'act {act} not found'
        return self.send_msg(self.template_code.get(act), phone, code)
