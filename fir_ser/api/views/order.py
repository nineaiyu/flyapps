#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/29

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from api.models import Price, Order
from api.utils.serializer import PriceSerializer, OrdersSerializer
from rest_framework.pagination import PageNumberPagination
from api.utils.utils import get_order_num, get_choices_dict
from api.utils.storage.caches import update_order_status
import logging
from api.utils.pay.util import get_pay_obj_form_name, get_enable_pay_choices, get_payment_type

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
        pay_id = request.data.get("pay_id", None)
        order_number = request.data.get("order_number", None)
        if (price_id and pay_id) or order_number:
            price_obj = Price.objects.filter(name=price_id).first()
            order_obj = Order.objects.filter(account=request.user, order_number=order_number).first()
            if order_obj and order_obj.status in [1, 2] and order_obj.payment_name:
                pay_obj = get_pay_obj_form_name(order_obj.payment_name)
                pay_url = pay_obj.get_pay_pc_url(order_number, int(order_obj.actual_amount),
                                                 {'user_id': request.user.id})
                res.data = pay_url
                logger.info("%s 下单成功 %s" % (request.user, res.dict))
                return Response(res.dict)
            if price_obj:
                try:
                    order_number = get_order_num()
                    actual_amount = price_obj.price
                    pay_obj = get_pay_obj_form_name(pay_id)
                    pay_url = pay_obj.get_pay_pc_url(order_number, int(actual_amount), {'user_id': request.user.id})
                    Order.objects.create(payment_type=get_payment_type(pay_obj.p_type), order_number=order_number,
                                         account=request.user, status=1, order_type=0, actual_amount=actual_amount,
                                         actual_download_times=price_obj.package_size, payment_name=pay_obj.name,
                                         actual_download_gift_times=price_obj.download_count_gift)
                    res.data = pay_url
                    logger.info("%s 下单成功 %s" % (request.user, res.dict))
                    return Response(res.dict)
                except Exception as e:
                    logger.error("%s 订单 %s 保存失败 Exception：%s" % (request.user, price_id, e))
                    res.code = 1003
                    res.msg = "订单保存失败"
            else:
                logger.error("%s 价格 %s 获取失败" % (request.user, price_id))
                res.code = 1002
                res.msg = "价格获取失败，请稍后重试"
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
                        pass
                        # alipay = Alipay()
                        # alipay.update_order_status(order_obj.order_number)
                        # wxpay = Weixinpay()
                        # wxpay.update_order_status(order_obj.order_number)
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
        res.pay_choices = get_enable_pay_choices()
        return Response(res.dict)

    def delete(self, request, price_id):
        res = BaseResponse()
        return Response(res.dict)

    def put(self, request, price_id):
        res = BaseResponse()
        return Response(res.dict)


class PaySuccess(APIView):

    def get(self, request):
        print(request.META)
        return Response(111)

    def post(self, request, name):
        pay_obj = get_pay_obj_form_name(name)
        msg = 'failure'
        if pay_obj:
            logger.info("支付回调参数：%s" % request.body)
            logger.info("支付回调头部：%s" % request.META)
            if pay_obj.p_type == 'ALI':
                if pay_obj.valid_order(request):
                    msg = 'success'
                return Response(msg)
            elif pay_obj.p_type == 'WX':
                if pay_obj.valid_order(request):
                    return Response(msg)
                else:
                    return Response(status=201)
        return Response(status=201, data=msg)