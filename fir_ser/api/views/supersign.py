#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4
from django.http.response import FileResponse
from rest_framework.views import APIView

from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication, SuperSignPermission
from rest_framework.response import Response
from api.models import AppIOSDeveloperInfo, APPSuperSignUsedInfo, AppUDID
from api.utils.serializer import DeveloperSerializer, SuperSignUsedSerializer, DeviceUDIDSerializer
from rest_framework.pagination import PageNumberPagination
from api.utils.app.supersignutils import IosUtils
from api.utils.utils import get_developer_devices, get_choices_dict
import logging

logger = logging.getLogger(__name__)


class PageNumber(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class DeveloperView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):

        res = BaseResponse()

        app_id = request.query_params.get("appid", None)
        developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user)
        res.use_num = get_developer_devices(developer_obj)
        if app_id:
            developer_obj = developer_obj.filter(issuer_id=app_id)

        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=developer_obj.order_by("-updated_time"),
                                                         request=request,
                                                         view=self)
        developer_serializer = DeveloperSerializer(app_page_serializer, many=True, )

        res.data = developer_serializer.data
        res.count = developer_obj.count()

        res.apple_auth_list = get_choices_dict(AppIOSDeveloperInfo.auth_type_choices)
        return Response(res.dict)

    def put(self, request):
        data = request.data
        issuer_id = data.get("issuer_id", None)
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
        else:
            return self.get(request)

        if developer_obj:
            act = data.get("act", None)
            if act:
                res = BaseResponse()
                logger.info(f"user {request.user} ios developer {developer_obj} act {act}")
                if act == "checkauth":
                    status, result = IosUtils.active_developer(developer_obj)
                    if status:
                        if not developer_obj.certid:
                            IosUtils.get_device_from_developer(developer_obj, request.user)
                        return self.get(request)
                    else:
                        res.code = 1008
                        res.msg = result.get("return_info", "未知错误")
                        return Response(res.dict)

                elif act == "ioscert":
                    if not developer_obj.certid:
                        status, result = IosUtils.create_developer_cert(developer_obj, request.user)
                        if status:
                            IosUtils.get_device_from_developer(developer_obj, request.user)
                        else:
                            res.code = 1008
                            res.msg = result.get("err_info")
                            return Response(res.dict)
                elif act == "renewcert":
                    if developer_obj.certid:
                        # clean developer somethings. remove profile and  revoke cert
                        IosUtils.clean_developer(developer_obj, request.user)
                        status, result = IosUtils.revoke_developer_cert(developer_obj, request.user)
                        if status:
                            pass
                            # status, result = IosUtils.create_developer_cert(developer_obj, request.user)
                            # if status:
                            #     IosUtils.get_device_from_developer(developer_obj, request.user)
                            # else:
                            #     res.code = 1008
                            #     res.msg = result.get("err_info")
                            #     return Response(res.dict)
                        else:
                            res.code = 1008
                            res.msg = result.get("err_info", '')
                            return Response(res.dict)
                elif act == "syncdevice":
                    status, result = IosUtils.get_device_from_developer(developer_obj, request.user)
                    if not status:
                        res.code = 1008
                        res.msg = result.get("err_info")
                        return Response(res.dict)
            else:
                logger.info(f"user {request.user} ios developer {developer_obj} update input data {data}")
                logger.info(
                    f"user {request.user} ios developer {developer_obj} update old data {developer_obj.__dict__}")
                try:
                    usable_number = int(data.get("usable_number", developer_obj.usable_number))
                    if 0 <= usable_number <= 100:
                        developer_obj.usable_number = usable_number
                except Exception as e:
                    logger.error(
                        f"developer {developer_obj} usable_number {data.get('usable_number', developer_obj.usable_number)} get failed Exception:{e}")
                developer_obj.description = data.get("description", developer_obj.description)
                private_key_id = data.get("private_key_id", developer_obj.private_key_id)
                p8key = data.get("p8key", developer_obj.p8key)
                if private_key_id != "" and private_key_id != developer_obj.private_key_id:
                    developer_obj.private_key_id = private_key_id
                    developer_obj.is_actived = False
                if p8key != "" and p8key != developer_obj.p8key:
                    developer_obj.p8key = p8key
                    developer_obj.is_actived = False
                try:
                    developer_obj.save()
                    logger.info(
                        f"user {request.user} ios developer {developer_obj} update now data {developer_obj.__dict__}")
                except Exception as e:
                    logger.error(
                        f"user {request.user} ios developer {developer_obj} update error data {data} Exception {e}")

        return self.get(request)

    def post(self, request):
        data = request.data
        data_info = {}
        if data.get("auth_type") == 0:
            data_info = {
                "usable_number": data.get("usable_number", ""),
                "description": data.get("description", ""),
                "issuer_id": data.get("issuer_id", ""),
                "private_key_id": data.get("private_key_id", ""),
                "p8key": data.get("p8key", ""),
                "auth_type": 0
            }
        try:
            logger.error(f"user {request.user} add new developer {data.get('issuer_id', '')} data {data_info}")
            developer_obj = AppIOSDeveloperInfo.objects.create(user_id=request.user, **data_info)
            IosUtils.create_developer_space(developer_obj, request.user)
        except Exception as e:
            logger.error(f"user {request.user} create developer {data_info} failed Exception:{e}")
            res = BaseResponse()
            res.code = 1005
            res.msg = "添加失败"
            return Response(res.dict)

        return self.get(request)

    def delete(self, request):
        issuer_id = request.query_params.get("issuer_id", None)
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
        else:
            return self.get(request)

        if developer_obj:
            logger.error(f"user {request.user} delete developer {developer_obj}")
            IosUtils.clean_developer(developer_obj, request.user)
            IosUtils.revoke_developer_cert(developer_obj, request.user)
            developer_obj.delete()

        return self.get(request)


class SuperSignUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()

        udid = request.query_params.get("udid", None)
        bundle_id = request.query_params.get("bundleid", None)
        developer_id = request.query_params.get("appid", None)

        super_sign_used_objs = APPSuperSignUsedInfo.objects.filter(user_id=request.user, )

        if developer_id:
            super_sign_used_objs = super_sign_used_objs.filter(developerid__issuer_id=developer_id)
        if udid:
            super_sign_used_objs = super_sign_used_objs.filter(udid__udid=udid)
        if bundle_id:
            super_sign_used_objs = super_sign_used_objs.filter(app_id__bundle_id=bundle_id)

        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=super_sign_used_objs.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
        app_serializer = SuperSignUsedSerializer(app_page_serializer, many=True, )
        res.data = app_serializer.data
        res.count = super_sign_used_objs.count()
        return Response(res.dict)


class AppUDIDUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()

        udid = request.query_params.get("udid", None)
        bundle_id = request.query_params.get("bundleid", None)
        app_udid_objs = AppUDID.objects.filter(app_id__user_id_id=request.user)
        if udid:
            app_udid_objs = app_udid_objs.filter(udid=udid)
        if bundle_id:
            app_udid_objs = app_udid_objs.filter(app_id__bundle_id=bundle_id)

        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=app_udid_objs.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
        app_serializer = DeviceUDIDSerializer(app_page_serializer, many=True, )
        res.data = app_serializer.data
        res.count = app_udid_objs.count()
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        pk = request.query_params.get("id", None)
        app_id = request.query_params.get("aid", None)
        app_udid_obj = AppUDID.objects.filter(app_id__user_id_id=request.user, pk=pk)
        if app_udid_obj:
            logger.error(f"user {request.user} delete devices {app_udid_obj}")
            IosUtils.disable_udid(app_udid_obj.first(), app_id)
            app_udid_obj.delete()
        return Response(res.dict)


class SuperSignCertView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        issuer_id = request.query_params.get('issuer_id', None)
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
            # resign_app_obj = IosUtils.get_resign_obj(request.user, developer_obj)
            # resign_app_obj.make_p12_from_cert(developer_obj.certid)
            if developer_obj:
                zip_file_path = IosUtils.zip_cert(request.user, developer_obj)
                response = FileResponse(open(zip_file_path, 'rb'))
                response['Content-Type'] = "application/octet-stream"
                response["Access-Control-Expose-Headers"] = "Content-Disposition"
                response['Content-Disposition'] = 'attachment; filename=' + developer_obj.certid + '.zip'
                return response
        res = BaseResponse()
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        issuer_id = request.data.get('issuer_id', None)
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
            if developer_obj:
                resign_app_obj = IosUtils.get_resign_obj(request.user, developer_obj)
                status, result = resign_app_obj.make_cert_from_p12(request.data.get('cert_pwd', ''),
                                                                   request.data.get('cert_content', None))
                if status:
                    status, result = IosUtils.auto_get_cert_id_by_p12(developer_obj, request.user)
                    if status:
                        resign_app_obj.write_cert()
                    else:
                        res.code = 1003
                        res.msg = '证书未在开发者账户找到，请检查推送证书是否属于该开发者'
                else:
                    res.code = 1002
                    res.msg = str(result['err_info'])
                    return Response(res.dict)
        return Response(res.dict)
