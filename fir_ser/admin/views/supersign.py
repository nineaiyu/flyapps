#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

from django.contrib import auth
from api.models import Token, APPSuperSignUsedInfo, AppIOSDeveloperInfo
from rest_framework.response import Response
from api.utils.auth import AdminTokenAuthentication
from api.utils.baseutils import get_dict_from_filter_fields
from api.utils.serializer import AdminDeveloperSerializer, AdminUserCertificationSerializer, \
    AdminSuperSignUsedSerializer
from django.core.cache import cache
from rest_framework.views import APIView
import binascii
import os, datetime
from api.utils.utils import get_captcha, valid_captcha, get_choices_dict
from api.utils.response import BaseResponse
from fir_ser.settings import CACHE_KEY_TEMPLATE, LOGIN
from api.utils.storage.caches import login_auth_failed
import logging
from api.utils.throttle import VisitRegister1Throttle, VisitRegister2Throttle
from rest_framework.pagination import PageNumberPagination

logger = logging.getLogger(__name__)


class AppsPageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class DeveloperInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "user_id", "issuer_id", "private_key_id", "certid", "description", "auth_type"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = AppsPageNumber()
        obj_list = AppIOSDeveloperInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminDeveloperSerializer(page_serializer, many=True)
        res.data = serializer.data
        res.total = obj_list.count()
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        obj = AppIOSDeveloperInfo.objects.filter(pk=pk).first()
        if obj:
            data['pk'] = pk
            serializer = AdminDeveloperSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res.data = serializer.data
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)


class DevicesInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "user_id", "issuer_id", "udid", "name", "bundle_id", "short"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = AppsPageNumber()
        if 'udid' in filter_data:
            filter_data["udid__udid"] = filter_data['udid']
            del filter_data['udid']

        if 'name' in filter_data:
            filter_data["app_id__name"] = filter_data['name']
            del filter_data['name']

        if 'bundle_id' in filter_data:
            filter_data["app_id__bundle_id"] = filter_data['bundle_id']
            del filter_data['bundle_id']

        if 'short' in filter_data:
            filter_data["app_id__short"] = filter_data['short']
            del filter_data['short']

        if 'issuer_id' in filter_data:
            filter_data["developerid__issuer_id"] = filter_data['issuer_id']
            del filter_data['issuer_id']

        obj_list = APPSuperSignUsedInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminSuperSignUsedSerializer(page_serializer, many=True)
        res.data = serializer.data
        res.total = obj_list.count()
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        obj = AppIOSDeveloperInfo.objects.filter(pk=pk).first()
        if obj:
            data['pk'] = pk
            serializer = AdminDeveloperSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res.data = serializer.data
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)
