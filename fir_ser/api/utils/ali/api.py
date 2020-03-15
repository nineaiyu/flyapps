#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2

"""
    阿里 api 调用出口

        封装更易用的api
"""

from django.conf import settings
from django.utils.functional import LazyObject

from .pay.basic import AliPay
from .yun.basic import AliYunClient


class AliApi(object):

    # 默认的支付配置
    DEFAULT_ALI_PAY_CONFIG = settings.THIRD_PART_CONFIG["ALI_PAY"]["default"]
    # 指定的支付配置(业务拓展)
    SPECIFIC_ALI_PAY_CONFIG = settings.THIRD_PART_CONFIG["ALI_PAY"].get("pay") or DEFAULT_ALI_PAY_CONFIG
    # 注册云配置
    ALI_YUN_CONFIG = settings.THIRD_PART_CONFIG["ALI_YUN"]

    def __init__(self, ):
        # 支付类业务
        self.pay = AliPay(
            app_id=self.SPECIFIC_ALI_PAY_CONFIG["app_id"],
            app_private_key_path=self.SPECIFIC_ALI_PAY_CONFIG["app_private_key_path"],
            ali_public_key_path=self.SPECIFIC_ALI_PAY_CONFIG["alipay_public_key_path"],
            notify_url=self.SPECIFIC_ALI_PAY_CONFIG["callback_url"],
            return_url=self.SPECIFIC_ALI_PAY_CONFIG["callback_url"],
            debug=self.SPECIFIC_ALI_PAY_CONFIG["debug"]
        )
        # 转账类业务
        self.transfer = AliPay(
            app_id=self.DEFAULT_ALI_PAY_CONFIG["app_id"],
            app_private_key_path=self.DEFAULT_ALI_PAY_CONFIG["app_private_key_path"],
            ali_public_key_path=self.DEFAULT_ALI_PAY_CONFIG["alipay_public_key_path"],
            notify_url=self.SPECIFIC_ALI_PAY_CONFIG["callback_url"],
            return_url=self.SPECIFIC_ALI_PAY_CONFIG["callback_url"],
            debug=self.DEFAULT_ALI_PAY_CONFIG["debug"]
        )
        # 阿里云业务
        self.yun = AliYunClient(
            app_id=self.ALI_YUN_CONFIG.get("ACCESS_KEY"),
            secret=self.ALI_YUN_CONFIG.get("SECRET")
        )


class DefaultApi(LazyObject):

    def _setup(self):
        self._wrapped = AliApi()


ali_api = DefaultApi()
