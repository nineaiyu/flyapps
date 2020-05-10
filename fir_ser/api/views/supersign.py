#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from api.models import AppIOSDeveloperInfo, APPSuperSignUsedInfo, AppUDID
from api.utils.serializer import DeveloperSerializer, SuperSignUsedSerializer, DeviceUDIDSerializer
from rest_framework.pagination import PageNumberPagination
from api.utils.app.supersignutils import IosUtils
from api.utils.utils import get_developer_devices
from api.utils.storage.caches import developer_auth_code


class AppsPageNumber(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class DeveloperView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):

        res = BaseResponse()

        appid = request.query_params.get("appid", None)
        developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user)
        res.use_num = get_developer_devices(developer_obj)
        if appid:
            developer_obj = developer_obj.filter(email=appid)

        page_obj = AppsPageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=developer_obj.order_by("-updated_time"),
                                                         request=request,
                                                         view=self)
        Developer_serializer = DeveloperSerializer(app_page_serializer, many=True, )

        res.data = Developer_serializer.data
        res.count = developer_obj.count()
        return Response(res.dict)

    def put(self, request):
        data = request.data
        email = data.get("email", None)
        if email:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, email=email).first()
            if developer_obj:
                act = data.get("act", None)
                if act:
                    res = BaseResponse()
                    if act == "preactive":
                        developer_auth_code("del", request.user, developer_obj.email)
                        status, result = IosUtils.active_developer(developer_obj, request.user)
                        if status:
                            if not developer_obj.certid:
                                status, result = IosUtils.create_developer_cert(developer_obj, request.user)
                                if status:
                                    IosUtils.get_device_from_developer(developer_obj, request.user)
                                else:
                                    res.code = 1008
                                    res.msg = result.get("err_info")
                                    return Response(res.dict)
                            return self.get(request)
                        else:
                            res.code = 1008
                            res.msg = result.get("return_info")
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
                        developer_auth_code("del", request.user, developer_obj.email)
                        status, result = IosUtils.active_developer(developer_obj, request.user)
                        if status:
                            return self.get(request)
                        else:
                            res.code = 1008
                            res.msg = result.get("return_info")
                            return Response(res.dict)
                else:
                    try:
                        usable_number = int(data.get("usable_number", developer_obj.usable_number))
                        if usable_number >= 0 and usable_number <= 100:
                            developer_obj.usable_number = usable_number
                    except Exception as e:
                        print(e)
                    developer_obj.description = data.get("description", developer_obj.description)
                    password = data.get("password", developer_obj.password)
                    if password != "" and password != developer_obj.password:
                        developer_obj.password = password
                        developer_obj.is_actived = False
                    developer_obj.save()

        return self.get(request)

    def post(self, request):
        data = request.data
        datainfo = {
            "usable_number": data.get("usable_number", ""),
            "description": data.get("description", ""),
            "password": data.get("password", ""),
            "email": data.get("email", ""),
        }
        try:
            AppIOSDeveloperInfo.objects.create(user_id=request.user, **datainfo)
        except Exception as e:
            print(e)
            res = BaseResponse()
            res.code = 1005
            res.msg = "添加失败"
            return Response(res.dict)

        return self.get(request)

    def delete(self, request):
        email = request.query_params.get("email", None)
        if email:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, email=email).first()
            if developer_obj:
                IosUtils.clean_developer(developer_obj, request.user)
                developer_obj.delete()

        return self.get(request)


class SuperSignUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

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

        page_obj = AppsPageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=SuperSignUsed_obj.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
        app_serializer = SuperSignUsedSerializer(app_page_serializer, many=True, )
        res.data = app_serializer.data
        res.count = SuperSignUsed_obj.count()
        return Response(res.dict)


class AppUDIDUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()

        udid = request.query_params.get("udid", None)
        bundleid = request.query_params.get("bundleid", None)
        AppUDID_obj = AppUDID.objects.filter(app_id__user_id_id=request.user)
        if udid:
            AppUDID_obj = AppUDID_obj.filter(udid=udid)
        if bundleid:
            AppUDID_obj = AppUDID_obj.filter(app_id__bundle_id=bundleid)

        page_obj = AppsPageNumber()
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
        IosUtils.disable_udid(app_udid_obj.first(), app_id)
        app_udid_obj.delete()
        return Response(res.dict)
