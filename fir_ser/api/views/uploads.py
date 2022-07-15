#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6
import json
import logging
import os

from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Apps, AppReleaseInfo, UserInfo, AppScreenShot, CertificationInfo, UserAdDisplayInfo
from api.utils.apputils import get_random_short, save_app_infos
from api.utils.modelutils import get_app_download_uri, check_bundle_id_legal, get_user_storage_used, \
    get_user_storage_capacity
from api.utils.response import BaseResponse
from api.utils.signalutils import run_signal_resign_utils
from common.base.baseutils import make_app_uuid, make_from_user_uuid
from common.cache.state import MigrateStorageState
from common.core.auth import ExpiringTokenAuthentication
from common.core.sysconfig import Config, UserConfig
from common.utils.caches import upload_file_tmp_name, del_cache_response_by_short
from common.utils.storage import Storage
from common.utils.token import verify_token, make_token
from fir_ser import settings

logger = logging.getLogger(__name__)


class AppAnalyseView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def post(self, request):
        """
        应用上传前 分析数据，并返回应用上传信息
        :param request:
        :return:
        """
        res = BaseResponse()
        # 1.接收 bundelid ，返回随机应用名称和短连接
        bundle_id = request.data.get("bundleid", None)
        app_type = request.data.get("type", None)
        filesize = request.data.get("filesize", 0)
        if bundle_id:
            if check_bundle_id_legal(request.user.uid, bundle_id):
                res.code = 1004
                res.msg = "疑似违规，上传失败，如有疑问，请联系管理员"
                return Response(res.dict)

        if MigrateStorageState(request.user.uid).get_state():
            res.code = 1008
            res.msg = "数据迁移中，无法处理该操作"
            return Response(res.dict)

        if bundle_id and app_type:
            storage_used = get_user_storage_used(request.user)
            try:
                filesize = abs(int(filesize))
            except Exception as e:
                logger.warning(f"filesize check failed {request.data} Exception:{e}")
                filesize = 0
            if filesize + storage_used > get_user_storage_capacity(request.user):
                res.code = 1008
                res.msg = "存储空间不足，请升级存储空间或清理无用的历史版本数据来释放空间"
                return Response(res.dict)

            ap = 'apk'
            if app_type.lower() == 'iOS'.lower():
                ap = 'ipa'
            app_uuid = make_app_uuid(request.user, bundle_id + ap)
            uid = request.user.uid
            release_id = make_from_user_uuid(uid)
            png_id = make_from_user_uuid(uid)
            app_obj = Apps.objects.filter(app_id=app_uuid).first()
            binary_url = ''
            enable_sign = False
            if app_obj:
                is_new = False
                enable_sign = app_obj.issupersign
                short = app_obj.short
                app_release_obj = AppReleaseInfo.objects.filter(app_id=app_obj, is_master=True).first()
                short_domain_name = get_app_download_uri(request, request.user, app_obj)
                if app_release_obj:
                    binary_url = app_release_obj.binary_url
            else:
                is_new = True
                short_domain_name = get_app_download_uri(request, request.user)
                short = get_random_short()
            if app_type == 'iOS':
                upload_key = release_id + '.ipa' + settings.FILE_UPLOAD_TMP_KEY
            else:
                upload_key = release_id + '.apk' + settings.FILE_UPLOAD_TMP_KEY
            png_key = png_id + '.png' + settings.FILE_UPLOAD_TMP_KEY
            short_domain_name = f"{short_domain_name}/{'#/' if UserConfig(request.user).PREVIEW_ROUTE_HASH else ''}"
            storage = Storage(request.user)
            storage_type = storage.get_storage_type()
            upload_token = storage.get_upload_token(upload_key)
            png_token = storage.get_upload_token(png_key)
            upload_file_tmp_name("set", png_key, request.user.id)
            upload_file_tmp_name("set", upload_key, request.user.id)
            res.data = {"app_uuid": app_uuid, "short": short,
                        "short_domain_name": short_domain_name,
                        "upload_token": upload_token,
                        "upload_key": upload_key,
                        "png_token": png_token,
                        "png_key": png_key,
                        "storage": storage_type,
                        "is_new": is_new,
                        "binary_url": binary_url,
                        "enable_sign": enable_sign,
                        "access_token": make_token(app_uuid, time_limit=60 * 5, key='update_app_info', force_new=True)
                        }
            if storage_type not in [1, 2]:
                res.data['domain_name'] = Config.FILE_UPLOAD_DOMAIN
        else:
            res.code = 1003

        return Response(res.dict)

    def put(self, request):
        """
        该方法就是 应用上传完成之后的回调方法，更新或者创建新应用信息
        :param request:
        :return:
        """
        res = BaseResponse()

        if MigrateStorageState(request.user.uid).get_state():
            res.code = 1008
            res.msg = "数据迁移中，无法处理该操作"
            return Response(res.dict)

        data = request.data
        app_info = {
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

            bundle_id = data.get("bundleid", "")
            if not bundle_id:
                raise KeyError('bundle_id not exist')
            app_uuid = make_app_uuid(request.user, bundle_id + app_new_filename.split(".")[1])
            if not verify_token(data.get('access_token', ''), app_uuid, False):
                res.msg = '授权过期，请重试'
                res.code = 1004
                storage.delete_file(app_tmp_filename)
                storage.delete_file(png_tmp_filename)
                return Response(res.dict)

            logger.info(f"user {request.user} create or update app  {bundle_id}  data:{data}")
            if save_app_infos(app_tmp_filename, app_new_filename, request.user, app_info,
                              bundle_id, png_new_filename, data.get("short"), data.get('filesize'),
                              data.get('enable_sign')):
                # 需要将tmp 文件修改为正式文件
                storage.rename_file(app_tmp_filename, app_new_filename)
                storage.rename_file(png_tmp_filename, png_new_filename)

                app_obj = Apps.objects.filter(bundle_id=data.get("bundleid"), user_id=request.user, type=1).first()
                if app_obj:
                    run_signal_resign_utils(app_obj)
            else:
                storage.delete_file(app_tmp_filename)
                storage.delete_file(png_tmp_filename)
                res.code = 10003
                res.msg = '应用信息保存失败'
            # 删除redis key
            upload_file_tmp_name("del", app_tmp_filename, request.user.id)
            upload_file_tmp_name("del", png_tmp_filename, request.user.id)

        except Exception as e:
            logger.error(f"user {request.user} save app {data.get('bundleid')} info {app_info} failed Exception:{e}")
            res.code = 10003
            res.msg = '应用信息保存失败'

        return Response(res.dict)


class UploadView(APIView):
    """
    上传文件接口
    """
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        """
        该方法 主要是本地上传，通过该方法获取上传的 应用图片或者用户头像 的上传信息
        :param request:
        :return:
        """
        res = BaseResponse()
        storage = Storage(request.user)
        request_upload_key = request.query_params.get("upload_key", None)
        app_id = request.query_params.get("app_id", None)
        f_type = request.query_params.get("ftype", None)
        if f_type and app_id and request_upload_key:
            if f_type == 'app' or f_type == 'screen':
                app_obj = Apps.objects.filter(app_id=app_id, user_id=request.user).first()

            elif f_type and f_type in ['head', 'certification', 'advert']:
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
                    if f_type and f_type == 'certification':
                        storage = Storage(request.user, None, True)
                    upload_key = make_from_user_uuid(request.user.uid) + '.' + app_type + settings.FILE_UPLOAD_TMP_KEY
                    upload_token = storage.get_upload_token(upload_key)
                    storage_type = storage.get_storage_type()
                    res.data = {
                        "domain_name": Config.FILE_UPLOAD_DOMAIN,
                        "upload_token": upload_token,
                        "upload_key": upload_key,
                        "storage": storage_type,
                        "app_id": app_id,
                        "ftype": f_type
                    }
            else:
                res.code = 1006
                res.msg = '该应用不存在'
        else:
            res.code = 1006
        return Response(res.dict)

    def post(self, request):
        """
        该方法 主要是本地上传文件接口，负责上传 应用图片，应用文件或者用户头像
        :param request:
        :return:
        """
        res = BaseResponse()

        if MigrateStorageState(request.user.uid).get_state():
            res.code = 1008
            res.msg = "数据迁移中，无法处理该操作"
            return Response(res.dict)

        # 获取多个file
        files = request.FILES.getlist('file', None)
        cert_info = request.data.get('certinfo', None)

        try:
            cert_info = json.loads(cert_info)
            if not cert_info:
                res.msg = "数据信息 校验失败"
                res.code = 1006
                return Response(res.dict)
        except Exception as e:
            logger.error(f"{request.user} cert_info:{cert_info} get failed Exception:{e}")
            res.msg = "token 校验失败"
            res.code = 1006
            return Response(res.dict)

        if verify_token(token=cert_info.get("upload_token", None),
                        release_id=cert_info.get("upload_key", None)):

            app_id = cert_info.get("app_id", None)
            f_type = cert_info.get("ftype", None)
            if f_type and f_type in ['app', 'screen']:
                pass
                # app_obj = Apps.objects.filter(app_id=app_id, user_id=request.user).first()
                # if not app_obj:
                #     res.code = 1006
                #     res.msg = '该应用不存在'
                #     return Response(res.dict)
            elif f_type and f_type in ['head', 'certification', 'advert']:
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
                        logger.error(f"user:{request.user} upload file type error file:{file_obj.name}")
                        raise TypeError
                except Exception as e:
                    logger.error(f"user:{request.user} upload file type error Exception:{e}")
                    res.code = 1003
                    res.msg = "错误的类型"
                    return Response(res.dict)

                storage_used = get_user_storage_used(request.user)
                if file_obj.size + storage_used > get_user_storage_capacity(request.user):
                    res.code = 1008
                    res.msg = "存储空间不足，请升级存储空间或清理无用的历史版本数据来释放空间"
                    return Response(res.dict)

                random_file_name = make_from_user_uuid(request.user.uid)
                local_file = os.path.join(settings.MEDIA_ROOT, cert_info.get("upload_key", random_file_name))
                # 读取传入的文件
                logger.info(f"user:{request.user} save file:{local_file}")
                try:
                    destination = open(local_file, 'wb+')
                    for chunk in file_obj.chunks():
                        destination.write(chunk)
                    destination.close()

                except Exception as e:
                    logger.error(f"user:{request.user} save file:{local_file} error Exception:{e}")
                    res.code = 1003
                    res.msg = "数据写入失败"
                    try:
                        if os.path.isfile(local_file):
                            os.remove(local_file)
                    except Exception as e:
                        logger.error(f"user:{request.user} delete file:{local_file} error Exception:{e}")
                    return Response(res.dict)
        else:
            res.msg = "token 校验失败"
            res.code = 1006

        return Response(res.dict)

    def put(self, request):
        """
        该方法就是 应用图片或者用户头像上传完成之后的回调方法，为了更新上传完成的信息
        :param request:
        :return:
        """
        res = BaseResponse()

        if MigrateStorageState(request.user.uid).get_state():
            res.code = 1008
            res.msg = "数据迁移中，无法处理该操作"
            return Response(res.dict)

        cert_info = request.data.get('certinfo', None)
        if cert_info:
            app_id = cert_info.get("app_id", None)
            logger.info(f"user {request.user} update img {app_id} info")

            f_type = cert_info.get('ftype', None)
            upload_key = cert_info.get("upload_key", None)
            if f_type and upload_key:
                storage = Storage(request.user)
                new_upload_key = upload_key.strip(settings.FILE_UPLOAD_TMP_KEY)
            else:
                res.msg = '参数有误'
                res.code = 1008
                return Response(res.dict)
            if f_type and app_id and f_type == 'app':
                app_obj = Apps.objects.filter(app_id=app_id, user_id=request.user).first()
                if app_obj:
                    release_obj = AppReleaseInfo.objects.filter(app_id=app_obj, is_master=True).first()
                    if release_obj:
                        old_file_key = release_obj.icon_url
                        release_obj.icon_url = new_upload_key
                        release_obj.save(update_fields=["icon_url"])
                        storage.rename_file(upload_key, new_upload_key)
                        del_cache_response_by_short(app_id)
                        storage.delete_file(old_file_key)
                        return Response(res.dict)
            elif f_type and app_id and f_type == 'screen':
                app_obj = Apps.objects.filter(app_id=app_id, user_id=request.user).first()
                if app_obj:
                    if AppScreenShot.objects.filter(app_id=app_obj).count() >= 5:
                        storage.delete_file(upload_key)
                        res.msg = '最多支持五张截图'
                        res.code = 1009
                        return Response(res.dict)
                    AppScreenShot.objects.create(app_id=app_obj, screenshot_url=new_upload_key)
                    storage.rename_file(upload_key, new_upload_key)
                    del_cache_response_by_short(app_id)
                    return Response(res.dict)

            elif f_type and app_id and f_type in ['head', 'certification', 'advert']:
                if request.user.uid != app_id:
                    res.code = 1007
                    res.msg = '该用户不存在'
                    return Response(res.dict)
                if f_type == 'head':
                    old_file_key = request.user.head_img
                    UserInfo.objects.filter(pk=request.user.id).update(head_img=new_upload_key)
                    if old_file_key != "" or old_file_key != 'head_img.jpeg':
                        storage.delete_file(old_file_key)
                        storage.rename_file(upload_key, new_upload_key)
                elif f_type == 'certification':
                    ext = cert_info.get('ext', None)
                    if ext:
                        p_type = ext.get('ptype', None)
                        if p_type is not None and p_type in [1, 2, 3]:
                            storage = Storage(request.user, None, True)
                            certification_obj = CertificationInfo.objects.filter(user_id=request.user,
                                                                                 type=p_type).first()
                            if certification_obj:
                                old_certification_url = certification_obj.certification_url
                                certification_obj.certification_url = new_upload_key
                                certification_obj.save(update_fields=["certification_url"])
                                storage.delete_file(old_certification_url)
                            else:
                                CertificationInfo.objects.create(user_id=request.user, type=p_type,
                                                                 certification_url=new_upload_key)
                            storage.rename_file(upload_key, new_upload_key)

                        return Response(res.dict)
                elif f_type == 'advert':
                    ext = cert_info.get('ext', None)
                    if ext:
                        pk = ext.get('id')
                        if pk:
                            ad_info_obj = UserAdDisplayInfo.objects.filter(user_id=request.user, pk=pk).first()
                            if ad_info_obj:
                                old_file_key = ad_info_obj.ad_pic
                                storage.delete_file(old_file_key)
                                storage.rename_file(upload_key, new_upload_key)
                                ad_info_obj.ad_pic = new_upload_key
                                ad_info_obj.save(update_fields=['ad_pic'])
                return Response(res.dict)
            else:
                pass
        res.code = 1008
        return Response(res.dict)
