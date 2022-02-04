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

from admin.utils.serializer import AdminDeveloperSerializer, AdminSuperSignUsedSerializer, AdminBillInfoSerializer
from admin.utils.utils import AppsPageNumber, BaseModelSet, ApiResponse
from api.models import APPSuperSignUsedInfo, AppIOSDeveloperInfo, IosDeveloperPublicPoolBill, IosDeveloperBill
from api.utils.auth import AdminTokenAuthentication
from api.utils.modelutils import get_user_public_used_sign_num, get_user_public_sign_num, get_user_obj_from_epu
from api.utils.utils import get_developer_devices
from common.base.baseutils import get_real_ip_address

logger = logging.getLogger(__name__)


class DeveloperFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user_id__id")

    class Meta:
        model = AppIOSDeveloperInfo
        fields = ["id", "issuer_id", "private_key_id", "certid", "description", "auth_type"]


class DeveloperInfoView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = AppIOSDeveloperInfo.objects.all()
    serializer_class = AdminDeveloperSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time', 'cert_expire_time', 'updated_time']
    filterset_class = DeveloperFilter


class DevicesFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user_id__id")
    issuer_id = filters.CharFilter(field_name="developerid__issuer_id")
    udid = filters.CharFilter(field_name="udid__udid__udid")
    name = filters.CharFilter(field_name="app_id__name")
    bundle_id = filters.CharFilter(field_name="app_id__bundle_id")
    short = filters.CharFilter(field_name="app_id__short")

    class Meta:
        model = APPSuperSignUsedInfo
        fields = ["id", "user_id", "issuer_id", "udid", "name", "bundle_id", "short"]


class DevicesInfoView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = APPSuperSignUsedInfo.objects.all()
    serializer_class = AdminSuperSignUsedSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time', 'updated_time']
    filterset_class = DevicesFilter


class SuperSignBillFilter(filters.FilterSet):
    user_id = filters.NumberFilter(field_name="user_id__id")

    class Meta:
        model = IosDeveloperPublicPoolBill
        fields = ["id", "user_id", "udid", "app_id"]


class SuperSignBillView(BaseModelSet):
    authentication_classes = [AdminTokenAuthentication, ]
    queryset = IosDeveloperPublicPoolBill.objects.all()
    serializer_class = AdminBillInfoSerializer
    pagination_class = AppsPageNumber

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ['created_time']
    filterset_class = SuperSignBillFilter

    def create(self, request, *args, **kwargs):
        data = request.data
        user_id = data.get('user_id')
        to_user_id = data.get('to_user_id')
        number = data.get('number')
        if user_id and number and to_user_id:
            user_obj = get_user_obj_from_epu(user_id)
            to_user_obj = get_user_obj_from_epu(to_user_id)
            if user_obj and to_user_obj and user_obj.pk != to_user_obj.pk:
                try:
                    IosDeveloperBill.objects.create(user_id=user_obj, to_user_id=to_user_obj,
                                                    status=2, number=number,
                                                    remote_addr=get_real_ip_address(request),
                                                    description=f'{user_obj.first_name} 共享给 {to_user_obj.first_name} {number} 设备数')
                    return ApiResponse()
                except Exception as e:
                    msg = str(e)
            else:
                msg = '用户不合法'
        else:
            msg = '数量和用户不能为空'
        return ApiResponse(code=1001, msg=msg)


class SuperSignBillUserInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        public_balance_info = {}
        private_balance_info = {}
        if user_id:
            user_obj = get_user_obj_from_epu(user_id)
            if user_obj:
                public_balance_info = {
                    'used_balance': get_user_public_used_sign_num(user_obj),
                    'all_balance': get_user_public_sign_num(user_obj)
                }
                use_num = get_developer_devices(AppIOSDeveloperInfo.objects.filter(user_id=user_obj))
                private_balance_info = {
                    'used_balance': use_num.get('flyapp_used_sum', 0) + use_num.get('other_used_sum', 0),
                    'all_balance': use_num.get('max_total', 0)
                }

        return ApiResponse(public_balance_info=public_balance_info, private_balance_info=private_balance_info)
