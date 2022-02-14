#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from admin.utils.serializer import AdminDomainNameSerializer
from admin.utils.utils import BaseModelSet, AppsPageNumber, ApiResponse
from api.models import UserDomainInfo
from common.core.auth import AdminTokenAuthentication
from common.utils.caches import reset_app_wx_easy_type

logger = logging.getLogger(__name__)


class DomainNameFilter(filters.FilterSet):
    app_name = filters.CharFilter(field_name="app_id__name", lookup_expr='icontains')

    class Meta:
        model = UserDomainInfo
        fields = ["id", "domain_name", "domain_type", "user_id", "is_enable"]


class DomainNameInfoView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = UserDomainInfo.objects.all()
    serializer_class = AdminDomainNameSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time']
    filterset_class = DomainNameFilter

    def update(self, request, *args, **kwargs):
        data = super().update(request, *args, **kwargs).data
        instance = self.queryset.filter(pk=data.get('id')).first()
        if instance:
            reset_app_wx_easy_type(instance.user_id, instance.app_id)
        return ApiResponse(**data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        reset_app_wx_easy_type(instance.user_id, instance.app_id)
        self.perform_destroy(instance)
        return ApiResponse()
