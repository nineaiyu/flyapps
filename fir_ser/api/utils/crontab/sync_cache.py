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
    key = "_".join([down_tem_key, '*'])
    for app_download in cache.iter_keys(key):
        app_id = app_download.split(down_tem_key)[1].strip('_')
        Apps.objects.filter(app_id=app_id).update(count_hits=cache.get(app_download))


def sync_download_times_by_app_id(app_ids):
    app_id_lists = []
    for app_id in app_ids:
        down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_times_key"), app_id.get("app_id")])
        app_id_lists.append(down_tem_key)
    down_times_lists = cache.get_many(app_id_lists)
    for k, v in down_times_lists.items():
        app_id = k.split(CACHE_KEY_TEMPLATE.get("download_times_key"))[1].strip('_')
        Apps.objects.filter(app_id=app_id).update(count_hits=v)
