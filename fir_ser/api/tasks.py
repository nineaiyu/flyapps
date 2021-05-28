#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月 
# author: NinEveN
# date: 2021/5/27

from celery import shared_task
from django.core.cache import cache

from api.models import Apps
from api.utils.app.supersignutils import IosUtils, resign_by_app_id


@shared_task
def run_sign_task(format_udid_info, short):
    app_info = Apps.objects.filter(short=short).first()
    with cache.lock("%s_%s_%s" % ('task_sign', app_info.app_id, format_udid_info.get('udid')), timeout=60 * 10):
        ios_obj = IosUtils(format_udid_info, app_info.user_id, app_info)
        status, msg = ios_obj.sign()
        if not status:
            code = msg.get("code", -1)
            if code == 0:
                msg = ""
            elif code == 1005:
                msg = "签名余额不足"
            elif code == 1002:
                msg = "维护中"
            elif code == 1003:
                msg = "应用余额不足"
            elif code in [1004, 1001, 1009]:
                msg = msg.get('msg', '未知错误')
            else:
                msg = '系统内部错误'
        else:
            msg = ""
        return msg


@shared_task
def run_resign_task(app_id, need_download_profile=True):
    app_obj = Apps.objects.filter(app_id=app_id).first()
    with cache.lock("%s_%s" % ('task_resign', app_id), timeout=60 * 60):
        return resign_by_app_id(app_obj, need_download_profile)
