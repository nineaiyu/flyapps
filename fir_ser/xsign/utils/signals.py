#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: NinEveN
# date: 2022/2/15
import logging

from django.dispatch import receiver

from api.models import AppReleaseInfo
from api.utils.utils import migrating_storage_file_data, get_filename_from_apptype
from common.core.signals import run_resign_task_signal, delete_app_signal, xsign_app_download_url_signal, \
    xsign_migrate_data_signal, xsign_clean_data_signal, xsign_app_release_obj_signal
from common.core.sysconfig import Config
from common.libs.storage.localApi import LocalStorage
from xsign.models import AppUDID, APPToDeveloper, APPSuperSignUsedInfo
from xsign.tasks import run_resign_task
from xsign.utils.modelutils import get_filename_form_file
from xsign.utils.supersignutils import IosUtils

logger = logging.getLogger(__name__)

"""
更新应用的时候，是否同时更新超级签名数据
"""


@receiver(run_resign_task_signal)
def run_resign_task_callback(sender, **kwargs):
    app_obj = kwargs.get('app_obj')
    if app_obj:
        AppUDID.objects.filter(app_id=app_obj, sign_status__gte=3).update(sign_status=3)
        if app_obj.change_auto_sign:
            c_task = run_resign_task(app_obj.pk, False, False)
            logger.info(f"app {app_obj} run_resign_task end msg:{c_task}")
    return 'success'


"""
删除应用时的信号，用户清理签名相关数据
"""


@receiver(delete_app_signal)
def delete_app_callback(sender, **kwargs):
    app_obj = kwargs.get('app_obj')
    if app_obj:
        count = APPToDeveloper.objects.filter(app_id=app_obj).count()
        if app_obj.issupersign or count > 0:
            logger.info(f"app_id:{app_obj.app_id} is supersign ,delete this app need clean IOS developer")
            IosUtils.clean_app_by_user_obj(app_obj)


"""
下载超级签名数据
"""


@receiver(xsign_app_download_url_signal)
def xsign_app_download_url_callback(sender, **kwargs):
    udid = kwargs.get('udid')
    download_url_type = kwargs.get('download_url_type')
    limit = kwargs.get('limit')
    app_pk = kwargs.get('app_pk')

    local_storage = LocalStorage(**Config.IOS_PMFILE_DOWNLOAD_DOMAIN)
    appudid_obj = AppUDID.objects.filter(app_id_id=app_pk, udid__udid=udid, sign_status=4).last()
    if appudid_obj:
        super_sign_obj = APPSuperSignUsedInfo.objects.filter(udid__udid__udid=udid,
                                                             app_id_id=app_pk,
                                                             developerid__status__in=Config.DEVELOPER_USE_STATUS).last()
        if super_sign_obj and super_sign_obj.user_id.supersign_active:
            app_to_developer_obj = APPToDeveloper.objects.filter(app_id_id=app_pk,
                                                                 developerid=super_sign_obj.developerid).last()
            if app_to_developer_obj:
                release_obj = AppReleaseInfo.objects.filter(app_id_id=app_pk, is_master=True).last()
                if release_obj.release_id == app_to_developer_obj.release_file:
                    binary_file = app_to_developer_obj.binary_file
                else:
                    binary_file = app_to_developer_obj.release_file
                return local_storage.get_download_url(
                    binary_file + "." + download_url_type, limit, is_xsign=True), ""
            else:
                return "", ""
        else:
            return "", ""
    else:
        return "", ""


"""
迁移超级签名数据
"""


@receiver(xsign_migrate_data_signal)
def xsign_migrate_data_signal_callback(sender, **kwargs):
    app_release_obj = kwargs.get('app_release_obj')
    user_obj = kwargs.get('user_obj')
    new_storage_obj = kwargs.get('new_storage_obj')
    clean_old_data = kwargs.get('clean_old_data')
    for apptodev_obj in APPToDeveloper.objects.filter(app_id=app_release_obj.app_id).all():
        filename = get_filename_from_apptype(apptodev_obj.binary_file, app_release_obj.release_type)
        migrating_storage_file_data(user_obj, filename, new_storage_obj, clean_old_data)


"""
清理超级签名数据
"""


@receiver(xsign_clean_data_signal)
def xsign_clean_data_signal_callback(sender, **kwargs):
    app_release_obj = kwargs.get('app_release_obj')
    storage_obj = kwargs.get('storage_obj')
    for apptodev_obj in APPToDeveloper.objects.filter(app_id=app_release_obj.app_id).all():
        storage_obj.delete_file(apptodev_obj.binary_file, app_release_obj.release_type)


"""
根据binary_file获取签名应用数据
"""


@receiver(xsign_app_release_obj_signal)
def xsign_app_release_obj_signal_callback(sender, **kwargs):
    binary_file = kwargs.get('binary_file')
    return get_filename_form_file(binary_file)


def main():
    logger.info('signal receiver init success')
