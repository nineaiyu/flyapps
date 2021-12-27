#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import APPSuperSignUsedInfo, AppIOSDeveloperInfo, IosDeveloperPublicPoolBill
from api.utils.auth import AdminTokenAuthentication
from api.utils.modelutils import get_user_public_used_sign_num, get_user_public_sign_num, get_user_obj_from_epu
from api.utils.response import BaseResponse
from api.utils.serializer import AdminDeveloperSerializer, AdminSuperSignUsedSerializer, AdminBillInfoSerializer
from api.utils.utils import get_developer_devices
from common.base.baseutils import get_dict_from_filter_fields, get_real_ip_address, get_order_num

logger = logging.getLogger(__name__)


class AppsPageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class DeveloperInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "user_id", "issuer_id", "private_key_id", "certid", "description", "auth_type"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = AppsPageNumber()
        obj_list = AppIOSDeveloperInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminDeveloperSerializer(page_serializer, many=True)
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
        obj = AppIOSDeveloperInfo.objects.filter(pk=pk).first()
        if obj:
            data['pk'] = pk
            serializer = AdminDeveloperSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res.data = serializer.data
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)


class DevicesInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "user_id", "issuer_id", "udid", "name", "bundle_id", "short"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = AppsPageNumber()
        if 'udid' in filter_data:
            filter_data["udid__udid__udid"] = filter_data['udid']
            del filter_data['udid']

        if 'name' in filter_data:
            filter_data["app_id__name"] = filter_data['name']
            del filter_data['name']

        if 'bundle_id' in filter_data:
            filter_data["app_id__bundle_id"] = filter_data['bundle_id']
            del filter_data['bundle_id']

        if 'short' in filter_data:
            filter_data["app_id__short"] = filter_data['short']
            del filter_data['short']

        if 'issuer_id' in filter_data:
            filter_data["developerid__issuer_id"] = filter_data['issuer_id']
            del filter_data['issuer_id']

        obj_list = APPSuperSignUsedInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminSuperSignUsedSerializer(page_serializer, many=True)
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
        obj = AppIOSDeveloperInfo.objects.filter(pk=pk).first()
        if obj:
            data['pk'] = pk
            serializer = AdminDeveloperSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                res.data = serializer.data
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)


class PageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class SuperSignBillView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "user_id", "to_user_id", "action", "udid", "app_id"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = PageNumber()
        obj_list = IosDeveloperPublicPoolBill.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminBillInfoSerializer(page_serializer, many=True)
        res.data = serializer.data
        res.total = obj_list.count()
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        user_id = data.get('user_id')
        to_user_id = data.get('to_user_id')
        number = data.get('number')
        if user_id and number and to_user_id:
            user_obj = get_user_obj_from_epu(user_id)
            to_user_obj = get_user_obj_from_epu(to_user_id)
            if user_obj and to_user_obj and user_obj.pk != to_user_obj.pk:
                try:
                    IosDeveloperPublicPoolBill.objects.create(user_id=user_obj, to_user_id=to_user_obj,
                                                              action=2, number=number,
                                                              remote_addr=get_real_ip_address(request),
                                                              product='后台转账',
                                                              udid=f'oid:{get_order_num()}',
                                                              version=f'{user_obj.first_name} 后台转账 {number} 设备数',
                                                              )
                    return Response(res.dict)
                except Exception as e:
                    res.msg = str(e)
            else:
                res.msg = '用户不合法'
        else:
            res.msg = '数量和用户不能为空'
        res.code = 1001
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
        else:
            order_obj = IosDeveloperPublicPoolBill.objects.filter(pk=pk).first()
            order_obj.delete()
        return Response(res.dict)


class SuperSignBillUserInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        user_id = request.query_params.get('user_id')
        if user_id:
            user_obj = get_user_obj_from_epu(user_id)
            if user_obj:
                res.public_balance_info = {
                    'used_balance': get_user_public_used_sign_num(user_obj),
                    'all_balance': get_user_public_sign_num(user_obj)
                }
                use_num = get_developer_devices(AppIOSDeveloperInfo.objects.filter(user_id=user_obj))
                res.private_balance_info = {
                    'used_balance': use_num.get('flyapp_used_sum', 0) + use_num.get('other_used_sum', 0),
                    'all_balance': use_num.get('max_total', 0)
                }

        return Response(res.dict)
