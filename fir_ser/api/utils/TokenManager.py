#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/8
import uuid
import string
import random
import time
from django.core.cache import cache
from fir_ser.settings import CACHE_KEY_TEMPLATE

'''
        user = cache.get(token)
        delta = datetime.timedelta(weeks=2) - delta
        cache.set(token_obj.key, token_obj.user, min(delta.total_seconds(), 3600 * 24 * 7))
'''


class DownloadToken(object):

    def make_token(self, release_id, time_limit=60, key='', force_new=False):
        token_key = "_".join([key.lower(), CACHE_KEY_TEMPLATE.get("make_token_key"), release_id])
        token = cache.get(token_key)
        if token and not force_new:
            return token
        else:
            random_str = uuid.uuid1().__str__().split("-")[0:-1]
            user_ran_str = uuid.uuid5(uuid.NAMESPACE_DNS, release_id).__str__().split("-")
            user_ran_str.extend(random_str)
            token = "".join(user_ran_str)
            cache.set(token, {
                "atime": time.time() + time_limit,
                "data": release_id
            }, time_limit)
            cache.set(token_key, token, time_limit - 1)
            return token

    def verify_token(self, token, release_id):
        try:
            values = cache.get(token)
            if values and release_id in values.get("data", None):
                return True
        except Exception as e:
            print(e)
            return False

        return False


def generateTokenForMedium(medium):
    if medium == 'email':
        return generateAlphanumericTokenOfLength(32)
    elif medium == 'wechat':
        return 'WeChat'
    else:
        return generateNumericTokenOfLength(6)


def generateNumericTokenOfLength(length):
    return "".join([random.choice(string.digits) for _ in range(length)])


def generateAlphanumericTokenOfLength(length):
    return "".join(
        [random.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase) for _ in range(length)])
