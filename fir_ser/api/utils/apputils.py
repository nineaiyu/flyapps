#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6
import logging
import random

from api.models import AppReleaseInfo, Apps
from api.utils.modelutils import get_user_domain_name
from common.base.baseutils import make_app_uuid
from common.base.magic import MagicCacheData
from common.cache.state import MigrateStorageState
from common.utils.caches import del_cache_response_by_short
from common.utils.storage import Storage

logger = logging.getLogger(__name__)


def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if float(n) >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return f'{n}B'


def get_release_type(app_file_name, app_info):
    extension = app_file_name.split(".")[1]
    if extension == "ipa":
        release_type = app_info.get("release_type")
        if release_type == "Adhoc":  # Adhoc： 内测版   Inhouse：企业版
            return 1
        elif release_type == "Inhouse":
            return 2
        else:
            return 3
    else:
        return 0


def get_app_type(app_file_name):
    extension = app_file_name.split(".")[1]
    if extension == "ipa":
        return 1
    if extension == "apk":
        return 0
    else:
        return 2


def get_random_short(number=4):
    short_url = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f',
         'e', 'd', 'c', 'b', 'a'], number))
    app_obj = Apps.objects.filter(short=short_url).first()
    if app_obj:
        number += 2
        return get_random_short(number)
    else:
        return short_url


def clean_history_apps(app_obj, user_obj, history_release_limit=20):
    storage_obj = Storage(user_obj)
    if not MigrateStorageState(user_obj.uid).get_state():
        release_queryset = AppReleaseInfo.objects.filter(app_id=app_obj).order_by("-created_time")
        if release_queryset.count() > history_release_limit:
            flag = 0
            for release_obj in release_queryset:
                flag += 1
                if flag > history_release_limit:
                    logger.info(
                        f"history_release_limit:{history_release_limit} this release is to more,so delete it release_id:{release_obj.release_id}")
                    storage_obj.delete_file(release_obj.release_id, app_obj.type)
                    storage_obj.delete_file(release_obj.icon_url)
                    release_obj.delete()
    MagicCacheData.invalid_cache(app_obj.app_id)


def save_app_infos(app_tmp_filename, app_file_name, user_obj, app_info, bundle_id, app_img, short, size, issupersign):
    app_uuid = make_app_uuid(user_obj, bundle_id + app_file_name.split(".")[1])
    ##判断是否存在该app
    app_obj = Apps.objects.filter(app_id=app_uuid, user_id=user_obj).first()
    storage = Storage(user_obj)
    is_new_app = False
    if not app_obj:
        is_new_app = True
        appdata = {
            "app_id": app_uuid,
            "user_id": user_obj,
            "type": get_app_type(app_file_name),
            "name": app_info["labelname"],
            "new_bundle_name": app_info["labelname"],
            "short": short,
            "issupersign": issupersign,
            "bundle_id": bundle_id,
            "count_hits": 0,
            "wxeasytype": False if get_user_domain_name(user_obj) else True
        }
        try:
            if Apps.objects.filter(short=short).count() == 1:
                appdata['short'] = get_random_short()
            app_obj = Apps.objects.create(**appdata)
        except Exception as e:
            logger.error(f"create new app failed,appdata:{appdata}  Exception:{e}")
            return False
    else:
        try:
            is_new_app = False
            app_obj.short = short
            app_obj.name = app_info["labelname"]
            app_obj.issupersign = issupersign
            # appmobj.wxeasytype = False if user_obj.domain_name or appmobj.domain_name else True
            app_obj.bundle_id = bundle_id
            app_obj.save(update_fields=["short", "name", "bundle_id", "issupersign", "updated_time"])
        except Exception as e:
            logger.error(f"save app info failed,app_obj:{app_obj}  Exception:{e}")
            app_obj.bundle_id = bundle_id
            app_obj.issupersign = issupersign
            app_obj.name = app_info["labelname"]
            app_obj.save(update_fields=["name", "bundle_id", "issupersign", "updated_time"])
        del_cache_response_by_short(app_obj.app_id)
        MagicCacheData.invalid_cache(app_obj.app_id)
    AppReleaseInfo.objects.filter(app_id=app_obj).update(is_master=False)

    file_info = storage.get_file_info(app_tmp_filename)
    logger.info(f'get file {app_tmp_filename} info:{file_info}')
    size = file_info.get('content_length', size)

    release_data = {
        "app_id": app_obj,
        "icon_url": app_img,
        "release_id": app_file_name.split(".")[0],
        "build_version": str(app_info.get("version", "latest")),
        "app_version": str(app_info.get("versioncode", "latest")),
        "release_type": get_release_type(app_file_name, app_info),
        "minimum_os_version": str(app_info.get("miniOSversion", "latest")),
        "binary_size": size,
        "is_master": True,
        "changelog": app_info.get("changelog", ''),
        "udid": app_info.get("udid", ''),
        "distribution_name": app_info.get("distribution_name", ''),
    }
    try:
        AppReleaseInfo.objects.create(**release_data)
    except Exception as e:
        logger.error(f"create app release failed,release_data:{release_data}  Exception:{e}")
        if is_new_app:
            logger.info(
                f"create app release failed,release_data:{release_data} ,and app is new ,so delete this app:{app_obj}")
            storage.delete_file(release_data.get("release_id"), app_obj.type)
            storage.delete_file(app_img)
            app_obj.delete()
        return False
    try:
        history_release_limit = int(user_obj.history_release_limit)
    except Exception as e:
        logger.error(
            f"get history_release_limit failed,history_release_limit:{user_obj.history_release_limit}  Exception:{e}")
        return True

    if history_release_limit != 0:
        clean_history_apps(app_obj, user_obj, history_release_limit)
    return True
