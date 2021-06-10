#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

from django.contrib import auth

from api.base_views import storage_change
from api.models import Token, UserInfo, AppStorage
from rest_framework.response import Response
from api.utils.auth import AdminTokenAuthentication
from api.utils.baseutils import get_dict_from_filter_fields
from api.utils.serializer import AdminStorageSerializer, AdminUserCertificationSerializer
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
from api.utils.baseutils import format_storage_selection

logger = logging.getLogger(__name__)


class AppsPageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class StorageInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "user_id", "name", "storage_type", "access_key", "bucket_name"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = AppsPageNumber()
        obj_list = AppStorage.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminStorageSerializer(page_serializer, many=True)
        res.data = serializer.data
        res.total = obj_list.count()
        if res.total:
            res.storage_selection = format_storage_selection(serializer.data, serializer.data[0].get('storage_choices'))
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        obj = AppStorage.objects.filter(pk=pk).first()
        if obj and obj.user_id_id != obj.pk:
            data['pk'] = pk
            serializer = AdminStorageSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res.data = serializer.data
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)


class StorageChangeView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def put(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        obj = UserInfo.objects.filter(pk=pk).first()
        if obj:
            logger.info("user %s update storage data:%s" % (obj, data))
            use_storage_id = data.get("use_storage_id", None)
            force = data.get("force", None)
            if use_storage_id:
                if not storage_change(use_storage_id, obj, force):
                    res.code = 1006
                    res.msg = '修改失败'
                return Response(res.dict)

        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)
