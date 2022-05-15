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
from admin.utils.utils import AppsPageNumber, BaseModelSet
from api.models import UserInfo, AppStorage
from api.tasks import migrate_storage_job
from common.base.baseutils import format_storage_selection
from common.core.auth import AdminTokenAuthentication
from common.core.response import ApiResponse

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
                c_task = migrate_storage_job.apply_async((use_storage_id, obj.pk, force))
                msg = c_task.get(propagate=False)
                logger.info(f"run migrate storage task {obj} msg:{msg}")
                if c_task.successful():
                    c_task.forget()
                else:
                    ApiResponse(code=1006, msg=msg)
                return ApiResponse()

        return ApiResponse(code=1004, msg="数据校验失败")
