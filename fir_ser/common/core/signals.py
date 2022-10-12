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
run_resign_task_signal = Signal()

"""
删除应用时的信号，用户清理签名相关数据
"""

delete_app_signal = Signal()

"""
下载超级签名数据
"""
xsign_app_download_url_signal = Signal()

"""
迁移超级签名数据
"""
xsign_migrate_data_signal = Signal()

"""
清理超级签名数据
"""
xsign_clean_data_signal = Signal()

"""
根据binary_file获取签名应用数据
"""
xsign_app_release_obj_signal = Signal()
