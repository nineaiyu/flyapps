#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView

from admin.utils.serializer import AdminUserInfoSerializer, AdminUserCertificationSerializer, AdminThirdWxSerializer
from admin.utils.utils import AppsPageNumber, BaseModelSet, ApiResponse
from api.models import UserInfo, UserCertificationInfo, ThirdWeChatUserInfo
from common.base.baseutils import get_dict_from_filter_fields
from common.core.auth import AdminTokenAuthentication
from common.core.sysconfig import Config
from common.utils.caches import auth_user_download_times_gift

logger = logging.getLogger(__name__)


class UserInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        filter_fields = ["id", "mobile", "username", "email", "first_name"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-date_joined")
        certification = request.query_params.get("certification", None)
        if certification:
            if certification == "-1":
                filter_data["certification__status__isnull"] = True
            else:
                filter_data["certification__status"] = certification
        page_obj = AppsPageNumber()
        obj_list = UserInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminUserInfoSerializer(page_serializer, many=True)
        data = serializer.data
        total = obj_list.count()
        return ApiResponse(data=data, total=total)

    def put(self, request):
        data = request.data
        id = data.get("id", None)
        if not id:
            return ApiResponse(code=1003, msg="参数错误")
        user_obj = UserInfo.objects.filter(id=id).first()
        if user_obj:
            data['pk'] = id
            users_serializer = AdminUserInfoSerializer(user_obj, data=data, partial=True)
            if users_serializer.is_valid():
                users_serializer.save()
                certification = data.get("certification", None)
                if certification and certification != -1:
                    user_cert_obj = UserCertificationInfo.objects.filter(user_id=user_obj).first()
                    if user_cert_obj:
                        status = user_cert_obj.status
                        UserCertificationInfo.objects.filter(user_id=user_obj).update(status=data["certification"])
                        if status != 1 and UserCertificationInfo.objects.filter(user_id=user_obj).first().status == 1:
                            auth_user_download_times_gift(user_obj, Config.AUTH_USER_GIVE_DOWNLOAD_TIMES)
                data = users_serializer.data
                return ApiResponse(data=data)
        return ApiResponse(code=1004, msg='数据校验失败')


class UserCertificationInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        filter_fields = ["id", "card", "name", "status"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = AppsPageNumber()
        obj_list = UserCertificationInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminUserCertificationSerializer(page_serializer, many=True)
        data = serializer.data
        total = obj_list.count()
        return ApiResponse(data=data, total=total)

    def put(self, request):
        data = request.data
        pk = data.get("id", None)
        if not pk:
            return ApiResponse(code=1003, msg='参数错误')
        obj = UserCertificationInfo.objects.filter(id=pk).first()
        if obj:
            data['pk'] = pk
            status = obj.status
            users_serializer = AdminUserCertificationSerializer(obj, data=data, partial=True)
            if users_serializer.is_valid():
                users_serializer.save()
                if status != 1 and users_serializer.data.get('status') == 1:
                    auth_user_download_times_gift(obj.user_id, Config.AUTH_USER_GIVE_DOWNLOAD_TIMES)
                data = users_serializer.data
                return ApiResponse(data=data)
        return ApiResponse(code=1004, msg='数据校验失败')


class ThirdWxAccountFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user_id__id")

    class Meta:
        model = ThirdWeChatUserInfo
        fields = ["id", "openid", "nickname", "subscribe", "user_id"]


class ThirdWxAccountView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = ThirdWeChatUserInfo.objects.all()
    serializer_class = AdminThirdWxSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time']
    filterset_class = ThirdWxAccountFilter
