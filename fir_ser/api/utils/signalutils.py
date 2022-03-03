#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2022/3/3
from common.core.signals import run_resign_task_signal, delete_app_signal, xsign_app_download_url_signal, \
    xsign_migrate_data_signal, xsign_clean_data_signal, xsign_app_release_obj_signal


def run_signal_resign_utils(app_obj):
    return run_resign_task_signal.send(sender=None, app_obj=app_obj)


def run_delete_app_signal(app_obj):
    return delete_app_signal.send(None, app_pk=app_obj)


def run_xsign_app_download_url(app_obj, udid, download_url_type, limit):
    return xsign_app_download_url_signal.send(None, app_pk=app_obj.get('pk'), udid=udid,
                                              download_url_type=download_url_type, limit=limit)[0][1]


def run_xsign_migrate_data(app_release_obj, user_obj, new_storage_obj, clean_old_data):
    return xsign_migrate_data_signal.send(None, app_release_obj=app_release_obj, user_obj=user_obj,
                                          new_storage_obj=new_storage_obj, clean_old_data=clean_old_data)


def run_xsign_clean_data(app_release_obj, storage_obj):
    return xsign_clean_data_signal.send(None, app_release_obj=app_release_obj, storage_obj=storage_obj)


def run_get_xsign_binary_file(binary_file):
    return xsign_app_release_obj_signal.send(None, binary_file=binary_file)[0][1]
