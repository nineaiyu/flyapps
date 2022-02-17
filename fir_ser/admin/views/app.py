#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from admin.utils.serializer import AdminAppsSerializer, AdminAppReleaseSerializer
from admin.utils.utils import AppsPageNumber, BaseModelSet
from api.base_views import app_delete
from api.models import AppReleaseInfo, Apps
from common.core.auth import AdminTokenAuthentication
from common.core.response import ApiResponse
from common.utils.caches import del_cache_response_by_short
from common.utils.download import get_download_url_by_cache
from common.utils.token import verify_token

logger = logging.getLogger(__name__)


class AppsFilter(filters.FilterSet):
    min_count_hits = filters.NumberFilter(field_name="count_hits", lookup_expr='gte')
    max_count_hits = filters.NumberFilter(field_name="count_hits", lookup_expr='lte')
    bundle_id_like = filters.CharFilter(field_name="bundle_id", lookup_expr='icontains')

    class Meta:
        model = Apps
        fields = ["id", "type", "name", "short", "bundle_id", "user_id", "status"]


class AppInfoView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = Apps.objects.all()
    serializer_class = AdminAppsSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['updated_time', 'count_hits', 'created_time']
    filterset_class = AppsFilter

    def update(self, request, *args, **kwargs):
        data = super().update(request, *args, **kwargs).data
        del_cache_response_by_short(data.get('app_id'))
        return ApiResponse(**data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        app_delete(instance)
        return ApiResponse()


class AppReleaseInfoView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]

    queryset = AppReleaseInfo.objects.all()
    serializer_class = AdminAppReleaseSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time']
    filterset_fields = ("id", "release_id", "app_id")

    def update(self, request, *args, **kwargs):
        data = super().update(request, *args, **kwargs).data
        del_cache_response_by_short(data.get('app_aid'))
        return ApiResponse(**data)

    def create(self, request, *args, **kwargs):
        data = request.data
        downtoken = data.get("token", None)
        app_id = data.get("app_id", None)
        release_id = data.get("release_id", None)

        if not downtoken or not app_id or not release_id:
            return ApiResponse(code=1004, msg='参数丢失')

        if verify_token(downtoken, release_id):
            app_obj = Apps.objects.filter(pk=app_id).values("pk", 'user_id', 'type').first()
            release_obj = AppReleaseInfo.objects.filter(app_id=app_id, release_id=release_id).count()
            if app_obj and release_obj:
                if app_obj.get("type") == 0:
                    app_type = '.apk'
                else:
                    app_type = '.ipa'
                download_url, extra_url = get_download_url_by_cache(app_obj, release_id + app_type, 600)
                return ApiResponse(data={"download_url": download_url, "extra_url": extra_url})
        else:
            return ApiResponse(code=1004, msg='token校验失败')
        return ApiResponse(code=1006, msg='该应用不存在')
