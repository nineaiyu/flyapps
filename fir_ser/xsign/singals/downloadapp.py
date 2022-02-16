#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: NinEveN
# date: 2022/2/15
import logging

from django.dispatch import Signal, receiver

from api.models import AppReleaseInfo
from common.core.sysconfig import Config
from common.libs.storage.localApi import LocalStorage
from xsign.models import AppUDID, APPToDeveloper, APPSuperSignUsedInfo

logger = logging.getLogger(__name__)

"""
xsign 下载连接
"""

xsign_app_download_url_signal = Signal(providing_args=["app_pk", "udid", "download_url_type", "limit"])


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
