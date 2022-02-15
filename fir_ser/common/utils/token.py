#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/8
import logging
import random
import string
import time
import uuid

from common.cache.storage import TokenManagerCache, RedisCacheBase

logger = logging.getLogger(__name__)


def make_token(release_id, time_limit=60, key='', force_new=False):
    token_cache = TokenManagerCache(key, release_id)
    token_key, token = token_cache.get_storage_key_and_cache()
    if token and not force_new:
        logger.debug(
            f"make_token  cache exists get token:{token}  release_id:{release_id} force_new:{force_new} token_key:{token_key}")
        return token
    else:
        random_str = uuid.uuid1().__str__().split("-")[0:-1]
        user_ran_str = uuid.uuid5(uuid.NAMESPACE_DNS, release_id).__str__().split("-")
        user_ran_str.extend(random_str)
        token = "".join(user_ran_str)
        token_cache.set_storage_cache({
            "atime": time.time() + time_limit,
            "data": release_id
        }, time_limit)
        RedisCacheBase(token).set_storage_cache({
            "atime": time.time() + time_limit,
            "data": release_id
        }, time_limit)
        token_cache.set_storage_cache(token, time_limit - 1)
        logger.debug(
            f"make_token  cache not exists get token:{token}  release_id:{release_id} force_new:{force_new} token_key:{token_key}")
        return token


def verify_token(token, release_id, success_once=False):
    try:
        token_cache = RedisCacheBase(token)
        token, values = token_cache.get_storage_key_and_cache()
        if values and release_id == values.get("data", None):
            logger.debug(f"verify_token token:{token}  release_id:{release_id} success")
            if success_once:
                token_cache.del_storage_cache()
            return True
    except Exception as e:
        logger.error(f"verify_token token:{token}  release_id:{release_id} failed Exception:{e}")
        return False
    logger.error(f"verify_token token:{token}  release_id:{release_id} failed")
    return False


def generate_token_for_medium(medium):
    if medium == 'email':
        return generate_alphanumeric_token_of_length(32)
    elif medium == 'wechat':
        return 'WeChat'
    else:
        return generate_numeric_token_of_length(6)


def generate_numeric_token_of_length(length, random_str=''):
    return "".join([random.choice(string.digits + random_str) for _ in range(length)])


def generate_alphanumeric_token_of_length(length):
    return "".join(
        [random.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase) for _ in range(length)])
