#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2

"""
    阿里巴巴旗下相关服务

        蚂蚁金服

        阿里云

            因阿里云权限访问控制, 可能每种服务都会映射到一个访问key和秘钥(当然也可以用最大权限)

"""

import logging
import requests

logger = logging.getLogger(__name__)


class BaseAli(object):

    API_BASE_URL = ""

    _http = requests.session()

    def __init__(self, timeout, auto_retry=False):
        self.timeout = timeout
        self.auto_retry = auto_retry

    def request(self, *args, **kwargs):
        raise NotImplementedError()

    def get(self, url, **kwargs):
        return self.request(
            method="get",
            url_or_endpoint=url,
            **kwargs
        )

    def post(self, url, **kwargs):
        return self.request(
            method="post",
            url_or_endpoint=url,
            **kwargs
        )
