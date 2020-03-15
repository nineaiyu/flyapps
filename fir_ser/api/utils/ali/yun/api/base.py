#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/9/18


class BaseAliYunAPI(object):

    """

    阿里云服务API基类

    """

    def __init__(self, client=None):
        self._client = client

    def _get(self, action, **kwargs):
        if hasattr(self, "API_BASE_URL"):
            kwargs['api_base_url'] = getattr(self, "API_BASE_URL")

        if hasattr(self, "VERSION"):
            kwargs["version"] = getattr(self, "VERSION")

        return self._client.get(action, **kwargs)

    def _post(self, action, **kwargs):

        if hasattr(self, "API_BASE_URL"):
            kwargs['api_base_url'] = getattr(self, "API_BASE_URL")

        if hasattr(self, "VERSION"):
            kwargs["version"] = getattr(self, "VERSION")

        return self._client.post(action, **kwargs)

    @property
    def app_id(self):
        return self._client.app_id

    @property
    def secret_key(self):
        return self._client.secret_key
