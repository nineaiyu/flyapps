#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

import logging
import os
import time

from api.models import Apps, UserInfo
from api.utils.modelutils import get_app_d_count_by_app_id, add_remote_info_from_request, check_app_access_token
from api.utils.signalutils import run_xsign_app_download_url
from common.base.baseutils import get_real_ip_address
from common.cache.storage import AppDownloadTodayTimesCache, AppDownloadTimesCache, DownloadUrlCache, AppInstanceCache
from common.core.sysconfig import Config
from common.utils.caches import consume_user_download_times
from common.utils.storage import Storage, LocalStorage

logger = logging.getLogger(__name__)


def get_download_url_by_cache(app_obj, filename, limit, is_download=True, key='', udid=None):
    now = time.time()
    if is_download:
        download_val = DownloadUrlCache(key, filename).get_storage_cache()
        if download_val:
            if download_val.get("time") > now - 60:
                return download_val.get("download_url"), ""
        else:
            user_obj = UserInfo.objects.filter(pk=app_obj.get("user_id")).first()
            storage = Storage(user_obj)
            return storage.get_download_url(filename, limit), ""
    else:
        local_storage = LocalStorage(**Config.IOS_PMFILE_DOWNLOAD_DOMAIN)
        download_url_type = 'plist'
        if udid:
            return run_xsign_app_download_url(app_obj, udid, download_url_type, limit)
        else:
            if app_obj.get('issupersign', None):
                download_url_type = 'mobileconifg'

        supersign = Config.DEFAULT_MOBILEPROVISION.get("supersign")
        mobileconifg = ""

        if download_url_type == 'plist':
            enterprise = Config.DEFAULT_MOBILEPROVISION.get("enterprise")
            mpath = enterprise.get('path', None)
            murl = enterprise.get('url', None)
        else:
            mpath = supersign.get('path', None)
            murl = supersign.get('url', None)

        if murl and len(murl) > 5:
            mobileconifg = murl

        if mpath and os.path.isfile(mpath):
            mobileconifg = local_storage.get_download_url(filename.split(".")[0] + "." + "dmobileprovision", limit)

        if download_url_type == 'mobileconifg' and supersign.get("self"):
            mobileconifg = local_storage.get_download_url(filename.split(".")[0] + "." + "mobileprovision", limit)

        return local_storage.get_download_url(filename.split(".")[0] + "." + download_url_type, limit), mobileconifg


def get_app_instance_by_cache(app_id, limit):
    app_instance_cache = AppInstanceCache(app_id)
    app_obj_cache = app_instance_cache.get_storage_cache()
    if not app_obj_cache:
        app_obj_cache = Apps.objects.filter(app_id=app_id).values("pk", 'user_id', 'type', 'need_password',
                                                                  'issupersign',
                                                                  'user_id__certification__status').first()
        if app_obj_cache:
            app_obj_cache['d_count'] = get_app_d_count_by_app_id(app_id)
            app_instance_cache.set_storage_cache(app_obj_cache, limit)
    if not app_obj_cache:
        return False, '应用不存在'
    return True, app_obj_cache


def set_app_today_download_times(app_id):
    cache_obj = AppDownloadTodayTimesCache(app_id)
    if cache_obj.get_storage_cache():
        cache_obj.incr()
    else:
        cache_obj.set_storage_cache(1, 3600 * 24)


def set_app_download_by_cache(app_id, limit=900):
    app_download_cache = AppDownloadTimesCache(app_id)
    download_times = app_download_cache.get_storage_cache()
    if not download_times:
        download_times = Apps.objects.filter(app_id=app_id).values("count_hits").first().get('count_hits')
        app_download_cache.set_storage_cache(download_times + 1, limit)
    else:
        app_download_cache.incr()
        app_download_cache.expire(limit)
    set_app_today_download_times(app_id)
    return download_times + 1


def check_app_download_token(need_password, is_download, app_id, password, only_check=False, udid=None):
    if need_password:
        if is_download or check_app_access_token(app_id, password, only_check, udid):
            return True
    else:
        return True


def get_app_download_url(request, res, app_id, short, password, release_id, is_download, udid):
    status, app_obj = get_app_instance_by_cache(app_id, 900)
    if status:
        if app_obj.get("type") == 0:
            app_type = '.apk'
            download_url, extra_url = get_download_url_by_cache(app_obj, release_id + app_type, 600)
        else:
            app_type = '.ipa'
            download_url, extra_url = get_download_url_by_cache(app_obj, release_id + app_type, 600, is_download,
                                                                udid=udid)

        res.data = {"download_url": download_url, "extra_url": extra_url}
        if download_url != "" and "mobileconifg" not in download_url:

            if not check_app_download_token(app_obj.get("need_password"), is_download, app_id, password):
                res.code = 1006
                res.msg = '下载授权码有误'
                return res

            ip = get_real_ip_address(request)
            msg = f"remote ip {ip} short {short} download_url {download_url} app_obj {app_obj}"
            logger.info(msg)
            add_remote_info_from_request(request, msg)
            set_app_download_by_cache(app_id)
            amount = app_obj.get("d_count")
            auth_status = False
            status = app_obj.get('user_id__certification__status', None)
            if status and status == 1:
                auth_status = True
            if not consume_user_download_times(app_obj.get("user_id"), app_id, amount, auth_status):
                res.code = 1009
                res.msg = "可用下载额度不足"
                del res.data
                return res
        return res
    res.code = 1006
    res.msg = str(app_obj)
    return res
