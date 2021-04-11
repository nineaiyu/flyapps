#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/29

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from api.models import UserInfo, Price, Order
from api.utils.serializer import PriceSerializer, OrdersSerializer
from rest_framework.pagination import PageNumberPagination
from api.utils.utils import get_order_num, get_choices_dict
from api.utils.storage.caches import add_user_download_times
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class PageNumber(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class OrderView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        order_id = request.query_params.get("order_id", None)
        order_obj_lists = Order.objects.filter(account=request.user)
        if order_id:
            order_obj_lists = order_obj_lists.filter(order_number=order_id)
        page_obj = PageNumber()
        order_info_serializer = page_obj.paginate_queryset(queryset=order_obj_lists.order_by("-created_time"),
                                                           request=request,
                                                           view=self)
        order_info = OrdersSerializer(order_info_serializer, many=True, )
        res.data = order_info.data
        res.count = order_obj_lists.count()

        res.payment_type_choices = get_choices_dict(Order.payment_type_choices)
        res.status_choices = get_choices_dict(Order.status_choices)
        res.order_type_choices = get_choices_dict(Order.order_type_choices)

        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        price_id = request.data.get("price_id", None)
        if price_id:
            price_obj = Price.objects.filter(name=price_id).first()
            if price_obj:
                try:
                    Order.objects.create(payment_type=0, order_number=get_order_num(),
                                         account=request.user, status=1, order_type=0, actual_amount=price_obj.price,
                                         actual_download_times=price_obj.package_size,
                                         actual_download_gift_times=price_obj.download_count_gift)
                    return Response(res.dict)
                except Exception as e:
                    logger.error("%s 订单 %s 保存失败 Exception：%s" % (request.user, price_id, e))
                    res.code = 1003
                    res.msg = "订单保存失败"
            else:
                logger.error("%s 价格 %s 获取失败" % (request.user, price_id))
                res.code = 1002
                res.msg = "价格获取失败"
        else:
            res.code = 1001
            res.msg = "错误的价格"
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        order_number = request.data.get("order_number", None)
        if order_number:
            order_obj = Order.objects.filter(account=request.user, order_number=order_number, status=1).first()
            if order_obj:
                download_times = order_obj.actual_download_times + order_obj.actual_download_gift_times
                try:
                    order_obj.status = 0
                    now = timezone.now()
                    if not timezone.is_naive(now):
                        now = timezone.make_naive(now, timezone.utc)
                    order_obj.pay_time = now
                    n_download_times = UserInfo.objects.filter(pk=request.user.id).values('download_times').first()
                    order_obj.description = "充值成功，充值下载次数 %s ，现总共可用次数 %s" % (
                        download_times, n_download_times.get("download_times", 0))
                    order_obj.save()
                    add_user_download_times(request.user.id, download_times)
                except Exception as e:
                    logger.error("%s 订单 %s 更新失败 Exception：%s" % (request.user, order_number, e))
                    res.code = 1003
                return Response(res.dict)
            else:
                logger.error("%s 订单 %s 获取失败" % (request.user, order_number))
                res.code = 1003
                res.msg = "订单获取失败，或订单已经支付"
        else:
            res.code = 1001
            res.msg = "订单有误"
        return Response(res.dict)


class PriceView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        price_obj_lists = Price.objects.filter(is_enable=True).all().order_by("updated_time").order_by("price")
        res.data = PriceSerializer(price_obj_lists, many=True).data
        return Response(res.dict)

    def delete(self, request, price_id):
        res = BaseResponse()
        return Response(res.dict)

    def put(self, request, price_id):
        res = BaseResponse()
        return Response(res.dict)
