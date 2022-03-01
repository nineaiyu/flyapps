#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 12月 
# author: NinEveN
# date: 2021/12/22
import logging
import time
from functools import wraps

from django.core.cache import cache

logger = logging.getLogger(__name__)


def run_function_by_locker(timeout=60 * 5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            locker = kwargs.get('locker', {})
            if locker:
                kwargs.pop('locker')
            t_locker = {'timeout': timeout, 'locker_key': func.__name__}
            t_locker.update(locker)
            new_locker_key = t_locker.pop('locker_key')
            new_timeout = t_locker.pop('timeout')
            if locker and new_timeout and new_locker_key:
                with cache.lock(new_locker_key, timeout=new_timeout, **t_locker):
                    logger.info(f"{new_locker_key} exec {func} start. now time:{time.time()}")
                    res = func(*args, **kwargs)
            else:
                res = func(*args, **kwargs)
            logger.info(f"{new_locker_key} exec {func} finished. used time:{time.time() - start_time}")
            return res

        return wrapper

    return decorator


def call_function_try_attempts(try_attempts=3, sleep_time=2, failed_callback=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            res = False, {}
            start_time = time.time()
            for i in range(try_attempts):
                res = func(*args, **kwargs)
                status, result = res
                if status:
                    return res
                else:
                    logger.warning(f'exec {func} failed. {try_attempts} times in total. now {sleep_time} later try '
                                   f'again...{i}')
                time.sleep(sleep_time)
            if not res[0]:
                logger.error(f'exec {func} failed after the maximum number of attempts. Failed:{res[1]}')
                if failed_callback:
                    failed_callback()
            logger.info(f"exec {func} finished. time:{time.time() - start_time}")
            return res

        return wrapper

    return decorator


def get_pending_result(func, expect_func, loop_count=10, sleep_time=3, *args, **kwargs):
    try:
        with cache.lock("%s_%s" % ('get_pending_result', kwargs.get('locker_key')), timeout=loop_count * sleep_time):
            count = 1
            del kwargs['locker_key']
            while True:
                result = func(*args, **kwargs)
                if expect_func(result, *args, **kwargs):
                    return True, result
                time.sleep(sleep_time)
                if loop_count < count:
                    return False, result
                count += 1
    except Exception as e:
        logger.warning(f'get pending result exception: {e}')
        return False, result
