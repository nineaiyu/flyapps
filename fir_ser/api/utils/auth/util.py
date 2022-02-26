#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: liuyu
# date: 2022/2/7
import logging

from api.utils.auth.captcha import CaptchaAuth
from api.utils.auth.geetest import GeeTestAuth

logger = logging.getLogger(__name__)

"""
验证流程
微信公众号验证码，短信验证码，邮件验证码
图片验证码，mfa验证，最后将数据通过geetest验证发送到后台进验证
"""


class AuthInfo(object):
    def __init__(self, captcha=False, geetest=False):
        """
        {
            "captcha": True,  # 是否开启注册字母验证码
            "geetest": False,  # 是否开启geetest验证，如要开启请先配置geetest
        }
        """
        self.captcha = captcha
        self.geetest = geetest

    def make_rules_info(self):
        data = {}
        if self.captcha:
            data['captcha'] = CaptchaAuth().generate()
        if self.geetest:
            data['geetest'] = True
        return data

    def make_geetest_info(self, unique_key='', ip_address=''):
        if self.geetest:
            return GeeTestAuth(unique_key, ip_address).generate()
        return {}

    def valid(self, data):
        if self.captcha:
            captcha_key = data.get("captcha_key", '')
            verify_code = data.get("verify_code", '')
            is_valid = CaptchaAuth(captcha_key=captcha_key).valid(verify_code)
            if not is_valid:
                return False, '验证码有误'

        if self.geetest:
            """
                "geetest_challenge"  # 极验二次验证表单传参字段 chllenge
                "geetest_validate"  # 极验二次验证表单传参字段 validate
                "geetest_seccode"  # 极验二次验证表单传参字段 seccode
            """
            geetest = data.get("geetest", {})
            is_valid = GeeTestAuth().valid(geetest)

            # geetest_data = {
            #     "geetest_challenge": geetest.get("geetest_challenge"),
            #     "geetest_validate": geetest.get("geetest_validate"),
            #     "geetest_seccode": geetest.get("geetest_seccode")
            # }
            # is_valid = GeeTestAuth().valid(geetest_data)
            if not is_valid:
                return False, '滑动验证有误'

        return True, '验证通过'
