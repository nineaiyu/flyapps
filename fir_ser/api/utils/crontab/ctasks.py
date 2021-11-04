#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

import logging
import os
import time

from django.core.cache import cache

from api.models import Apps, UserInfo, AppIOSDeveloperInfo
from api.utils.app.supersignutils import IosUtils
from api.utils.storage.storage import Storage
from api.utils.utils import send_ios_developer_active_status
from fir_ser.settings import CACHE_KEY_TEMPLATE, SYNC_CACHE_TO_DATABASE, SUPER_SIGN_ROOT, MSGTEMPLATE

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


def auto_delete_ios_mobile_tmp_file():
    mobile_config_tmp_dir = os.path.join(SUPER_SIGN_ROOT, 'tmp', 'mobile_config')
    for root, dirs, files in os.walk(mobile_config_tmp_dir, topdown=False):
        now_time = time.time()
        for name in files:
            file_path = os.path.join(root, name)
            st_mtime = os.stat(file_path).st_mtime
            if now_time - st_mtime > SYNC_CACHE_TO_DATABASE.get('clean_local_tmp_file_from_mtime', 30 * 60):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"auto_delete_tmp_file {file_path} Failed . Exception {e}")


def auto_check_ios_developer_active():
    all_ios_developer = AppIOSDeveloperInfo.objects.filter(is_actived=True)
    for ios_developer in all_ios_developer:
        userinfo = ios_developer.user_id
        if userinfo.supersign_active:
            count = 3
            while count > 0:
                status, result = IosUtils.active_developer(ios_developer)
                msg = f"auto_check_ios_developer_active  user:{userinfo}  ios.developer:{ios_developer}  status:{status}  result:{result}"
                if status:
                    IosUtils.get_device_from_developer(ios_developer)
                    logger.info(msg)
                    break
                else:
                    count -= 1
                    time.sleep(5)
                if count == 0:
                    ios_developer.is_actived = False
                    ios_developer.save(update_fields=['is_actived'])
                    logger.error(msg)
                    send_ios_developer_active_status(userinfo, MSGTEMPLATE.get('AUTO_CHECK_DEVELOPER') % (
                        userinfo.first_name, ios_developer.name))
