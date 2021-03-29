#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication, SuperSignPermission
from rest_framework.response import Response
from api.models import AppIOSDeveloperInfo, APPSuperSignUsedInfo, AppUDID
from api.utils.serializer import DeveloperSerializer, SuperSignUsedSerializer, DeviceUDIDSerializer
from rest_framework.pagination import PageNumberPagination
from api.utils.app.supersignutils import IosUtils
from api.utils.utils import get_developer_devices
from api.utils.storage.caches import developer_auth_code
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
            developer_obj1 = developer_obj.filter(email=appid)
            developer_obj2 = developer_obj.filter(issuer_id=appid)
            developer_obj = developer_obj1 | developer_obj2

        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=developer_obj.order_by("-updated_time"),
                                                         request=request,
                                                         view=self)
        developer_serializer = DeveloperSerializer(app_page_serializer, many=True, )

        res.data = developer_serializer.data
        res.count = developer_obj.count()

        res.apple_auth_list = []
        apple_auth_org_list = list(AppIOSDeveloperInfo.auth_type_choices)
        for auth_t in apple_auth_org_list:
            res.apple_auth_list.append({'id': auth_t[0], 'name': auth_t[1]})

        return Response(res.dict)

    def put(self, request):
        data = request.data
        email = data.get("email", None)
        issuer_id = data.get("issuer_id", None)
        if email:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, email=email).first()
        elif issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
        else:
            return self.get(request)

        if developer_obj:
            act = data.get("act", None)
            if act:
                res = BaseResponse()
                logger.info("user %s iosdeveloper %s act %s" % (request.user, developer_obj, act))
                if act == "preactive":
                    if developer_obj.email:
                        developer_auth_code("del", request.user, developer_obj.email)
                    elif developer_obj.issuer_id:
                        developer_auth_code("del", request.user, developer_obj.issuer_id)

                    status, result = IosUtils.active_developer(developer_obj, request.user)
                    if status:
                        if not developer_obj.certid:
                            if developer_obj.email:
                                status, result = IosUtils.create_developer_cert(developer_obj, request.user)
                            elif developer_obj.issuer_id:
                                return Response(res.dict)
                            if status:
                                IosUtils.get_device_from_developer(developer_obj, request.user)
                            else:
                                res.code = 1008
                                res.msg = result.get("err_info")
                                return Response(res.dict)
                        return self.get(request)
                    else:
                        res.code = 1008
                        res.msg = result.get("return_info", "未知错误")
                        return Response(res.dict)
                elif act == "nowactive":
                    code = data.get("code", None)
                    if code:
                        developer_auth_code("set", request.user, developer_obj.email, code)

                elif act == "ioscert":
                    if not developer_obj.certid:
                        status, result = IosUtils.create_developer_cert(developer_obj, request.user)
                        if status:
                            IosUtils.get_device_from_developer(developer_obj, request.user)
                        else:
                            res.code = 1008
                            res.msg = result.get("err_info")
                            return Response(res.dict)
                elif act == "syncdevice":
                    status, result = IosUtils.get_device_from_developer(developer_obj, request.user)
                    if status:
                        IosUtils.get_device_from_developer(developer_obj, request.user)
                    else:
                        res.code = 1008
                        res.msg = result.get("err_info")
                        return Response(res.dict)
                elif act == "checkauth":
                    if developer_obj.email:
                        developer_auth_code("del", request.user, developer_obj.email)
                    elif developer_obj.issuer_id:
                        developer_auth_code("del", request.user, developer_obj.issuer_id)
                    status, result = IosUtils.active_developer(developer_obj, request.user)
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
                password = data.get("password", developer_obj.password)
                if password != "" and password != developer_obj.password:
                    developer_obj.password = password
                    developer_obj.is_actived = False
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
        if data.get("auth_type") == 0:
            datainfo = {
                "usable_number": data.get("usable_number", ""),
                "description": data.get("description", ""),
                "issuer_id": data.get("issuer_id", ""),
                "private_key_id": data.get("private_key_id", ""),
                "p8key": data.get("p8key", ""),
                "auth_type": 0
            }
        else:
            datainfo = {
                "usable_number": data.get("usable_number", ""),
                "description": data.get("description", ""),
                "password": data.get("password", ""),
                "email": data.get("email", ""),
                "auth_type": 1
            }
        try:
            logger.error("user %s  add new developer %s  data %s" % (
                request.user, data.get("email", ""), datainfo))
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
        email = request.query_params.get("email", None)
        issuer_id = request.query_params.get("issuer_id", None)
        if email:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, email=email).first()
        elif issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
        else:
            return self.get(request)

        if developer_obj:
            logger.error("user %s delete developer %s " % (
                request.user, developer_obj))
            IosUtils.clean_developer(developer_obj, request.user)
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
            SuperSignUsed_obj = SuperSignUsed_obj.filter(developerid__email=developerid)
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
