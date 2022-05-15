#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2021/4/13

import logging

from api.models import AppReleaseInfo, UserInfo, AppScreenShot, AppStorage
from api.utils.response import BaseResponse
from api.utils.signalutils import run_delete_app_signal
from api.utils.utils import delete_local_files, delete_app_screenshots_files, change_storage_and_change_head_img, \
    migrating_storage_data, clean_storage_data, check_storage_is_new_storage, migrating_storage_file_data
from common.base.magic import MagicCacheData
from common.cache.state import MigrateStorageState
from common.utils.caches import del_cache_response_by_short, del_cache_by_delete_app, \
    del_cache_storage
from common.utils.storage import Storage

logger = logging.getLogger(__name__)


def app_delete(app_obj):
    res = BaseResponse()
    if not app_obj:
        res.code = 1001
        res.msg = "应用不存在"
        return res
    user_obj = app_obj.user_id
    if MigrateStorageState(user_obj.uid).get_state():
        res.code = 1001
        res.msg = "数据迁移中"
        return res

    run_delete_app_signal(app_obj)

    storage = Storage(user_obj)
    has_combo = app_obj.has_combo
    del_cache_response_by_short(app_obj.app_id)
    del_cache_by_delete_app(app_obj.app_id)
    for app_release_obj in AppReleaseInfo.objects.filter(app_id=app_obj).all():
        logger.info(f"delete app_id:{app_obj.app_id}  need clean all release,release_id:{app_release_obj.release_id}")
        storage.delete_file(app_release_obj.release_id, app_release_obj.release_type)
        delete_local_files(app_release_obj.release_id, app_release_obj.release_type)
        storage.delete_file(app_release_obj.icon_url)
        app_release_obj.delete()
    delete_app_screenshots_files(storage, app_obj)
    if has_combo:
        logger.info(
            f"app_id:{app_obj.app_id} has_combo ,delete this app need uncombo and clean del_cache_response_by_short")
        has_combo.has_combo = None
        has_combo.save(update_fields=['has_combo'])

    MagicCacheData.invalid_cache(app_obj.app_id)
    app_obj.delete()

    return res


def app_screen_delete(screen_id, apps_obj, storage):
    screen_obj = AppScreenShot.objects.filter(pk=screen_id, app_id=apps_obj).first()
    if screen_obj:
        storage.delete_file(screen_obj.screenshot_url)
        screen_obj.delete()
        del_cache_response_by_short(apps_obj.app_id)


def check_storage_ok(user_obj, new_storage_obj):
    if migrating_storage_file_data(user_obj, 'head_img.jpeg', new_storage_obj, False):
        return True


def storage_change(use_storage_id, user_obj, force):
    if use_storage_id:
        if user_obj.storage and use_storage_id == user_obj.storage.id:
            return True
    try:
        if use_storage_id == -1:
            if not check_storage_ok(user_obj, None):
                return False
            change_storage_and_change_head_img(user_obj, None)
            if migrating_storage_data(user_obj, None, False):
                if check_storage_is_new_storage(user_obj, None):
                    clean_storage_data(user_obj)
                UserInfo.objects.filter(pk=user_obj.pk).update(storage=None)
        else:
            new_storage_obj = AppStorage.objects.filter(pk=use_storage_id).first()
            if not check_storage_ok(user_obj, new_storage_obj):
                return False
            change_storage_and_change_head_img(user_obj, new_storage_obj)
            if migrating_storage_data(user_obj, new_storage_obj, False):
                if check_storage_is_new_storage(user_obj, new_storage_obj):
                    clean_storage_data(user_obj)
                UserInfo.objects.filter(pk=user_obj.pk).update(storage_id=use_storage_id)

    except Exception as e:
        logger.error(f"update user {user_obj} storage failed Exception:{e}")
        if force:
            if use_storage_id == -1:
                UserInfo.objects.filter(pk=user_obj.pk).update(storage=None)
            else:
                UserInfo.objects.filter(pk=user_obj.pk).update(storage_id=use_storage_id)
        else:
            return False
    del_cache_storage(user_obj)
    return True
