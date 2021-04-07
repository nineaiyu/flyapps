#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6

from api.utils.app.apputils import get_random_short, SaveAppInfos
from api.utils.storage.storage import Storage
from api.utils.storage.caches import upload_file_tmp_name, del_cache_response_by_short
from api.models import Apps, AppReleaseInfo, UserInfo, AppScreenShot
from api.utils.app.randomstrings import make_app_uuid
from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from api.utils.app.randomstrings import make_from_user_uuid
from rest_framework.response import Response
from fir_ser import settings
from api.utils.TokenManager import DownloadToken
from api.utils.app.supersignutils import resign_by_app_obj, get_redirect_server_domain
import os, json, logging

logger = logging.getLogger(__file__)


class AppAnalyseView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def post(self, request):
        '''
        应用上传前 分析数据，并返回应用上传信息
        :param request:
        :return:
        '''
        res = BaseResponse()
        # 1.接收 bundelid ，返回随机应用名称和短连接
        bundleid = request.data.get("bundleid", None)
        app_type = request.data.get("type", None)

        if bundleid and app_type:
            ap = 'apk'
            if app_type.lower() == 'iOS'.lower():
                ap = 'ipa'
            app_uuid = make_app_uuid(request.user, bundleid + ap)
            release_id = make_from_user_uuid(request.user)
            png_id = make_from_user_uuid(request.user)
            app_obj = Apps.objects.filter(app_id=app_uuid).first()
            binary_url = ''
            if app_obj:
                is_new = False
                short = app_obj.short
                app_release_obj = AppReleaseInfo.objects.filter(app_id=app_obj, is_master=True).first()
                if app_release_obj:
                    binary_url = app_release_obj.binary_url
            else:
                is_new = True
                short = get_random_short()
            if app_type == 'iOS':
                upload_key = release_id + '.ipa' + settings.FILE_UPLOAD_TMP_KEY
            else:
                upload_key = release_id + '.apk' + settings.FILE_UPLOAD_TMP_KEY
            png_key = png_id + '.png' + settings.FILE_UPLOAD_TMP_KEY
            storage = Storage(request.user)
            storage_type = storage.get_storage_type()

            if storage_type == 1:
                upload_token = storage.get_upload_token(upload_key)
                png_token = storage.get_upload_token(png_key)
            elif storage_type == 2:
                png_token = upload_token = storage.get_upload_token(upload_key)
            else:
                upload_token = storage.get_upload_token(upload_key)
                png_token = storage.get_upload_token(png_key)

            upload_file_tmp_name("set", png_key, request.user.id)
            upload_file_tmp_name("set", upload_key, request.user.id)
            res.data = {"app_uuid": app_uuid, "short": short,
                        "domain_name": settings.SERVER_DOMAIN.get("FILE_UPLOAD_DOMAIN", None),
                        "upload_token": upload_token,
                        "upload_key": upload_key,
                        "png_token": png_token,
                        "png_key": png_key,
                        "storage": storage_type,
                        "is_new": is_new, "binary_url": binary_url}
        else:
            res.code = 1003

        return Response(res.dict)

    def put(self, request):
        '''
        该方法就是 应用上传完成之后的回调方法，更新或者创建新应用信息
        :param request:
        :return:
        '''
        res = BaseResponse()
        data = request.data
        appinfo = {
            "labelname": data.get("appname"),
            "version": data.get("buildversion"),
            "versioncode": data.get("version"),
            "release_type": data.get("release_type"),
            "miniOSversion": data.get("miniosversion"),
            "changelog": data.get("changelog", ''),
            "udid": data.get("udid", ''),
            "distribution_name": data.get("distribution_name", ''),
        }

        try:
            storage = Storage(request.user)
            app_tmp_filename = data.get("upload_key")
            app_new_filename = data.get("upload_key").strip(settings.FILE_UPLOAD_TMP_KEY)

            png_tmp_filename = data.get("png_key")
            png_new_filename = data.get("png_key").strip(settings.FILE_UPLOAD_TMP_KEY)
            logger.info("user %s create or update app %s  data:%s" % (request.user, data.get("bundleid"), data))
            if SaveAppInfos(app_new_filename, request.user, appinfo,
                            data.get("bundleid"), png_new_filename, data.get("short"), data.get('filesize')):
                # 需要将tmp 文件修改为正式文件
                storage.rename_file(app_tmp_filename, app_new_filename)
                storage.rename_file(png_tmp_filename, png_new_filename)

                app_info = Apps.objects.filter(bundle_id=data.get("bundleid")).first()
                if app_info:
                    if app_info.issupersign and app_info.user_id.supersign_active:
                        resign_by_app_obj(app_info, need_download_profile=False)

            else:
                storage.delete_file(app_tmp_filename)
                storage.delete_file(png_tmp_filename)
            # 删除redis key
            upload_file_tmp_name("del", app_tmp_filename, request.user.id)
            upload_file_tmp_name("del", png_tmp_filename, request.user.id)

        except Exception as e:
            logger.error("user %s %s save app info failed Exception:%s" % (request.user, data.get("bundleid"), e))
            res.code = 10003
            res.msg = 'save app info failed'

        return Response(res.dict)


class UploadView(APIView):
    '''
    上传文件接口
    '''
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        '''
        该方法 主要是本地上传，通过该方法获取上传的 应用图片或者用户头像 的上传信息
        :param request:
        :return:
        '''
        res = BaseResponse()
        storage = Storage(request.user)
        request_upload_key = request.query_params.get("upload_key", None)
        app_id = request.query_params.get("app_id", None)
        ftype = request.query_params.get("ftype", None)
        if ftype and app_id and request_upload_key:
            if ftype == 'app' or ftype == 'screen':
                app_obj = Apps.objects.filter(app_id=app_id, user_id=request.user).first()

            elif ftype and ftype in ['head', 'certification']:
                if request.user.uid != app_id:
                    res.code = 1007
                    res.msg = '该用户不存在'
                    return Response(res.dict)
                else:
                    app_obj = True
            else:
                app_obj = False

            if app_obj:
                app_type = request_upload_key.split(".")[-1]
                if app_type not in ["apk", "ipa", 'png', 'jpeg', 'jpg']:
                    res.code = 1006
                    res.msg = '类型不允许'
                else:
                    upload_key = make_from_user_uuid(request.user) + '.' + app_type + settings.FILE_UPLOAD_TMP_KEY
                    upload_token = storage.get_upload_token(upload_key)
                    storage_type = storage.get_storage_type()
                    res.data = {
                        "domain_name": settings.SERVER_DOMAIN.get("FILE_UPLOAD_DOMAIN", None),
                        "upload_token": upload_token,
                        "upload_key": upload_key,
                        "storage": storage_type,
                        "app_id": app_id,
                        "ftype": ftype
                    }
            else:
                res.code = 1006
                res.msg = '该应用不存在'
        else:
            res.code = 1006
        return Response(res.dict)

    def post(self, request):
        '''
        该方法 主要是本地上传文件接口，负责上传 应用图片，应用文件或者用户头像
        :param request:
        :return:
        '''
        res = BaseResponse()

        # 获取多个file
        files = request.FILES.getlist('file', None)
        certinfo = request.data.get('certinfo', None)

        try:
            certinfo = json.loads(certinfo)
            if not certinfo:
                res.msg = "数据信息 校验失败"
                res.code = 1006
                return Response(res.dict)
        except Exception as e:
            logger.error("%s certinfo:%s get failed Exception:%s" % (request.user, certinfo, e))
            res.msg = "token 校验失败"
            res.code = 1006
            return Response(res.dict)

        token_obj = DownloadToken()
        if token_obj.verify_token(token=certinfo.get("upload_token", None),
                                  release_id=certinfo.get("upload_key", None)):

            app_id = certinfo.get("app_id", None)
            ftype = certinfo.get("ftype", None)
            if ftype and ftype in ['app', 'screen']:
                pass
                # app_obj = Apps.objects.filter(app_id=app_id, user_id=request.user).first()
                # if not app_obj:
                #     res.code = 1006
                #     res.msg = '该应用不存在'
                #     return Response(res.dict)
            elif ftype and ftype in ['head', 'certification']:
                if request.user.uid != app_id:
                    res.code = 1007
                    res.msg = '该用户不存在'
                    return Response(res.dict)
            else:
                res.code = 1008
                res.msg = '该请求不存在'
                return Response(res.dict)
            if not files:
                res.msg = "文件不存在"
            for file_obj in files:
                try:

                    app_type = file_obj.name.split(".")[-1]
                    if app_type == "tmp":
                        app_type = file_obj.name.split(".")[-2]
                    if app_type not in ["apk", "ipa", 'png', 'jpeg', 'jpg']:
                        logger.error("user:%s  upload file type error file:%s " % (request.user, file_obj.name))
                        raise TypeError
                except Exception as e:
                    logger.error("user:%s  upload file type error Exception:%s " % (request.user, e))
                    res.code = 1003
                    res.msg = "错误的类型"
                    return Response(res.dict)

                random_file_name = make_from_user_uuid(request.user)
                local_file = os.path.join(settings.MEDIA_ROOT, certinfo.get("upload_key", random_file_name))
                # 读取传入的文件
                logger.info("user:%s  save file:%s" % (request.user, local_file))
                try:
                    destination = open(local_file, 'wb+')
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
                    destination.close()

                except Exception as e:
                    logger.error("user:%s  save file:%s error Exception:%s " % (request.user, local_file, e))
                    res.code = 1003
                    res.msg = "数据写入失败"
                    try:
                        if os.path.isfile(local_file):
                            os.remove(local_file)
                    except Exception as e:
                        logger.error("user:%s  delete file:%s error Exception:%s " % (request.user, local_file, e))
                    return Response(res.dict)
        else:
            res.msg = "token 校验失败"
            res.code = 1006

        return Response(res.dict)

    def put(self, request):
        '''
        该方法就是 应用图片或者用户头像上传完成之后的回调方法，为了更新上传完成的信息
        :param request:
        :return:
        '''
        res = BaseResponse()
        certinfo = request.data.get('certinfo', None)
        if certinfo:
            app_id = certinfo.get("app_id", None)
            logger.info("user %s update img %s info" % (request.user, app_id))

            ftype = certinfo.get('ftype', None)
            upload_key = certinfo.get("upload_key", None)
            if ftype and upload_key:
                storage = Storage(request.user)
                new_upload_key = upload_key.strip(settings.FILE_UPLOAD_TMP_KEY)
            else:
                res.msg = '参数有误'
                res.code = 1008
                return Response(res.dict)
            if ftype and app_id and ftype == 'app':
                app_obj = Apps.objects.filter(app_id=app_id, user_id=request.user).first()
                if app_obj:
                    release_obj = AppReleaseInfo.objects.filter(app_id=app_obj, is_master=True).first()
                    if release_obj:
                        old_file_key = release_obj.icon_url
                        release_obj.icon_url = new_upload_key
                        release_obj.save()
                        storage.rename_file(upload_key, new_upload_key)
                        del_cache_response_by_short(app_id)
                        storage.delete_file(old_file_key)
                        return Response(res.dict)
            elif ftype and app_id and ftype == 'screen':
                app_obj = Apps.objects.filter(app_id=app_id, user_id=request.user).first()
                if app_obj:
                    scount = AppScreenShot.objects.filter(app_id=app_obj).count()
                    if scount >= 5:
                        storage.delete_file(upload_key)
                        res.msg = '最多支持五张截图'
                        res.code = 1009
                        return Response(res.dict)
                    AppScreenShot.objects.create(app_id=app_obj, screenshot_url=new_upload_key)
                    storage.rename_file(upload_key, new_upload_key)
                    del_cache_response_by_short(app_id)
                    return Response(res.dict)

            elif ftype and app_id and ftype in ['head', 'certification']:
                if request.user.uid != app_id:
                    res.code = 1007
                    res.msg = '该用户不存在'
                    return Response(res.dict)
                if ftype == 'head':
                    old_file_key = request.user.head_img
                    UserInfo.objects.filter(pk=request.user.id).update(head_img=new_upload_key)
                    if old_file_key != "" or old_file_key != 'head_img.jpeg':
                        storage.delete_file(old_file_key)
                        storage.rename_file(upload_key, new_upload_key)
                elif ftype == 'certification':
                    ext = certinfo.get('ext', None)
                    if ext:
                        ptype = ext.get('type', None)
                        if ptype is not None:
                            pass
                    pass
                else:
                    pass

                return Response(res.dict)
            else:
                pass
        res.code = 1008
        return Response(res.dict)
