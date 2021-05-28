#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2021/4/13

from api.utils.response import BaseResponse

from api.utils.app.supersignutils import IosUtils
from api.utils.storage.storage import Storage
from api.utils.storage.caches import del_cache_response_by_short, get_app_today_download_times, del_cache_by_delete_app, \
    del_cache_storage
from api.models import Apps, AppReleaseInfo, APPToDeveloper, AppIOSDeveloperInfo, UserInfo, AppScreenShot, AppStorage
import logging
from api.utils.utils import delete_local_files, delete_app_screenshots_files, change_storage_and_change_head_img, \
    migrating_storage_data, clean_storage_data, check_storage_is_new_storage

logger = logging.getLogger(__name__)


def app_delete(app_obj):
    res = BaseResponse()
    if not app_obj:
        res.code = 1001
        res.msg = "应用不存在"
        return res
    user_obj = app_obj.user_id
    count = APPToDeveloper.objects.filter(app_id=app_obj).count()
    if app_obj.issupersign or count > 0:
        logger.info("app_id:%s is supersign ,delete this app need clean IOS developer" % (app_obj.app_id))
        IosUtils.clean_app_by_user_obj(app_obj, user_obj)

    storage = Storage(user_obj)
    has_combo = app_obj.has_combo
    if has_combo:
        logger.info(
            "app_id:%s has_combo ,delete this app need uncombo and clean del_cache_response_by_short" % (
                app_obj.app_id))
        has_combo.has_combo = None
    del_cache_response_by_short(app_obj.app_id)
    del_cache_by_delete_app(app_obj.app_id)
    for app_release_obj in AppReleaseInfo.objects.filter(app_id=app_obj).all():
        logger.info("delete app_id:%s  need clean all release,release_id:%s" % (
            app_obj.app_id, app_release_obj.release_id))
        storage.delete_file(app_release_obj.release_id, app_release_obj.release_type)
        delete_local_files(app_release_obj.release_id, app_release_obj.release_type)
        storage.delete_file(app_release_obj.icon_url)
        app_release_obj.delete()
    delete_app_screenshots_files(storage, app_obj)
    app_obj.delete()

    return res


def app_screen_delete(screen_id, apps_obj, storage):
    screen_obj = AppScreenShot.objects.filter(pk=screen_id, app_id=apps_obj).first()
    if screen_obj:
        storage.delete_file(screen_obj.screenshot_url)
        screen_obj.delete()
        del_cache_response_by_short(apps_obj.app_id)


def app_release_delete(app_obj, release_id, storage):
    res = BaseResponse()
    user_obj = app_obj.user_id
    if app_obj:
        apprelease_count = AppReleaseInfo.objects.filter(app_id=app_obj).values("release_id").count()
        appreleaseobj = AppReleaseInfo.objects.filter(app_id=app_obj, release_id=release_id).first()
        if not appreleaseobj.is_master:
            logger.info("delete app release %s" % (appreleaseobj))
            storage.delete_file(appreleaseobj.release_id, appreleaseobj.release_type)
            delete_local_files(appreleaseobj.release_id, appreleaseobj.release_type)
            storage.delete_file(appreleaseobj.icon_url)

            appreleaseobj.delete()
        elif appreleaseobj.is_master and apprelease_count < 2:
            logger.info("delete app master release %s and clean app %s " % (appreleaseobj, app_obj))
            count = APPToDeveloper.objects.filter(app_id=app_obj).count()
            if app_obj.issupersign or count > 0:
                logger.info("app_id:%s is supersign ,delete this app need clean IOS developer" % (app_obj.app_id))
                IosUtils.clean_app_by_user_obj(app_obj, user_obj)

            storage.delete_file(appreleaseobj.release_id, appreleaseobj.release_type)
            delete_local_files(appreleaseobj.release_id, appreleaseobj.release_type)
            storage.delete_file(appreleaseobj.icon_url)
            del_cache_by_delete_app(app_obj.app_id)

            appreleaseobj.delete()
            delete_app_screenshots_files(storage, app_obj)
            has_combo = app_obj.has_combo
            if has_combo:
                app_obj.has_combo.has_combo = None
            app_obj.delete()
        else:
            pass
        del_cache_response_by_short(app_obj.app_id)

    return res


def storage_change(use_storage_id, user_obj, force):
    if use_storage_id:
        if user_obj.storage and use_storage_id == user_obj.storage.id:
            return True
    try:
        if use_storage_id == -1:
            change_storage_and_change_head_img(user_obj, None)
            if migrating_storage_data(user_obj, None, False):
                if check_storage_is_new_storage(user_obj, None):
                    clean_storage_data(user_obj)
                UserInfo.objects.filter(pk=user_obj.pk).update(storage=None)
        else:
            new_storage_obj = AppStorage.objects.filter(pk=use_storage_id).first()
            change_storage_and_change_head_img(user_obj, new_storage_obj)
            if migrating_storage_data(user_obj, new_storage_obj, False):
                if check_storage_is_new_storage(user_obj, new_storage_obj):
                    clean_storage_data(user_obj)
                UserInfo.objects.filter(pk=user_obj.pk).update(storage_id=use_storage_id)

    except Exception as e:
        logger.error("update user %s storage failed Exception:%s" % (user_obj, e))
        if force:
            if use_storage_id == -1:
                UserInfo.objects.filter(pk=user_obj.pk).update(storage=None)
            else:
                UserInfo.objects.filter(pk=user_obj.pk).update(storage_id=use_storage_id)
        else:
            return False
    del_cache_storage(user_obj)

    return True
