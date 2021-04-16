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
from api.utils.storage.caches import update_order_status
import logging
from django.utils import timezone
from api.utils.pay.ali import Alipay
from fir_ser.settings import PAY_SUCCESS_URL
from django.http import HttpResponseRedirect

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
        order_number = request.data.get("order_number", None)
        if price_id or order_number:
            price_obj = Price.objects.filter(name=price_id).first()
            order_obj = Order.objects.filter(account=request.user, order_number=order_number).first()
            if order_obj and order_obj.status in [1, 2]:
                alipay = Alipay()
                pay_url = alipay.get_pay_pc_url(order_obj.order_number, order_obj.actual_amount / 100,
                                                {'user_id': request.user.id})
                res.data = pay_url
                return Response(res.dict)
            if price_obj:
                try:
                    order_number = get_order_num()
                    actual_amount = price_obj.price
                    Order.objects.create(payment_type=1, order_number=order_number,
                                         account=request.user, status=1, order_type=0, actual_amount=actual_amount,
                                         actual_download_times=price_obj.package_size,
                                         actual_download_gift_times=price_obj.download_count_gift)
                    alipay = Alipay()
                    pay_url = alipay.get_pay_pc_url(order_number, actual_amount / 100, {'user_id': request.user.id})
                    res.data = pay_url
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
        act = request.data.get("act", None)
        if order_number:
            order_obj = Order.objects.filter(account=request.user, order_number=order_number).first()
            if order_obj:
                try:
                    if act == 'cancel' and order_obj.status != 0:
                        update_order_status(order_number, 5)
                    elif act == 'status' and order_obj.status in [1, 2]:
                        alipay = Alipay()
                        alipay.update_order_status(order_obj.order_number)
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


class PaySuccess(APIView):
    # authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request):
        alipay = Alipay()
        alipay.update_order_status('1202141610723105226256209')
        return Response(111)

        # return HttpResponseRedirect(PAY_SUCCESS_URL)

    def post(self, request):
        alipay = Alipay()
        msg = 'failure'
        data = request.data.copy().dict()
        logger.info("支付回调参数：%s" % data)
        if alipay.valid_order(request.data.copy().dict()):
            msg = 'success'
        return Response(msg)
