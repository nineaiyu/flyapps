#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import UserInfo, UserCertificationInfo, ThirdWeChatUserInfo
from api.utils.auth import AdminTokenAuthentication
from api.utils.response import BaseResponse
from api.utils.serializer import AdminUserInfoSerializer, AdminUserCertificationSerializer, AdminThirdWxSerializer
from api.utils.storage.caches import auth_user_download_times_gift
from common.base.baseutils import get_dict_from_filter_fields
from fir_ser.settings import AUTH_USER_GIVE_DOWNLOAD_TIMES

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
                    user_cert_obj = UserCertificationInfo.objects.filter(user_id=user_obj).first()
                    if user_cert_obj:
                        status = user_cert_obj.status
                        UserCertificationInfo.objects.filter(user_id=user_obj).update(status=data["certification"])
                        if status != 1 and UserCertificationInfo.objects.filter(user_id=user_obj).first().status == 1:
                            auth_user_download_times_gift(user_obj, AUTH_USER_GIVE_DOWNLOAD_TIMES)
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
            status = obj.status
            users_serializer = AdminUserCertificationSerializer(obj, data=data, partial=True)
            if users_serializer.is_valid():
                users_serializer.save()
                if status != 1 and users_serializer.data.get('status') == 1:
                    auth_user_download_times_gift(obj.user_id, AUTH_USER_GIVE_DOWNLOAD_TIMES)
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
