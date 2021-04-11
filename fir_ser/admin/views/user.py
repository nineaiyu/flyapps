#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

from django.contrib import auth
from api.models import Token, UserInfo
from rest_framework.response import Response
from api.utils.auth import AdminTokenAuthentication
from api.utils.serializer import AdminUserInfoSerializer
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


class UserInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):

        mobile = request.query_params.get("mobile", None)
        username = request.query_params.get("username", None)
        email = request.query_params.get("email", None)
        first_name = request.query_params.get("first_name", None)
        certification = request.query_params.get("certification", None)
        id = request.query_params.get("id", None)
        sort = request.query_params.get("sort", "-date_joined")

        act_type = request.query_params.get("act", None)
        res = BaseResponse()
        filter_data = {}
        if mobile:
            filter_data["mobile"] = mobile
        if username:
            filter_data["username"] = username
        if email:
            filter_data["email"] = email
        if first_name:
            filter_data["email"] = first_name
        if id:
            filter_data["id"] = id
        if certification:
            if certification == "-1":
                filter_data["certification__status__isnull"] = True
            else:
                filter_data["certification__status"] = certification
        page_obj = AppsPageNumber()
        users_obj_list = UserInfo.objects.filter(**filter_data).order_by(sort)
        users_page_serializer = page_obj.paginate_queryset(queryset=users_obj_list, request=request,
                                                           view=self)
        users_serializer = AdminUserInfoSerializer(users_page_serializer, many=True)
        res.data = users_serializer.data
        res.total = users_obj_list.count()
        res.gender_choices = get_choices_dict(UserInfo.gender_choices)
        res.role_choices = get_choices_dict(UserInfo.role_choices)
        return Response(res.dict)
