#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6

import logging
import os

from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Apps, AppReleaseInfo
from api.utils.modelutils import get_filename_form_file, check_app_domain_name_access, \
    ad_random_weight, get_app_download_uri
from api.utils.response import BaseResponse
from api.utils.serializer import AppsShortSerializer, AppAdInfoSerializer
from common.base.baseutils import get_origin_domain_name, format_get_uri, make_random_uuid, make_resigned
from common.core.decorators import cache_response  # 本来使用的是 drf-extensions==0.7.0 但是还未支持该版本Django
from common.core.response import mobileprovision_file_response, file_response, ApiResponse
from common.core.sysconfig import Config
from common.core.throttle import VisitShortThrottle, InstallShortThrottle, InstallThrottle1, InstallThrottle2
from common.utils.caches import check_app_permission
from common.utils.download import get_app_download_url
from common.utils.storage import Storage, get_local_storage
from common.utils.token import verify_token
from fir_ser import settings

logger = logging.getLogger(__name__)


class DownloadView(APIView):
    """
    文件下载接口,适用于本地存储和所有plist文件下载
    """

    def get(self, request, filename):
        res = BaseResponse()
        down_token = request.query_params.get(settings.DATA_DOWNLOAD_KEY, None)
        f_type = filename.split(".")[-1]
        flag = True
        storage_obj = get_local_storage()
        if storage_obj.download_auth_type == 1:
            if not down_token:
                res.code = 1004
                res.msg = "缺失token"
                logger.error(f"file {filename} download failed lost down_token")
                return Response(res.dict)

            flag = verify_token(down_token, filename)

        if flag:
            if f_type == 'plist':
                release_id = filename.split('.')[0]
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
            elif f_type == 'dmobileprovision':  # 企业签名安装信任跳转
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    file_path = Config.DEFAULT_MOBILEPROVISION.get("enterprise").get('path')
                    if file_path and os.path.isfile(file_path):
                        return mobileprovision_file_response(file_path)
                res.msg = "d_mobile_provision release_id error"
            else:
                file_path = os.path.join(settings.MEDIA_ROOT, filename)
                try:
                    if os.path.isfile(file_path):
                        return FileResponse(open(file_path, 'rb'), as_attachment=True,
                                            filename=get_filename_form_file(filename))
                except Exception as e:
                    logger.error(f"read {file_path} failed  Exception:{e}")

        res.code = 1004
        res.msg = "token校验失败"
        logger.error(f"file {filename} download failed. down_token verify failed")
        return Response(res.dict)


class ShortDownloadView(APIView):
    throttle_classes = [VisitShortThrottle, InstallShortThrottle]
    '''
    根据下载短链接，获取应用信息
    '''

    @cache_response(timeout=600 - 60, cache="default", key_func='calculate_cache_key', cache_errors=False)
    def get(self, request, short):
        res = BaseResponse()
        release_id = request.query_params.get("release_id", None)
        udid = request.query_params.get("udid", None)
        app_obj = Apps.objects.filter(short=short).first()
        user_obj = None
        if app_obj:
            user_obj = app_obj.user_id
        res = check_app_permission(app_obj, res, user_obj)
        if res.code != 1000:
            return Response(res.dict)
        domain_name = get_app_download_uri(request, user_obj, app_obj, False)
        origin_domain_name = get_origin_domain_name(request)
        logger.info(f"app_obj:{app_obj.__dict__} domain_name:{domain_name}  origin_domain_name:{origin_domain_name}")
        if user_obj and user_obj.role and user_obj.role == 3:
            ...
        else:
            if not check_app_domain_name_access(app_obj, origin_domain_name, user_obj,
                                                domain_name.split('//')[-1]):
                res.code = 1004
                res.msg = "访问域名不合法"
                return Response(res.dict)
        if domain_name.split('//')[-1].split('/')[0] != origin_domain_name:
            res.code = 1000
            res.domain_name = domain_name
            res.redirect = True
            res.data = format_get_uri(domain_name, short, {'release_id': release_id, 'udid': udid})
            return Response(res.dict)
        if udid:
            if not app_obj.issupersign:
                res.code = 1002
                res.msg = "参数有误"
                return Response(res.dict)
            # del_cache_response_by_short(app_obj.app_id, udid=udid)

        app_serializer = AppsShortSerializer(app_obj, context={"key": "ShortDownloadView", "release_id": release_id,
                                                               "storage": Storage(user_obj)})
        res.data = app_serializer.data
        res.udid = udid
        res.domain_name = domain_name
        if user_obj and user_obj.role and user_obj.role > 1:
            ad_obj = ad_random_weight(user_obj)
            if ad_obj:
                res.ad = AppAdInfoSerializer(ad_obj, context={"key": "ShortDownloadView", "short": short}).data
        return Response(res.dict)

    # key的设置
    def calculate_cache_key(self, view_instance, view_method,
                            request, args, kwargs):
        release_id = request.query_params.get("release_id", '')
        udid = request.query_params.get("udid", '')
        short = kwargs.get("short", '')
        origin_name = get_origin_domain_name(request)
        if not origin_name:
            origin_name = 'default.site'
        logging.info(f"cache_response short:{short} origin_domain_name:{origin_name} release_id:{release_id}")
        return "_".join([settings.CACHE_KEY_TEMPLATE.get("download_short_key"), short, origin_name, release_id, udid])


class InstallView(APIView):
    throttle_classes = [InstallThrottle1, InstallThrottle2]
    '''
    安装操作，前端通过token 认证，认证成功之后，返回 下载连接，并且 让下载次数加一
    '''

    def get(self, request, app_id):
        res = BaseResponse()
        query_params = request.query_params
        downtoken = query_params.get("token", None)
        short = query_params.get("short", None)
        release_id = query_params.get("release_id", None)
        isdownload = query_params.get("isdownload", None)
        password = query_params.get("password", None)
        udid = query_params.get("udid", None)

        if not downtoken or not short or not release_id or not app_id:
            res.code = 1004
            res.msg = "参数丢失"
            return Response(res.dict)

        if verify_token(downtoken, release_id):
            res = get_app_download_url(request, res, app_id, short, password, release_id, isdownload, udid)
        else:
            res.code = 1004
            res.msg = "token校验失败"
        return Response(res.dict)
