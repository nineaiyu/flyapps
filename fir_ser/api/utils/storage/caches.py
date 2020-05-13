#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

from django.core.cache import cache
from api.models import Apps, UserInfo, AppReleaseInfo, AppUDID, APPToDeveloper, APPSuperSignUsedInfo
import time, os
from django.utils import timezone
from fir_ser.settings import CACHE_KEY_TEMPLATE, SERVER_DOMAIN
from api.utils.storage.storage import Storage, LocalStorage
from api.utils.crontab.sync_cache import sync_download_times_by_app_id
from api.utils.utils import file_format_path

try:
    from api.utils.crontab import run
except Exception as e:
    print(e)


def get_download_url_by_cache(app_obj, filename, limit, isdownload=True, key='', udid=None):
    now = time.time()
    if isdownload is None:
        local_storage = LocalStorage(**SERVER_DOMAIN.get("IOS_PMFILE_DOWNLOAD_DOMAIN"))
        download_url_type = 'plist'
        if not udid:
            if app_obj.get('issupersign', None):
                download_url_type = 'mobileconifg'
        else:
            appudid_obj = AppUDID.objects.filter(app_id_id=app_obj.get("pk"), udid=udid, is_signed=True).first()
            if appudid_obj:
                SuperSign_obj = APPSuperSignUsedInfo.objects.filter(udid__udid=udid,
                                                                    app_id_id=app_obj.get("pk")).first()
                if SuperSign_obj:
                    APPToDeveloper_obj = APPToDeveloper.objects.filter(app_id_id=app_obj.get("pk"),
                                                                       developerid=SuperSign_obj.developerid).first()
                    if APPToDeveloper_obj:
                        return local_storage.get_download_url(
                            APPToDeveloper_obj.binary_file + "." + download_url_type, limit)
                    else:
                        return ""
                else:
                    return ""
            else:
                return ""

        return local_storage.get_download_url(filename.split(".")[0] + "." + download_url_type, limit)
    down_key = "_".join([key.lower(), CACHE_KEY_TEMPLATE.get('download_url_key'), filename])
    download_val = cache.get(down_key)
    if download_val:
        if download_val.get("time") > now - 60:
            return download_val.get("download_url")
    else:
        user_obj = UserInfo.objects.filter(pk=app_obj.get("user_id")).first()
        storage = Storage(user_obj)
        return storage.get_download_url(filename, limit)


def get_app_instance_by_cache(app_id, password, limit, udid):
    if udid:
        return Apps.objects.filter(app_id=app_id).values("pk", 'user_id', 'type', 'password', 'issupersign').first()
    app_key = "_".join([CACHE_KEY_TEMPLATE.get("app_instance_key"), app_id])
    app_obj_cache = cache.get(app_key)
    if not app_obj_cache:
        app_obj_cache = Apps.objects.filter(app_id=app_id).values("pk", 'user_id', 'type', 'password',
                                                                  'issupersign').first()
        cache.set(app_key, app_obj_cache, limit)

    app_password = app_obj_cache.get("password")

    if app_password != '':
        if password is None:
            return None

        if app_password.lower() != password.strip().lower():
            return None

    return app_obj_cache


def set_app_download_by_cache(app_id, limit=900):
    down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_times_key"), app_id])
    download_times = cache.get(down_tem_key)
    if not download_times:
        download_times = Apps.objects.filter(app_id=app_id).values("count_hits").first().get('count_hits')
        cache.set(down_tem_key, download_times + 1, limit)
    else:
        cache.incr(down_tem_key)
        cache.expire(down_tem_key, timeout=limit)
    set_app_today_download_times(app_id)
    return download_times + 1


def del_cache_response_by_short(short, app_id, udid=''):
    cache.delete("_".join([CACHE_KEY_TEMPLATE.get("download_short_key"), short]))
    key = "_".join([CACHE_KEY_TEMPLATE.get("download_short_key"), short, '*'])
    for app_download_key in cache.iter_keys(key):
        cache.delete(app_download_key)

    cache.delete("_".join([CACHE_KEY_TEMPLATE.get("app_instance_key"), app_id]))

    key = 'ShortDownloadView'.lower()
    master_release_dict = AppReleaseInfo.objects.filter(app_id__app_id=app_id, is_master=True).values('icon_url',
                                                                                                      'release_id').first()
    if master_release_dict:
        download_val = CACHE_KEY_TEMPLATE.get('download_url_key')
        cache.delete("_".join([key, download_val, os.path.basename(master_release_dict.get("icon_url")), udid]))
        cache.delete("_".join([key, download_val, master_release_dict.get('release_id'), udid]))
        cache.delete(
            "_".join([key, CACHE_KEY_TEMPLATE.get("make_token_key"), master_release_dict.get('release_id'), udid]))


def del_cache_by_app_id(app_id, user_obj):
    key = ''
    master_release_dict = AppReleaseInfo.objects.filter(app_id__app_id=app_id, is_master=True).values('icon_url',
                                                                                                      'release_id').first()
    download_val = CACHE_KEY_TEMPLATE.get('download_url_key')
    cache.delete("_".join([key, download_val, os.path.basename(master_release_dict.get("icon_url"))]))
    cache.delete("_".join([key, download_val, master_release_dict.get('release_id')]))
    cache.delete(
        "_".join([key.lower(), CACHE_KEY_TEMPLATE.get("make_token_key"), master_release_dict.get('release_id')]))
    cache.delete("_".join([key, download_val, user_obj.head_img]))


def del_cache_storage(user_obj):
    for app_obj in Apps.objects.filter(user_id=user_obj):
        del_cache_response_by_short(app_obj.short, app_obj.app_id)
        del_cache_by_app_id(app_obj.app_id, user_obj)

    storage_keys = "_".join([CACHE_KEY_TEMPLATE.get('user_storage_key'), user_obj.uid, '*'])
    for storage_key in cache.iter_keys(storage_keys):
        cache.delete(storage_key)


def set_app_today_download_times(app_id):
    now = timezone.now()
    down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_today_times_key"),
                             str(now.year), str(now.month), str(now.day), app_id])
    if cache.get(down_tem_key):
        cache.incr(down_tem_key)
    else:
        cache.set(down_tem_key, 1, 3600 * 24)


def get_app_today_download_times(app_ids):
    sync_download_times_by_app_id(app_ids)

    now = timezone.now()
    app_id_lists = []
    download_times_count = 0
    for app_id in app_ids:
        down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_today_times_key"),
                                 str(now.year), str(now.month), str(now.day), app_id.get("app_id")])
        app_id_lists.append(down_tem_key)
    down_times_lists = cache.get_many(app_id_lists)
    for k, v in down_times_lists.items():
        download_times_count += v
    return download_times_count


def developer_auth_code(act, user_obj, developer_email, code=None):
    auth_key = file_format_path(user_obj, email=developer_email)
    key = "_".join([CACHE_KEY_TEMPLATE.get("developer_auth_code_key"), auth_key])
    if act == "set":
        cache.delete(key)
        cache.set(key, code, 60 * 10)
    elif act == "get":
        return cache.get(key)
    elif act == "del":
        cache.delete(key)


def upload_file_tmp_name(act, filename, user_obj_id):
    tmp_key = "_".join([CACHE_KEY_TEMPLATE.get("upload_file_tmp_name_key"), filename])
    if act == "set":
        cache.delete(tmp_key)
        cache.set(tmp_key, {'time': time.time(), 'id': user_obj_id, "filename": filename}, 60 * 60)
    elif act == "get":
        return cache.get(tmp_key)
    elif act == "del":
        cache.delete(tmp_key)
