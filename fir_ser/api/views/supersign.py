#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from api.models import AppIOSDeveloperInfo,APPSuperSignUsedInfo,AppUDID
from api.utils.serializer import  DeveloperSerializer, UserInfoSerializer,SuperSignUsedSerializer,DeviceUDIDSerializer
from rest_framework.pagination import PageNumberPagination
from api.utils.app.supersignutils import IosUtils



class AppsPageNumber(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class DeveloperView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):

        res = BaseResponse()

        developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user)

        page_obj = AppsPageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=developer_obj.order_by("-updated_time"), request=request,
                                                         view=self)

        app_serializer = DeveloperSerializer(app_page_serializer, many=True,)
        userserializer = UserInfoSerializer(request.user)
        res.userinfo = {}
        res.has_next = {}
        res.userinfo = userserializer.data
        res.data = app_serializer.data
        res.has_next = page_obj.page.has_next()
        return Response(res.dict)

class SuperSignUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        developer_obj = APPSuperSignUsedInfo.objects.filter(user_id=request.user)
        page_obj = AppsPageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=developer_obj.order_by("-created_time"), request=request,
                                                         view=self)
        app_serializer = SuperSignUsedSerializer(app_page_serializer, many=True, )
        res.data = app_serializer.data
        res.has_next = page_obj.page.has_next()
        return Response(res.dict)

class AppUDIDUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()

        udid = request.query_params.get("udid", None)
        bundleid = request.query_params.get("bundleid", None)
        if udid and bundleid:
            developer_obj = AppUDID.objects.filter(app_id__user_id_id=request.user,app_id__bundle_id=bundleid,udid=udid)
        elif udid:
                developer_obj = AppUDID.objects.filter(app_id__user_id_id=request.user,udid=udid)
        elif bundleid:
                developer_obj = AppUDID.objects.filter(app_id__user_id_id=request.user,app_id__bundle_id=bundleid)
        else:
            developer_obj = AppUDID.objects.filter(app_id__user_id_id=request.user)

        page_obj = AppsPageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=developer_obj.order_by("-created_time"), request=request,
                                                         view=self)
        app_serializer = DeviceUDIDSerializer(app_page_serializer, many=True,)
        res.data = app_serializer.data
        res.has_next = page_obj.page.has_next()
        return Response(res.dict)

    def delete(self,request):
        res = BaseResponse()
        id = request.query_params.get("id", None)
        app_id = request.query_params.get("aid", None)
        app_udid_obj=AppUDID.objects.filter(app_id__user_id_id=request.user,pk=id)
        IosUtils.disable_udid(app_udid_obj.first(),app_id)
        app_udid_obj.delete()
        return self.get(request)
