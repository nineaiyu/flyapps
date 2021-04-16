#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6
from rest_framework.views import APIView
from api.utils.response import BaseResponse
from rest_framework.response import Response
from fir_ser import settings
from api.utils.TokenManager import DownloadToken
from api.utils.app.randomstrings import make_random_uuid
from api.utils.app.apputils import make_resigned
from api.utils.app.supersignutils import make_sign_udid_mobileconfig, get_post_udid_url, get_redirect_server_domain
from api.utils.storage.storage import Storage, get_local_storage
from api.utils.storage.caches import get_app_instance_by_cache, get_download_url_by_cache, set_app_download_by_cache, \
    del_cache_response_by_short, consume_user_download_times, check_user_has_all_download_times
import os
from rest_framework_extensions.cache.decorators import cache_response
from api.utils.serializer import AppsShortSerializer
from api.models import Apps, AppReleaseInfo, APPToDeveloper, APPSuperSignUsedInfo
from django.http import FileResponse
import logging
from api.utils.baseutils import get_profile_full_path
from api.utils.throttle import VisitShortThrottle, InstallShortThrottle

logger = logging.getLogger(__file__)


class DownloadView(APIView):
    '''
    文件下载接口,适用于本地存储和所有plist文件下载
    '''

    def get(self, request, filename):
        res = BaseResponse()
        downtoken = request.query_params.get(settings.DATA_DOWNLOAD_KEY, None)
        ftype = filename.split(".")[-1]
        flag = True
        storage_obj = get_local_storage()
        if storage_obj.download_auth_type == 1:
            if not downtoken:
                res.code = 1004
                res.msg = "缺失token"
                return Response(res.dict)

            dtoken = DownloadToken()
            flag = dtoken.verify_token(downtoken, filename)

        if flag:
            if ftype == 'plist':
                release_id = filename.split('.')[0]
                apptodev_obj = APPToDeveloper.objects.filter(binary_file=release_id).first()
                if apptodev_obj:
                    release_obj = AppReleaseInfo.objects.filter(is_master=True, app_id=apptodev_obj.app_id).first()
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
                    response = FileResponse(ios_plist_bytes)
                    response['Content-Type'] = "application/x-plist"
                    response['Content-Disposition'] = 'attachment; filename=' + make_random_uuid()
                    return response
                res.msg = "plist release_id error"
            elif ftype == 'mobileconifg':
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    bundle_id = release_obj.app_id.bundle_id
                    udid_url = get_post_udid_url(request, release_obj.app_id.short)
                    ios_udid_mobileconfig = make_sign_udid_mobileconfig(udid_url, bundle_id, release_obj.app_id.name)
                    response = FileResponse(ios_udid_mobileconfig)
                    response['Content-Type'] = "application/x-apple-aspen-config"
                    response['Content-Disposition'] = 'attachment; filename=' + make_random_uuid() + '.mobileconfig'
                    return response
                res.msg = "mobileconifg release_id error"
            elif ftype == 'mobileprovision':
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    appsuper_obj = APPSuperSignUsedInfo.objects.filter(app_id=release_obj.app_id).last()
                    if not appsuper_obj:
                        appsuper_obj = APPSuperSignUsedInfo.objects.last()

                    if not appsuper_obj:
                        file_path = settings.DEFAULT_MOBILEPROVISION.get("supersign").get('path')
                        if os.path.isfile(file_path):
                            response = FileResponse(open(file_path, 'rb'))
                        else:
                            response = FileResponse()
                    else:
                        developer_obj = appsuper_obj.developerid
                        file_path = get_profile_full_path(developer_obj, release_obj.app_id)
                        if os.path.isfile(file_path):
                            response = FileResponse(open(file_path, 'rb'))
                        else:
                            file_path = settings.DEFAULT_MOBILEPROVISION.get("supersign").get('path')
                            if os.path.isfile(file_path):
                                response = FileResponse(open(file_path, 'rb'))
                            else:
                                response = FileResponse()
                    response['Content-Type'] = "application/x-apple-aspen-config"
                    response['Content-Disposition'] = 'attachment; filename=' + make_random_uuid() + '.mobileprovision'
                    return response
                res.msg = "mobileprovision release_id error"
            elif ftype == 'dmobileprovision':
                release_obj = AppReleaseInfo.objects.filter(release_id=filename.split('.')[0]).first()
                if release_obj:
                    file_path = settings.DEFAULT_MOBILEPROVISION.get("supersign").get('path')
                    if os.path.isfile(file_path):
                        response = FileResponse(open(file_path, 'rb'))
                    else:
                        response = FileResponse()
                    response['Content-Type'] = "application/x-apple-aspen-config"
                    response['Content-Disposition'] = 'attachment; filename=' + make_random_uuid() + '.mobileprovision'
                    return response
                res.msg = "dmobileprovision release_id error"

            else:
                file_path = os.path.join(settings.MEDIA_ROOT, filename)
                try:
                    if os.path.isfile(file_path):
                        response = FileResponse(open(file_path, 'rb'))
                    else:
                        response = FileResponse()
                except Exception as e:
                    logger.error("read %s failed  Exception:%s" % (file_path, e))
                    response = FileResponse()
                response['content_type'] = "application/octet-stream"
                response['Content-Disposition'] = 'attachment; filename=' + filename
                return response

        res.code = 1004
        res.msg = "token校验失败"
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
        if not app_obj:
            res.code = 1003
            res.msg = "该应用不存在"
            return Response(res.dict)

        if not check_user_has_all_download_times(app_obj):
            res.code = 1009
            res.msg = "可用下载额度不足，请联系开发者"
            return Response(res.dict)

        if not app_obj.isshow:
            res.code = 1004
            res.msg = "您没有权限访问该应用"
            return Response(res.dict)

        if udid:
            if not app_obj.issupersign:
                res.code = 1002
                res.msg = "参数有误"
                return Response(res.dict)
            del_cache_response_by_short(app_obj.app_id, udid=udid)

        app_serializer = AppsShortSerializer(app_obj, context={"key": "ShortDownloadView", "release_id": release_id,
                                                               "storage": Storage(app_obj.user_id)})
        res.data = app_serializer.data
        res.udid = udid
        res.domain_name = get_redirect_server_domain(request, app_obj.user_id, app_obj.domain_name)
        return Response(res.dict)

    # key的设置
    def calculate_cache_key(self, view_instance, view_method,
                            request, args, kwargs):
        release_id = request.query_params.get("release_id", '')
        udid = request.query_params.get("udid", None)
        time = request.query_params.get("time", None)
        if udid and time:
            udid = time
        if not udid:
            udid = ""
        logging.info(
            "get or make cache_response short:%s release_id:%s udid:%s" % (kwargs.get("short", ''), release_id, udid))
        return "_".join(
            [settings.CACHE_KEY_TEMPLATE.get("download_short_key"), kwargs.get("short", ''), release_id, udid])


class InstallView(APIView):
    throttle_classes = [VisitShortThrottle, InstallShortThrottle]
    '''
    安装操作，前端通过token 认证，认证成功之后，返回 下载连接，并且 让下载次数加一
    '''

    def get(self, request, app_id):
        res = BaseResponse()
        downtoken = request.query_params.get("token", None)
        short = request.query_params.get("short", None)
        release_id = request.query_params.get("release_id", None)
        isdownload = request.query_params.get("isdownload", None)
        password = request.query_params.get("password", None)
        udid = request.query_params.get("udid", None)

        if not downtoken or not short or not release_id:
            res.code = 1004
            res.msg = "参数丢失"
            return Response(res.dict)

        dtoken = DownloadToken()
        if dtoken.verify_token(downtoken, release_id):
            app_obj = get_app_instance_by_cache(app_id, password, 900, udid)
            if app_obj:
                if app_obj.get("type") == 0:
                    apptype = '.apk'
                    download_url, extra_url = get_download_url_by_cache(app_obj, release_id + apptype, 600)
                else:
                    apptype = '.ipa'
                    if isdownload:
                        download_url, extra_url = get_download_url_by_cache(app_obj, release_id + apptype, 600,
                                                                            udid=udid)
                    else:
                        download_url, extra_url = get_download_url_by_cache(app_obj, release_id + apptype, 600,
                                                                            isdownload,
                                                                            udid=udid)

                res.data = {"download_url": download_url, "extra_url": extra_url}
                if download_url != "" and "mobileconifg" not in download_url:
                    if request.META.get('HTTP_X_FORWARDED_FOR', None):
                        ip = request.META['HTTP_X_FORWARDED_FOR']
                    else:
                        ip = request.META['REMOTE_ADDR']
                    logger.info("remote ip %s short %s download_url %s app_obj %s" % (ip, short, download_url, app_obj))
                    set_app_download_by_cache(app_id)
                    amount = app_obj.get("d_count")
                    # 超级签需要多消耗2倍下载次数
                    if app_obj.get("issupersign"):
                        amount *= 2
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
