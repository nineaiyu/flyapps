#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月 
# author: NinEveN
# date: 2021/5/27

import logging

from celery import shared_task
from django.core.cache import cache

from common.cache.state import MigrateStorageState
from fir_ser.celery import app
from xsign.models import Apps, DeveloperAppID
from xsign.utils.ctasks import auto_check_ios_developer_active, auto_clean_sign_log
from xsign.utils.iproxy import get_best_proxy_ips
from xsign.utils.modelutils import add_sign_message
from xsign.utils.supersignutils import IosUtils, resign_by_app_id_and_developer

logger = logging.getLogger(__name__)


@shared_task
def run_sign_task(format_udid_info, short, client_ip):
    app_obj = Apps.objects.filter(short=short).first()
    user_obj = app_obj.user_id
    udid = format_udid_info.get('udid')
    if MigrateStorageState(user_obj.uid).get_state():
        msg = "数据迁移中，无法处理该操作"
        code = 1000
        return {'code': code, 'msg': msg}
    try:
        ios_sign_obj = IosUtils(format_udid_info, user_obj, app_obj)
        status, result = ios_sign_obj.sign_ipa(client_ip)
        if ios_sign_obj.developer_obj:
            if status:
                message = f"sign_info:[client_ip:{client_ip} udid:{udid}] raw_info:[{result}]"
                add_sign_message(user_obj, ios_sign_obj.developer_obj, app_obj, '签名成功', message, True)
    except Exception as e:
        logger.error(
            f"run_sign_task failed. client_ip:{client_ip} udid_info:{format_udid_info} app_obj:{app_obj} Exception:{e}")
        msg = '系统内部错误,请稍后再试或联系管理员'
        code = 5000
        return {'code': code, 'msg': msg}
    if not status:
        code = result.get("code", -1)
        if code == 1000:
            msg = ""
        elif code == 1005:
            msg = "签名余额不足"
        elif code == 1003:
            msg = "应用余额不足"
        elif code == 1007:
            msg = "设备注册中，请耐心等待"
        elif code in [1004, 1001, 1009]:
            msg = result.get('msg', '未知错误')
        else:
            code = 5000
            msg = '系统内部错误,请稍后再试或联系管理员'
        message = f"return_info:[client_ip:{client_ip},code:{code},msg:{msg},udid:{udid}] raw_info:[{result}]"
        if ios_sign_obj.developer_obj:
            add_sign_message(user_obj, ios_sign_obj.developer_obj, app_obj, '签名失败了', message, False)
        else:
            logger.error(f"[client_ip:{client_ip}] {user_obj} {app_obj} 签名失败了:{message}")
    else:
        msg = ""
        code = 1000
    result = {'code': code, 'msg': msg}
    if app_obj.supersign_redirect_url and (code == 1005 or (code == 1007 and app_obj.abnormal_redirect)):
        result['redirect'] = app_obj.supersign_redirect_url
    return result


def run_resign_task(app_id, need_download_profile=True, force=True, developers_filter=None):
    if developers_filter is None:
        developers_filter = []
    app_obj = Apps.objects.filter(pk=app_id).first()
    if app_obj.issupersign and app_obj.user_id.supersign_active:
        developer_app_id_queryset = DeveloperAppID.objects.filter(app_id=app_obj)
        if developers_filter:
            developer_app_id_queryset = developer_app_id_queryset.filter(developerid__in=developers_filter)

        with cache.lock(f"task_resign_{app_obj.app_id}", timeout=60 * 60):
            task_list = []
            for developer_app_id_obj in developer_app_id_queryset.all():
                c_task = run_resign_task_do.apply_async((app_id, developer_app_id_obj.developerid.pk,
                                                         developer_app_id_obj.aid, need_download_profile, force))
                task_list.append(c_task)
            for c_task in task_list:
                msg = c_task.get(propagate=False)
                logger.info(f"app {app_obj} run_resign_task msg:{msg}")
                if c_task.successful():
                    c_task.forget()
    return True


@shared_task
def run_resign_task_do(app_id, developer_id, developer_app_id, need_download_profile=True, force=True):
    return resign_by_app_id_and_developer(app_id, developer_id, developer_app_id, need_download_profile, force)


@app.task
def auto_check_ios_developer_active_job():
    return auto_check_ios_developer_active()


@app.task
def get_best_proxy_ips_job():
    return get_best_proxy_ips()


@app.task
def auto_clean_sign_log_job():
    return auto_clean_sign_log()
