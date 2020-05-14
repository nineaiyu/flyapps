#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

from api.models import Apps, UserInfo
from api.utils.storage.storage import Storage
from django.core.cache import cache
from fir_ser.settings import CACHE_KEY_TEMPLATE, SYNC_CACHE_TO_DATABASE
import time
from django_apscheduler.models import DjangoJobExecution
import logging

logger = logging.getLogger(__file__)


def sync_download_times():
    down_tem_key = CACHE_KEY_TEMPLATE.get("download_times_key")
    key = "_".join([down_tem_key, '*'])
    for app_download in cache.iter_keys(key):
        count_hits = cache.get(app_download)
        app_id = app_download.split(down_tem_key)[1].strip('_')
        Apps.objects.filter(app_id=app_id).update(count_hits=count_hits)
        logger.info("sync_download_times app_id:%s count_hits:%s" % (app_id, count_hits))


def sync_download_times_by_app_id(app_ids):
    app_id_lists = []
    for app_id in app_ids:
        down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_times_key"), app_id.get("app_id")])
        app_id_lists.append(down_tem_key)
    down_times_lists = cache.get_many(app_id_lists)
    for k, v in down_times_lists.items():
        app_id = k.split(CACHE_KEY_TEMPLATE.get("download_times_key"))[1].strip('_')
        Apps.objects.filter(app_id=app_id).update(count_hits=v)
        logger.info("sync_download_times_by_app_id app_id:%s count_hits:%s" % (app_id, v))


def auto_clean_upload_tmp_file():
    upload_tem_key = CACHE_KEY_TEMPLATE.get("upload_file_tmp_name_key")
    key = "_".join([upload_tem_key, '*'])
    for upload_tem_file_key in cache.iter_keys(key):
        data = cache.get(upload_tem_file_key)
        if data:
            stime = data.get("stime", None)
            if stime and time.time() - stime > 60 * 20:
                user_obj = UserInfo.objects.filter(pk=data.get("id")).first()
                if user_obj:
                    storage = Storage(user_obj)
                    filename = data.get("filename", None)
                    if filename:
                        storage.delete_file(filename)
                        logger.info("auto_clean_upload_tmp_file delete_file :%s " % (filename))

                cache.delete(upload_tem_file_key)
                logger.info("auto_clean_upload_tmp_file upload_tem_file_key :%s " % (upload_tem_file_key))


def auto_delete_job_log():
    job_execution = DjangoJobExecution.objects.order_by("-id").values("id").first()
    if job_execution:
        need_count = SYNC_CACHE_TO_DATABASE.get("auto_clean_apscheduler_log", 10000)
        max_id = job_execution.get("id")
        count = DjangoJobExecution.objects.count()
        if count > need_count:
            DjangoJobExecution.objects.filter(id__lte=max_id - need_count).delete()
