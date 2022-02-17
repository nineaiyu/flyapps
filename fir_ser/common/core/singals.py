#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: NinEveN
# date: 2022/2/15
import logging

from django.dispatch import Signal

logger = logging.getLogger(__name__)

"""
更新应用的时候，是否同时更新超级签名数据
"""
run_resign_task_signal = Signal(providing_args=["app_pk"])

"""
删除应用时的信号，用户清理签名相关数据
"""

delete_app_signal = Signal(providing_args=["app_pk"])

"""
下载超级签名数据
"""
xsign_app_download_url_signal = Signal(providing_args=["app_pk", "udid", "download_url_type", "limit"])
