#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2

import json
import inspect

from urllib.parse import quote_plus

from Crypto.PublicKey import RSA

from django.utils.timezone import now

from .. import BaseAli
from ..tools import calculate_signature
from .api.base import BaseAliPayAPI
from . import api


def _is_api_endpoint(instance):
    return issubclass(instance.__class__, BaseAliPayAPI)


class AliPay(BaseAli):
    # 在构造函数中初始化
    API_BASE_URL = ""

    # PC支付
    pc = api.AliPage()
    # Wap支付
    wap = api.AliWap()
    # App支付
    app = api.AliApp()
    # 转账
    transfer = api.AliTransfer()
    # 统一收单相关
    order = api.AliOrder()

    def __init__(
        self, app_id, app_private_key_path, ali_public_key_path,
        notify_url, return_url, debug,
    ):

        # 如果是调试模式，则用调试api
        if debug:
            setattr(self, "API_BASE_URL", "https://openapi.alipaydev.com/gateway.do")
        else:
            setattr(self, "API_BASE_URL", "https://openapi.alipay.com/gateway.do")

        # 暂时用不到父类方法参数(设置默认值)
        super(AliPay, self).__init__(timeout=3, auto_retry=True)

        self.app_id = app_id
        self.notify_url = notify_url
        self.return_url = return_url

        # 加载应用的私钥
        with open(app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())

        # 加载支付宝公钥
        with open(ali_public_key_path) as fp:
            self.ali_public_key = RSA.importKey(fp.read())

    def __new__(cls, *args, **kwargs):
        self = super(AliPay, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api_ins in api_endpoints:
            api_cls = type(api_ins)
            api_ins = api_cls(self)
            setattr(self, name, api_ins)
        return self

    def request(self, method, url_or_endpoint, **kwargs):
        if not url_or_endpoint.startswith(('http://', 'https://')):
            api_base_url = kwargs.pop('api_base_url', self.API_BASE_URL)
            url = '{base}{endpoint}'.format(
                base=api_base_url,
                endpoint=url_or_endpoint
            )
        else:
            url = url_or_endpoint

        res = self._http.request(
            method=method,
            url=url,
            **kwargs
        )

        res.raise_for_status()

        return self._handle_result(res)

    def _handle_result(self, res):
        """解析请求结果并校验签名

        """
        return res.json()

    def get_url_params(self, data):
        data.pop("sign", None)
        # 排序后[(k, v), ...]
        ordered_items = sorted(
            ((k, v if not isinstance(v, dict) else json.dumps(v, separators=(',', ':')))
             for k, v in data.items())
        )
        # 拼接成待签名的字符串
        unsigned_string = "&".join("{0}={1}".format(k, v) for k, v in ordered_items)
        # 对上一步得到的字符串进行签名
        sign = calculate_signature(unsigned_string.encode("utf-8"), self.app_private_key)
        # 处理URL
        quoted_string = "&".join("{0}={1}".format(k, quote_plus(v)) for k, v in ordered_items)
        # 添加签名，获得最终的订单信息字符串
        signed_string = quoted_string + "&sign=" + quote_plus(sign)
        return signed_string

    def build_body(self, method, biz_content, notify_url=None, return_url=None):
        """构建请求体

            公有请求体 + 业务请求体

        Parameters
        ----------
        method : string
            请求API

        biz_content: dict
            业务参数

        notify_url: string, default: None
            异步通知地址

        return_url: string, default: None
            同步地址

        Returns
        -------
        请求参数: dict
        """
        data = {
            "app_id": self.app_id,
            "method": method,
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": biz_content
        }

        # 同步回调
        if notify_url is not None:
            data["notify_url"] = notify_url

        # 异步回调
        if return_url is not None:
            data["return_url"] = return_url

        return data

    def generate_url(self, method, biz_content, notify_url=None, return_url=None):
        """构建请求体.
            公有请求体 + 业务请求体

        Parameters
        ----------
        method : string

            请求API

        biz_content: dict

            业务参数

        notify_url: string, default: None

            异步通知 `url`

        return_url: string, default: None

            同步通知 `url`


        Returns
        -------
        string
        """

        if notify_url is None:
            notify_url = self.notify_url

        if return_url is None:
            return_url = self.return_url

        body = self.build_body(method, biz_content, notify_url, return_url)

        params = self.get_url_params(body)

        return "{}?{}".format(self.API_BASE_URL, params)
