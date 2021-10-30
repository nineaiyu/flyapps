#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import UserDomainInfo
from api.utils.auth import AdminTokenAuthentication
from api.utils.baseutils import get_dict_from_filter_fields
from api.utils.response import BaseResponse
from api.utils.serializer import AdminDomainNameSerializer
from api.utils.storage.caches import reset_app_wx_easy_type

logger = logging.getLogger(__name__)


class PageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class DomainNameInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "domain_name", "app_name", "domain_type", "user_id", "is_enable"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        app_name = filter_data.get('app_name', None)
        if app_name:
            filter_data["app_id__name__contains"] = filter_data['app_name']
            del filter_data['app_name']
        sort = request.query_params.get("sort", "-created_time")
        page_obj = PageNumber()
        obj_list = UserDomainInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminDomainNameSerializer(page_serializer, many=True)
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
        obj = UserDomainInfo.objects.filter(pk=pk).first()
        if obj:
            data['pk'] = pk
            serializer_obj = AdminDomainNameSerializer(obj, data=data, partial=True)
            if serializer_obj.is_valid():
                serializer_obj.save()
                res.data = serializer_obj.data
                reset_app_wx_easy_type(obj.user_id, obj.app_id)
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
            user_domain_obj = UserDomainInfo.objects.filter(pk=pk).first()
            reset_app_wx_easy_type(user_domain_obj.user_id, user_domain_obj.app_id)
            user_domain_obj.delete()
            return self.get(request)
        return Response(res.dict)
