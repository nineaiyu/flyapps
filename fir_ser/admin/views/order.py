#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from admin.utils.serializer import AdminOrdersSerializer
from admin.utils.utils import BaseModelSet, AppsPageNumber
from api.models import UserInfo, Order
from common.core.auth import AdminTokenAuthentication
from common.core.response import ApiResponse
from common.core.sysconfig import Config
from common.utils.caches import update_order_info, admin_change_user_download_times

logger = logging.getLogger(__name__)


class OrderFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user_id__id")

    class Meta:
        model = Order
        fields = ["id", "payment_type", "payment_name", "payment_number", "order_number", "status", "order_type"]


class OrderInfoView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = Order.objects.all()
    serializer_class = AdminOrdersSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time', 'pay_time', 'actual_amount']
    filterset_class = OrderFilter

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_status = instance.status
        data = super().update(request, *args, **kwargs).data
        new_status = request.data.get('status', -99)
        if old_status != new_status and new_status == 0:
            update_order_info(instance.user_id.pk, instance.order_number, instance.order_number, instance.payment_type)
        return ApiResponse(**data)

    def create(self, request, *args, **kwargs):
        data = request.data
        pk = data.get("id", None)
        amount = data.get("amount", 0)
        if not pk:
            return ApiResponse(code=1003, msg="参数错误")
        obj = UserInfo.objects.filter(pk=pk).first()
        if obj:
            if amount > 0:
                if admin_change_user_download_times(obj, amount * Config.APP_USE_BASE_DOWNLOAD_TIMES):
                    return ApiResponse()
                else:
                    return ApiResponse(code=1005, msg="订单创建失败")
        return ApiResponse(code=1004, msg="数据校验失败")
