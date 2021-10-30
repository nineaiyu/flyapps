#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 9月 
# author: NinEveN
# date: 2020/9/24

import base64

from django.core.cache import cache


class TmpCache(object):

    @staticmethod
    def set_tmp_cache(key, token, target, limit=60 * 5):
        nkey = '%s:%s' % (key, token)
        nkey = base64.b64encode(nkey.encode("utf-8")).decode("utf-8")
        cache.set(nkey, target, limit)

    @staticmethod
    def get_tmp_cache(key, token):
        nkey = '%s:%s' % (key, token)
        nkey = base64.b64encode(nkey.encode("utf-8")).decode("utf-8")
        return cache.get(nkey)

    @staticmethod
    def del_tmp_cache(key, token):
        nkey = base64.b64encode('%s:%s'.encode("utf-8") % (key, token))
        return cache.delete(nkey)
