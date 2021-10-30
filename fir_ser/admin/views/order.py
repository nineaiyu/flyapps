#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import UserInfo, Order
from api.utils.auth import AdminTokenAuthentication
from api.utils.baseutils import get_dict_from_filter_fields
from api.utils.response import BaseResponse
from api.utils.serializer import AdminOrdersSerializer
from api.utils.storage.caches import update_order_info
from api.utils.utils import get_order_num

logger = logging.getLogger(__name__)


class PageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class OrderInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "user_id", "payment_type", "payment_name", "payment_number", "order_number", "status",
                         "order_type"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        page_obj = PageNumber()
        obj_list = Order.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminOrdersSerializer(page_serializer, many=True)
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
        obj = Order.objects.filter(pk=pk).first()
        old_status = obj.status
        new_status = data.get('status', -99)
        if obj:
            data['pk'] = pk
            serializer = AdminOrdersSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                if old_status != new_status and new_status == 0:
                    update_order_info(obj.user_id.pk, obj.order_number, obj.order_number, obj.payment_type)
                else:
                    serializer.save()
                res.data = serializer.data
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
            order_obj = Order.objects.filter(pk=pk).first()
            order_obj.delete()
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        amount = data.get("amount", 0)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        obj = UserInfo.objects.filter(pk=pk).first()
        if obj:
            if amount > 0:
                order_number = get_order_num()
                order_obj = Order.objects.create(payment_type=2, order_number=order_number, payment_number=order_number,
                                                 user_id=obj, status=1, order_type=1, actual_amount=0,
                                                 actual_download_times=amount, payment_name='后台管理员充值',
                                                 actual_download_gift_times=0)
                if update_order_info(obj.pk, order_obj.order_number, order_obj.order_number, order_obj.payment_type):
                    return Response(res.dict)
                else:
                    res.code = 1005
                    res.msg = "订单创建失败"
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)
