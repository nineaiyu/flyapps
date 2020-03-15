#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/9/18

import hmac
import base64
import inspect
import logging

from urllib.parse import quote

from .. import BaseAli
from ..yun import api
from ..yun.api.base import BaseAliYunAPI
from ..tools import get_uuid
from ..tools import get_iso_8061_date

logger = logging.getLogger(__name__)


QUERY_STRING = None


def _get_signature(string_to_sign, secret, signer=hmac):
    """获取签名

    """
    secret = "{}&".format(secret)
    hmb = signer.new(secret.encode("utf-8"), string_to_sign.encode("utf-8"), "sha1").digest()
    return quote(base64.standard_b64encode(hmb).decode("ascii"), safe="~")


def __pop_standard_urlencode(query):
    ret = ""
    for item in query:
        
        if not item[1]:
            continue

        ret += quote(item[0], safe="~") + "=" + quote(item[1], safe="~") + "&"

    return ret


def _compose_sign_string(query_params):
    """组成签名字符串

    """

    sorted_parameters = sorted(query_params.items(), key=lambda url_params: url_params[0])

    string_to_sign = __pop_standard_urlencode(sorted_parameters)

    query_string = string_to_sign[:-1]

    global QUERY_STRING
    QUERY_STRING = query_string

    tosign = "GET&%2F&" + quote(query_string, safe="~")

    return tosign


def _is_api_endpoint(instance):
    return issubclass(instance.__class__, BaseAliYunAPI)


class AliYunClient(BaseAli):

    VERSION = ""  # 每个接口都需要版本号

    API_BASE_URL = ""  # 阿里云api网关地址均从使用的接口定义

    # 点播api
    vod = api.AliYunVod()
    # 短信api
    sms = api.AliYunSms()

    def __new__(cls, *args, **kwargs):
        """注册接口

        """
        self = super(AliYunClient, cls).__new__(cls)
        api_endpoints = inspect.getmembers(self, _is_api_endpoint)
        for name, api_ins in api_endpoints:
            api_cls = type(api_ins)
            api_ins = api_cls(self)
            setattr(self, name, api_ins)
        return self

    def __init__(self, app_id, secret, timeout=None, auto_retry=False):
        super(AliYunClient, self).__init__(
            timeout, auto_retry
        )
        self.app_id = app_id
        self.secret = secret

    def request(self, method, action, **kwargs):
        """构造请求用户授权的url

        Parameters
        ----------
        method : string
            请求类型

        action : string
            API的命名，固定值，如发送短信API的值为：SendSms

        kwargs : dict
            请求参数

        Returns
        -------
        dict
        """
        query_string = ""

        api_base_url = kwargs.pop("api_base_url", self.API_BASE_URL)

        # 获取请求参数
        if isinstance(kwargs.get("data", {}), dict):

            data = kwargs["data"]

            data["Action"] = action

            # 封装公有请求参数

            # 接口版本号
            if "Version" not in data:
                data["Version"] = kwargs.pop("version", self.VERSION)

            # 时间戳
            data["Timestamp"] = get_iso_8061_date()
            # 签名算法名称
            data["SignatureMethod"] = "HMAC-SHA1"
            # 签名版本
            data["SignatureVersion"] = "1.0"
            # 随机码
            data["SignatureNonce"] = get_uuid()
            # access key
            data["AccessKeyId"] = self.app_id
            # 接口响应类型均为 `JSON`
            data["Format"] = "JSON"

            # 计算签名
            string_to_sign = _compose_sign_string(data)
            signature = _get_signature(string_to_sign, self.secret)

            query_string = '?{}{}'.format(QUERY_STRING, "&" + "Signature=" + signature)

        # 结果解析器, 如果需要定制可单独定制
        result_processor = kwargs.pop("result_processor", None)

        url = "{}{}".format(api_base_url, query_string)

        res = self._http.request(
            method=method,
            url=url,
            **kwargs
        )

        # res.raise_for_status()

        return self._handle_result(res, method, url, result_processor, **kwargs)

    def _handle_result(self, res, method=None, url=None,
                       result_processor=None, **kwargs):
        """结果解析

        Parameters
        ----------
        res : request instance
            响应对象 response

        method : string
            请求方法

        url : string
            请求的 `url`

        result_processor: func OR None
            结果处理器

        kwargs: dict
            更多参数

        Returns
        -------
        dict
        """
        if not isinstance(res, dict):
            result = res.json()
        else:
            result = res

        if not isinstance(result, dict):
            return result

        if "Code" in result:

            code = result.get("Code")

            if code != "OK":
                logger.error("AliApi {} 调用异常, Code {} Errmsg {}".format(
                    url, code, result.get("Message")
                ))

            if code in []:
                self.request(method, url, **kwargs)

        return result if not result_processor else result_processor(result)

    def get(self, url, **kwargs):
        return self.request(
            method="get",
            action=url,
            **kwargs
        )

    def post(self, url, **kwargs):
        return self.request(
            method="post",
            action=url,
            **kwargs
        )
