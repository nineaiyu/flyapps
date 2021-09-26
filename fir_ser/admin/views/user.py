#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

from django.contrib import auth
from api.models import Token, UserInfo, UserCertificationInfo, ThirdWeChatUserInfo
from rest_framework.response import Response
from api.utils.auth import AdminTokenAuthentication
from api.utils.baseutils import get_dict_from_filter_fields
from api.utils.serializer import AdminUserInfoSerializer, AdminUserCertificationSerializer, AdminThirdWxSerializer
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


class PageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class UserInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "mobile", "username", "email", "first_name"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-date_joined")
        certification = request.query_params.get("certification", None)
        if certification:
            if certification == "-1":
                filter_data["certification__status__isnull"] = True
            else:
                filter_data["certification__status"] = certification
        page_obj = PageNumber()
        obj_list = UserInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminUserInfoSerializer(page_serializer, many=True)
        res.data = serializer.data
        res.total = obj_list.count()
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        id = data.get("id", None)
        if not id:
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        user_obj = UserInfo.objects.filter(id=id).first()
        if user_obj:
            data['pk'] = id
            users_serializer = AdminUserInfoSerializer(user_obj, data=data, partial=True)
            if users_serializer.is_valid():
                users_serializer.save()
                certification = data.get("certification", None)
                if certification and certification != -1:
                    UserCertificationInfo.objects.filter(user_id=user_obj).update(status=data["certification"])
                res.data = users_serializer.data
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)


class UserCertificationInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "card", "name", "status"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = PageNumber()
        obj_list = UserCertificationInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminUserCertificationSerializer(page_serializer, many=True)
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
        obj = UserCertificationInfo.objects.filter(id=pk).first()
        if obj:
            data['pk'] = pk
            users_serializer = AdminUserCertificationSerializer(obj, data=data, partial=True)
            if users_serializer.is_valid():
                users_serializer.save()
                res.data = users_serializer.data
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)


class ThirdWxAccountView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "openid", "nickname", "subscribe", "user_id"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = PageNumber()
        obj_list = ThirdWeChatUserInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminThirdWxSerializer(page_serializer, many=True)
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
        obj = ThirdWeChatUserInfo.objects.filter(pk=pk).first()
        if obj:
            data['pk'] = pk
            serializer_obj = AdminThirdWxSerializer(obj, data=data, partial=True)
            if serializer_obj.is_valid():
                serializer_obj.save()
                res.data = serializer_obj.data
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
        else:
            ThirdWeChatUserInfo.objects.filter(pk=pk).delete()
            return self.get(request)
        return Response(res.dict)
