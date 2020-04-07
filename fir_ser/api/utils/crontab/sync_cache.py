#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

from api.models import Apps
from django.core.cache import cache
from fir_ser.settings import CACHE_KEY_TEMPLATE


def sync_download_times():
    down_tem_key = CACHE_KEY_TEMPLATE.get("download_times_key")
    key = "%s%s" %(down_tem_key,'*')
    for app_download in cache.iter_keys(key):
        app_id = app_download.split(down_tem_key)[1]
        Apps.objects.filter(app_id=app_id).update(count_hits=cache.get(app_download))



