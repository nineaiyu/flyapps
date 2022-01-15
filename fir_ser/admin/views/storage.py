#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging
from copy import deepcopy

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.views import APIView

from admin.utils.serializer import AdminStorageSerializer
from admin.utils.utils import AppsPageNumber, BaseModelSet, ApiResponse
from api.base_views import storage_change
from api.models import UserInfo, AppStorage
from api.utils.auth import AdminTokenAuthentication
from common.base.baseutils import format_storage_selection

logger = logging.getLogger(__name__)


class StorageFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user_id__id")

    class Meta:
        model = AppStorage
        fields = ["id", "name", "storage_type", "access_key", "bucket_name", "domain_name"]


class StorageInfoView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = AppStorage.objects.all()
    serializer_class = AdminStorageSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time', 'updated_time']
    filterset_class = StorageFilter

    def list(self, request, *args, **kwargs):
        data = super().list(request, *args, **kwargs)._data
        if data['results']:
            data['storage_selection'] = format_storage_selection(deepcopy(data['results']),
                                                                 data['results'][0].get('storage_choices'))
        return ApiResponse(data=data)


class StorageChangeView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def put(self, request):

        data = request.data
        pk = data.get("id", None)
        if not pk:
            return ApiResponse(code=1003, msg="参数错误")
        obj = UserInfo.objects.filter(pk=pk).first()
        if obj:
            logger.info(f"user {obj} update storage data:{data}")
            use_storage_id = data.get("use_storage_id", None)
            force = data.get("force", None)
            if use_storage_id:
                if not storage_change(use_storage_id, obj, force):
                    ApiResponse(code=1006, msg="修改失败")
                return ApiResponse()

        return ApiResponse(code=1004, msg="数据校验失败")
