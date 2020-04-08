#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

from django.core.cache import cache
from api.models import Apps,UserInfo
import time
from django.utils import timezone
from fir_ser.settings import CACHE_KEY_TEMPLATE
from api.utils.storage.storage import Storage,LocalStorage
from api.utils.crontab.sync_cache import sync_download_times_by_app_id
from api.utils.crontab import run

def get_download_url_by_cache(app_obj, filename, limit, isdownload=True,key=''):
    now = time.time()
    if isdownload is None:
        local_storage = LocalStorage('localhost', False)
        return local_storage.get_download_url(filename, limit, 'plist')
    down_key = "_".join([key.lower(), CACHE_KEY_TEMPLATE.get('download_url_key'), filename])
    download_val = cache.get(down_key)
    if download_val:
        if download_val.get("time") > now - 60:
            return download_val.get("download_url")
    else:
        user_obj = UserInfo.objects.filter(pk=app_obj.get("user_id")).first()
        storage = Storage(user_obj)
        return storage.get_download_url(filename, limit)


def get_app_instance_by_cache(app_id, limit):
    app_key="_".join([CACHE_KEY_TEMPLATE.get("app_instance_key"),app_id])
    app_obj_cache = cache.get(app_key)
    if not app_obj_cache:
        app_obj_cache = Apps.objects.filter(app_id=app_id).values("pk", 'user_id', 'type').first()
        cache.set(app_key, app_obj_cache, limit)
    return app_obj_cache


def set_app_download_by_cache(app_id, limit=900):
    down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_times_key"),app_id])
    download_times = cache.get(down_tem_key)
    if not download_times:
        download_times=Apps.objects.filter(app_id=app_id).values("count_hits").first().get('count_hits')
        cache.set(down_tem_key, download_times + 1, limit)
    else:
        cache.incr(down_tem_key)
        cache.expire(down_tem_key, timeout=limit)
    set_app_today_download_times(app_id)
    return download_times + 1

def del_cache_response_by_short(short,app_id):
    cache.delete("_".join([CACHE_KEY_TEMPLATE.get("download_short_key"),short]))
    cache.delete("_".join([CACHE_KEY_TEMPLATE.get("app_instance_key"),app_id]))


def set_app_today_download_times(app_id):
    now = timezone.now()
    down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_today_times_key"),
                             str(now.year),str(now.month),str(now.day),app_id])
    if cache.get(down_tem_key):
        cache.incr(down_tem_key)
    else:
        cache.set(down_tem_key,1,3600*24)

def get_app_today_download_times(app_ids):
    sync_download_times_by_app_id(app_ids)

    now = timezone.now()
    app_id_lists=[]
    download_times_count=0
    for app_id in app_ids:
        down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_today_times_key"),
                                 str(now.year),str(now.month),str(now.day),app_id.get("app_id")])
        app_id_lists.append(down_tem_key)
    down_times_lists = cache.get_many(app_id_lists)
    for k, v in down_times_lists.items():
        download_times_count+=v
    return download_times_count
