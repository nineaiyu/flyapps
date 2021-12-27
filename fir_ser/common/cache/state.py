#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 12月 
# author: NinEveN
# date: 2021/12/22
import logging
import time

from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheBaseState(object):

    def __init__(self, key, value=time.time(), timeout=3600 * 24):
        self.key = f"CacheBaseState_{self.__class__.__name__}_{key}"
        self.value = value
        self.timeout = timeout
        self.active = False

    def get_state(self):
        return cache.get(self.key)

    def __enter__(self):
        if cache.get(self.key):
            return False
        else:
            cache.set(self.key, self.value, self.timeout)
            self.active = True
        return True

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.active:
            cache.delete(self.key)
        logger.info(f"cache base state __exit__ {exc_type}, {exc_val}, {exc_tb}")


class MigrateStorageState(CacheBaseState):
    ...


class CleanSignDataState(CacheBaseState):
    ...


class CleanAppSignDataState(CacheBaseState):
    ...


class CleanErrorBundleIdSignDataState(CacheBaseState):
    ...
