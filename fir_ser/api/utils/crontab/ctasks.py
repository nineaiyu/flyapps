#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

from api.models import Apps, UserInfo, AppIOSDeveloperInfo
from api.utils.storage.storage import Storage
from api.utils.app.supersignutils import IosUtils
from api.utils.utils import send_ios_developer_active_status
from django.core.cache import cache
from fir_ser.settings import CACHE_KEY_TEMPLATE, SYNC_CACHE_TO_DATABASE, SUPER_SIGN_ROOT
import time, os
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


def auto_delete_tmp_file():
    mobileconfig_tmp_dir = os.path.join(SUPER_SIGN_ROOT, 'tmp', 'mobileconfig')
    for root, dirs, files in os.walk(mobileconfig_tmp_dir, topdown=False):
        now_time = time.time()
        for name in files:
            file_path = os.path.join(root, name)
            st_mtime = os.stat(file_path).st_mtime
            if now_time - st_mtime > SYNC_CACHE_TO_DATABASE.get('clean_local_tmp_file_from_mtime', 30 * 60):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error("auto_delete_tmp_file  %s Failed . Exception %s" % (file_path, e))


def auto_check_ios_developer_active():
    all_ios_developer = AppIOSDeveloperInfo.objects.filter(is_actived=True)
    for ios_developer in all_ios_developer:
        userinfo = ios_developer.user_id
        if userinfo.supersign_active:
            status, result = IosUtils.active_developer(ios_developer, userinfo)
            msg = "auto_check_ios_developer_active  user:%s  ios.developer:%s  status:%s  result:%s" % (
                ios_developer.user_id, ios_developer, status, result)
            if status:
                logger.info(msg)
            else:
                ios_developer.is_actived = False
                ios_developer.save()
                logger.error(msg)
                send_ios_developer_active_status(ios_developer.user_id, msg)
