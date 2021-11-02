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

from api.models import Apps, AppReleaseInfo, APPToDeveloper, APPSuperSignUsedInfo
from api.utils.TokenManager import verify_token
from api.utils.app.apputils import make_resigned
from api.utils.app.supersignutils import make_sign_udid_mobile_config
from api.utils.baseutils import get_profile_full_path, make_random_uuid, get_real_ip_address, get_origin_domain_name, \
    format_get_uri, get_post_udid_url
from api.utils.decorators import cache_response  # 本来使用的是 drf-extensions==0.7.0 但是还未支持该版本Django
from api.utils.modelutils import get_app_domain_name, get_filename_form_file, check_app_domain_name_access, \
    ad_random_weight, get_redirect_server_domain, add_remote_info_from_request
from api.utils.response import BaseResponse
from api.utils.serializer import AppsShortSerializer, AppAdInfoSerializer
from api.utils.storage.caches import get_app_instance_by_cache, get_download_url_by_cache, set_app_download_by_cache, \
    del_cache_response_by_short, consume_user_download_times, check_app_permission
from api.utils.storage.storage import Storage, get_local_storage
from api.utils.throttle import VisitShortThrottle, InstallShortThrottle, InstallThrottle1, InstallThrottle2
from fir_ser import settings

logger = logging.getLogger(__name__)


def file_response(stream, filename, content_type):
    return FileResponse(stream, as_attachment=True,
                        filename=filename,
                        content_type=content_type)


def mobileprovision_file_response(file_path):
    return file_response(open(file_path, 'rb'), make_random_uuid() + '.mobileprovision',
                         "application/x-apple-aspen-config")


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
                app_to_developer_obj = APPToDeveloper.objects.filter(binary_file=release_id).first()
                if app_to_developer_obj:
                    release_obj = AppReleaseInfo.objects.filter(is_master=True,
                                                                app_id=app_to_developer_obj.app_id).first()
                else:
                    release_obj = AppReleaseInfo.objects.filter(release_id=release_id).first()
                if release_obj:
                    storage = Storage(release_obj.app_id.user_id)
                    bundle_id = release_obj.app_id.bundle_id
                    app_version = release_obj.app_version
                    name = release_obj.app_id.name
                    ios_plist_bytes = make_resigned(storage.get_download_url(filename.split('.')[0] + ".ipa"),
                                                    storage.get_download_url(release_obj.icon_url), bundle_id,
                                                    app_version, name)
                    return file_response(ios_plist_bytes, make_random_uuid(), "application/x-plist")
                res.msg = "plist release_id error"
            elif f_type == 'mobileconifg':
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    app_obj = release_obj.app_id
                    udid_url = get_post_udid_url(request, app_obj.short)
                    ios_udid_mobile_config = make_sign_udid_mobile_config(udid_url, f'{app_obj.app_id}_{app_obj.short}',
                                                                          app_obj.bundle_id,
                                                                          app_obj.name)
                    return file_response(ios_udid_mobile_config, make_random_uuid() + '.mobileconfig',
                                         "application/x-apple-aspen-config")
                res.msg = "mobile_config release_id error"
            elif f_type == 'mobileprovision':
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    app_super_obj = APPSuperSignUsedInfo.objects.filter(app_id=release_obj.app_id).last()
                    if not app_super_obj:
                        app_super_obj = APPSuperSignUsedInfo.objects.last()

                    if not app_super_obj:
                        file_path = settings.DEFAULT_MOBILEPROVISION.get("supersign").get('path')
                        if file_path and os.path.isfile(file_path):
                            return mobileprovision_file_response(file_path)
                    else:
                        developer_obj = app_super_obj.developerid
                        file_path = get_profile_full_path(developer_obj, release_obj.app_id)
                        if os.path.isfile(file_path):
                            return mobileprovision_file_response(file_path)
                        else:
                            file_path = settings.DEFAULT_MOBILEPROVISION.get("supersign").get('path')
                            if file_path and os.path.isfile(file_path):
                                return mobileprovision_file_response(file_path)

                res.msg = "mobile_provision release_id error"
            elif f_type == 'dmobileprovision':  # 企业签名安装信任跳转
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    file_path = settings.DEFAULT_MOBILEPROVISION.get("enterprise").get('path')
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
        domain_name = get_redirect_server_domain(request, user_obj, get_app_domain_name(app_obj))
        origin_domain_name = get_origin_domain_name(request)
        if domain_name.split('//')[-1].split('/')[0] != origin_domain_name:
            res.code = 302
            res.data = format_get_uri(domain_name, short, {'release_id': release_id, 'udid': udid})
            return Response(res.dict)

        if user_obj and user_obj.role and user_obj.role == 3:
            ...
        else:
            if not check_app_domain_name_access(app_obj, origin_domain_name, user_obj,
                                                domain_name.split('//')[-1]):
                res.code = 1004
                res.msg = "访问域名不合法"
                return Response(res.dict)
        if udid:
            if not app_obj.issupersign:
                res.code = 1002
                res.msg = "参数有误"
                return Response(res.dict)
            del_cache_response_by_short(app_obj.app_id, udid=udid)

        app_serializer = AppsShortSerializer(app_obj, context={"key": "ShortDownloadView", "release_id": release_id,
                                                               "storage": Storage(user_obj)})
        res.data = app_serializer.data
        res.udid = udid
        res.domain_name = domain_name
        if user_obj and user_obj.role and user_obj.role > 1:
            res.ad = AppAdInfoSerializer(ad_random_weight(user_obj), context={"key": "ShortDownloadView"}).data
        return Response(res.dict)

    # key的设置
    def calculate_cache_key(self, view_instance, view_method,
                            request, args, kwargs):
        release_id = request.query_params.get("release_id", '')
        udid = request.query_params.get("udid", None)
        time = request.query_params.get("time", None)
        origin_domain_name = get_origin_domain_name(request)
        if not origin_domain_name:
            origin_domain_name = 'default.site'
        if udid and time:
            udid = time
        if not udid:
            udid = ""
        logging.info(
            f"get or make cache_response short:{kwargs.get('short', '')} origin_domain_name:{origin_domain_name} release_id:{release_id} udid:{udid}")
        return "_".join(
            [settings.CACHE_KEY_TEMPLATE.get("download_short_key"), kwargs.get("short", ''), origin_domain_name,
             release_id, udid])


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

        if not downtoken or not short or not release_id:
            res.code = 1004
            res.msg = "参数丢失"
            return Response(res.dict)

        if verify_token(downtoken, release_id):
            app_obj = get_app_instance_by_cache(app_id, password, 900, udid)
            if app_obj:
                if app_obj.get("type") == 0:
                    app_type = '.apk'
                    download_url, extra_url = get_download_url_by_cache(app_obj, release_id + app_type, 600)
                else:
                    app_type = '.ipa'
                    if isdownload:
                        download_url, extra_url = get_download_url_by_cache(app_obj, release_id + app_type, 600,
                                                                            udid=udid)
                    else:
                        download_url, extra_url = get_download_url_by_cache(app_obj, release_id + app_type, 600,
                                                                            isdownload,
                                                                            udid=udid)

                res.data = {"download_url": download_url, "extra_url": extra_url}
                if download_url != "" and "mobileconifg" not in download_url:
                    ip = get_real_ip_address(request)
                    msg = f"remote ip {ip} short {short} download_url {download_url} app_obj {app_obj}"
                    logger.info(msg)
                    add_remote_info_from_request(request, msg)
                    set_app_download_by_cache(app_id)
                    amount = app_obj.get("d_count")
                    # # 超级签需要多消耗2倍下载次数
                    # if app_obj.get("issupersign"):
                    #     amount *= 2
                    auth_status = False
                    status = app_obj.get('user_id__certification__status', None)
                    if status and status == 1:
                        auth_status = True
                    if not consume_user_download_times(app_obj.get("user_id"), app_id, amount, auth_status):
                        res.code = 1009
                        res.msg = "可用下载额度不足"
                        del res.data
                        return Response(res.dict)
                return Response(res.dict)
        else:
            res.code = 1004
            res.msg = "token校验失败"
            return Response(res.dict)

        res.code = 1006
        res.msg = "该应用不存在"
        return Response(res.dict)
