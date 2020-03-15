#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2


class BaseAliPayAPI(object):

    """

    支付宝支付API基类

    """

    def __init__(self, client=None):
        self._client = client

    def _get(self, url, **kwargs):
        if hasattr(self, "API_BASE_URL"):
            kwargs['api_base_url'] = getattr(self, "API_BASE_URL")
        return self._client.get(url, **kwargs)

    def _post(self, url, **kwargs):
        if hasattr(self, "API_BASE_URL"):
            kwargs['api_base_url'] = getattr(self, "API_BASE_URL")
        return self._client.post(url, **kwargs)

    def _generate_url(self, method, *args, **kwargs):
        return self._client.generate_url(method, *args, **kwargs)

    @property
    def app_id(self):
        return self._client.app_id
