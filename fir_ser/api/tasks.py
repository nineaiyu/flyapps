#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月 
# author: NinEveN
# date: 2021/5/27

import logging

from captcha.models import CaptchaStore

from api.utils.ctasks import sync_download_times, auto_clean_upload_tmp_file, auto_clean_remote_client_log, \
    notify_check_user_download_times, notify_check_apple_developer_devices, notify_check_apple_developer_cert
from api.views.login import get_login_type
from common.core.sysconfig import Config, ConfigCacheBase
from common.libs.geetest.geetest_utils import check_bypass_status
from common.libs.mp.wechat import sync_wx_access_token
from common.utils.storage import get_local_storage
from fir_ser.celery import app
from xsign.utils.ctasks import auto_delete_ios_mobile_tmp_file

logger = logging.getLogger(__name__)


@app.task
def start_api_sever_do_clean():
    # 启动服务的时候，同时执行下面操作,主要是修改配置存储的时候，需要执行清理，否则会出问题，如果不修改，则无需执行
    logger.info("clean local storage cache")
    get_local_storage(clean_cache=True)
    check_bypass_status()
    ConfigCacheBase().invalid_config_cache()


def clean_config_cache(key):
    ConfigCacheBase().invalid_config_cache(key)


@app.task
def sync_download_times_job():
    sync_download_times()


@app.task
def check_bypass_status_job():
    if Config.LOGIN.get("geetest") or Config.CHANGER.get('geetest') or Config.REGISTER.get(
            'geetest') or Config.REPORT.get('geetest'):
        check_bypass_status()


@app.task
def auto_clean_upload_tmp_file_job():
    auto_clean_upload_tmp_file()


@app.task
def auto_clean_captcha_store_job():
    CaptchaStore.remove_expired()


@app.task
def auto_delete_tmp_file_job():
    auto_delete_ios_mobile_tmp_file()


@app.task
def sync_wx_access_token_job():
    if get_login_type().get('third', '').get('wxp'):
        sync_wx_access_token()


@app.task
def auto_clean_remote_client_job():
    auto_clean_remote_client_log()


@app.task
def download_times_notify_check_job():
    notify_check_user_download_times()


@app.task
def apple_developer_devices_check_job():
    notify_check_apple_developer_devices()


@app.task
def apple_developer_cert_notify_check_job():
    notify_check_apple_developer_cert()
