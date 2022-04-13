#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7
import datetime
import logging
import time

from django.core.cache import cache

from api.models import Apps, UserInfo, RemoteClientInfo
from common.notify.ntasks import check_user_download_times, check_apple_developer_devices, check_apple_developer_cert
from common.utils.storage import Storage
from fir_ser.settings import CACHE_KEY_TEMPLATE

logger = logging.getLogger(__name__)


def sync_download_times():
    down_tem_key = CACHE_KEY_TEMPLATE.get("download_times_key")
    key = "_".join([down_tem_key, '*'])
    for app_download in cache.iter_keys(key):
        count_hits = cache.get(app_download)
        if count_hits:
            app_id = app_download.split(down_tem_key)[1].strip('_')
            Apps.objects.filter(app_id=app_id).update(count_hits=count_hits)
            logger.info(f"sync_download_times app_id:{app_id} count_hits:{count_hits}")


def auto_clean_upload_tmp_file():
    upload_tem_key = CACHE_KEY_TEMPLATE.get("upload_file_tmp_name_key")
    key = "_".join([upload_tem_key, '*'])
    for upload_tem_file_key in cache.iter_keys(key):
        data = cache.get(upload_tem_file_key)
        if data:
            u_time = data.get("u_time", None)
            if u_time and time.time() - u_time > 60 * 20:
                user_obj = UserInfo.objects.filter(pk=data.get("id")).first()
                if user_obj:
                    storage = Storage(user_obj)
                    filename = data.get("filename", None)
                    if filename:
                        storage.delete_file(filename)
                        logger.info(f"auto_clean_upload_tmp_file delete_file :{filename}")

                cache.delete(upload_tem_file_key)
                logger.info(f"auto_clean_upload_tmp_file upload_tem_file_key :{upload_tem_file_key}")


def auto_clean_remote_client_log(clean_day=30 * 6):
    clean_time = datetime.datetime.now() - datetime.timedelta(days=clean_day)
    return RemoteClientInfo.objects.filter(created_time__lt=clean_time).delete()


def notify_check_user_download_times():
    for user_obj in UserInfo.objects.filter(is_active=True, notify_available_downloads__gt=0).all():
        check_user_download_times(user_obj, days=[0, 1, 3, 7])


def notify_check_apple_developer_devices():
    for user_obj in UserInfo.objects.filter(is_active=True, supersign_active=True, notify_available_signs__gt=0).all():
        check_apple_developer_devices(user_obj, days=[0, 1, 3, 7])


def notify_check_apple_developer_cert():
    for user_obj in UserInfo.objects.filter(is_active=True, supersign_active=True).all():
        check_apple_developer_cert(user_obj, expire_day=7, days=[0, 1, 3, 7])
