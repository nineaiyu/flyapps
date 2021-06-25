#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4
from django.http.response import FileResponse
from rest_framework.views import APIView

from api.utils.app.iossignapi import ResignApp
from api.utils.baseutils import file_format_path
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication, SuperSignPermission
from rest_framework.response import Response
from api.models import AppIOSDeveloperInfo, APPSuperSignUsedInfo, AppUDID
from api.utils.serializer import DeveloperSerializer, SuperSignUsedSerializer, DeviceUDIDSerializer
from rest_framework.pagination import PageNumberPagination
from api.utils.app.supersignutils import IosUtils, get_auth_form_developer
from api.utils.utils import get_developer_devices, get_choices_dict
import logging

logger = logging.getLogger(__file__)


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

        appid = request.query_params.get("appid", None)
        developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user)
        res.use_num = get_developer_devices(developer_obj)
        if appid:
            developer_obj = developer_obj.filter(issuer_id=appid)

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
                logger.info("user %s iosdeveloper %s act %s" % (request.user, developer_obj, act))
                if act == "preactive":
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
                elif act == "checkauth":
                    status, result = IosUtils.active_developer(developer_obj)
                    if status:
                        return self.get(request)
                    else:
                        res.code = 1008
                        res.msg = result.get("return_info")
                        return Response(res.dict)
            else:
                logger.info("user %s iosdeveloper %s update input data %s" % (request.user, developer_obj, data))
                logger.info("user %s iosdeveloper %s update old data %s" % (
                    request.user, developer_obj, developer_obj.__dict__))
                try:
                    usable_number = int(data.get("usable_number", developer_obj.usable_number))
                    if 0 <= usable_number <= 100:
                        developer_obj.usable_number = usable_number
                except Exception as e:
                    logger.error("developer %s usable_number %s get failed Exception:%s" % (
                        developer_obj, data.get("usable_number", developer_obj.usable_number), e))
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
                    logger.info("user %s iosdeveloper %s update now data %s" % (
                        request.user, developer_obj, developer_obj.__dict__))
                except Exception as e:
                    logger.error("user %s iosdeveloper %s update error data %s Exception %s" % (
                        request.user, developer_obj, data, e))

        return self.get(request)

    def post(self, request):
        data = request.data
        datainfo = {}
        if data.get("auth_type") == 0:
            datainfo = {
                "usable_number": data.get("usable_number", ""),
                "description": data.get("description", ""),
                "issuer_id": data.get("issuer_id", ""),
                "private_key_id": data.get("private_key_id", ""),
                "p8key": data.get("p8key", ""),
                "auth_type": 0
            }
        try:
            logger.error("user %s  add new developer %s  data %s" % (
                request.user, data.get("issuer_id", ""), datainfo))
            AppIOSDeveloperInfo.objects.create(user_id=request.user, **datainfo)
        except Exception as e:
            logger.error("user %s create developer %s failed Exception:%s" % (
                request.user, datainfo, e))
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
            logger.error("user %s delete developer %s " % (
                request.user, developer_obj))
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
        bundleid = request.query_params.get("bundleid", None)
        developerid = request.query_params.get("appid", None)

        SuperSignUsed_obj = APPSuperSignUsedInfo.objects.filter(user_id=request.user, )

        if developerid:
            SuperSignUsed_obj = SuperSignUsed_obj.filter(developerid__issuer_id=developerid)
        if udid:
            SuperSignUsed_obj = SuperSignUsed_obj.filter(udid__udid=udid)
        if bundleid:
            SuperSignUsed_obj = SuperSignUsed_obj.filter(app_id__bundle_id=bundleid)

        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=SuperSignUsed_obj.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
        app_serializer = SuperSignUsedSerializer(app_page_serializer, many=True, )
        res.data = app_serializer.data
        res.count = SuperSignUsed_obj.count()
        return Response(res.dict)


class AppUDIDUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()

        udid = request.query_params.get("udid", None)
        bundleid = request.query_params.get("bundleid", None)
        AppUDID_obj = AppUDID.objects.filter(app_id__user_id_id=request.user)
        if udid:
            AppUDID_obj = AppUDID_obj.filter(udid=udid)
        if bundleid:
            AppUDID_obj = AppUDID_obj.filter(app_id__bundle_id=bundleid)

        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=AppUDID_obj.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
        app_serializer = DeviceUDIDSerializer(app_page_serializer, many=True, )
        res.data = app_serializer.data
        res.count = AppUDID_obj.count()
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        id = request.query_params.get("id", None)
        app_id = request.query_params.get("aid", None)
        app_udid_obj = AppUDID.objects.filter(app_id__user_id_id=request.user, pk=id)
        if app_udid_obj:
            logger.error("user %s delete devices %s" % (request.user, app_udid_obj))
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
                if not status:
                    res.code = 1002
                    res.msg = str(result['err_info'])
                    return Response(res.dict)
                status, result = IosUtils.auto_get_certid_by_p12(developer_obj, request.user)
                if not status:
                    res.code = 1003
                    res.msg = str('证书未在开发者账户找到，请检查推送证书是否属于该开发者')
        return Response(res.dict)
