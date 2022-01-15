#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from admin.utils.serializer import AdminAppReportSerializer
from admin.utils.utils import AppsPageNumber, BaseModelSet
from api.models import AppReportInfo
from api.utils.auth import AdminTokenAuthentication

logger = logging.getLogger(__name__)


class ReportFilter(filters.FilterSet):
    class Meta:
        model = AppReportInfo
        fields = ["id", "app_name", "bundle_id", "remote_addr", "report_type", "email", "status", "app_id"]


class AdminReportView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = AppReportInfo.objects.all()
    serializer_class = AdminAppReportSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time']
    filterset_class = ReportFilter
