#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6

import logging
import os
import random
from urllib.parse import quote

from django.urls import reverse
from rest_framework.views import APIView

from api.models import AppReleaseInfo
from common.base.baseutils import get_profile_full_path, make_random_uuid, get_server_domain_from_request, make_resigned
from common.core.response import ApiResponse, file_response, mobileprovision_file_response
from common.core.sysconfig import Config
from common.utils.storage import Storage, get_local_storage
from common.utils.token import verify_token, make_token
from fir_ser import settings
from xsign.models import APPToDeveloper, APPSuperSignUsedInfo
from xsign.utils.supersignutils import make_sign_udid_mobile_config

logger = logging.getLogger(__name__)


def get_post_udid_url(request, app_obj, pwd):
    server_domain = get_server_domain_from_request(request, Config.POST_UDID_DOMAIN)
    p_token = make_token(app_obj.app_id, time_limit=120, key='post_udid', force_new=True)
    token = f'{p_token}{"".join(random.sample(p_token, 3))}{app_obj.app_id}{"".join(random.sample(p_token, 3))}{pwd}'
    logger.info(f'make udid: p_token:{p_token} app_id:{app_obj.app_id} pwd:{pwd}')
    logger.info(f'make udid: token:{token}')
    token = quote(token, safe='/', encoding=None, errors=None)
    return f'{server_domain}{reverse("xudid", kwargs={"short": app_obj.short})}?p={token}'


class XsignDownloadView(APIView):
    """
    文件下载接口,适用于本地存储和所有plist文件下载
    """

    def get(self, request, filename):
        down_token = request.query_params.get(settings.DATA_DOWNLOAD_KEY, None)
        password = request.query_params.get('password', '')
        f_type = filename.split(".")[-1]
        flag = True
        storage_obj = get_local_storage()
        if storage_obj.download_auth_type == 1:
            if not down_token:
                logger.error(f"file {filename} download failed lost down_token")
                return ApiResponse(code=1004, msg="缺失token")

            flag = verify_token(down_token, filename)

        if flag:
            if f_type == 'plist':
                release_id = filename.split('.')[0]
                app_to_developer_obj = APPToDeveloper.objects.filter(binary_file=release_id).first()
                if app_to_developer_obj:
                    release_obj = AppReleaseInfo.objects.filter(is_master=True,
                                                                app_id=app_to_developer_obj.app_id).first()
                else:
                    release_obj = AppReleaseInfo.objects.filter(release_id=release_id).first()
                if release_obj:
                    app_obj = release_obj.app_id
                    storage = Storage(app_obj.user_id)
                    bundle_id = app_obj.bundle_id
                    app_version = release_obj.app_version
                    name = app_obj.name
                    ios_plist_bytes = make_resigned(storage.get_download_url(filename.split('.')[0] + ".ipa"),
                                                    storage.get_download_url(release_obj.icon_url), bundle_id,
                                                    app_version, name)
                    return file_response(ios_plist_bytes, make_random_uuid(), "application/x-plist")
                return ApiResponse(code=1004, msg="plist release_id error")
            elif f_type == 'mobileconifg':
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    app_obj = release_obj.app_id
                    udid_url = get_post_udid_url(request, app_obj, password)
                    ios_udid_mobile_config = make_sign_udid_mobile_config(udid_url, app_obj.bundle_id, app_obj.name)
                    return file_response(ios_udid_mobile_config, make_random_uuid() + '.mobileconfig',
                                         "application/x-apple-aspen-config")
                return ApiResponse(code=1004, msg="mobile_config release_id error")
            elif f_type == 'mobileprovision':
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    app_super_obj = APPSuperSignUsedInfo.objects.filter(app_id=release_obj.app_id).last()
                    if not app_super_obj:
                        app_super_obj = APPSuperSignUsedInfo.objects.last()

                    if not app_super_obj:
                        file_path = Config.DEFAULT_MOBILEPROVISION.get("supersign").get('path')
                        if file_path and os.path.isfile(file_path):
                            return mobileprovision_file_response(file_path)
                    else:
                        developer_obj = app_super_obj.developerid
                        file_path = get_profile_full_path(developer_obj, release_obj.app_id)
                        if os.path.isfile(file_path):
                            return mobileprovision_file_response(file_path)
                        else:
                            file_path = Config.DEFAULT_MOBILEPROVISION.get("supersign").get('path')
                            if file_path and os.path.isfile(file_path):
                                return mobileprovision_file_response(file_path)

                return ApiResponse(code=1004, msg="mobile_provision release_id error")
            else:
                logger.warning("super sing error file type")

        logger.error(f"file {filename} download failed. down_token verify failed")
        return ApiResponse(code=1004, msg="token校验失败")
