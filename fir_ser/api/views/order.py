from rest_framework.views import APIView
from rest_framework.response import Response
from api.utils.auth import ExpiringTokenAuthentication
from django.core.exceptions import ObjectDoesNotExist
from api.utils.response import BaseResponse
from api.models import Course, CouponRecord, Coupon, PricePolicy, Order, OrderDetail
from api.utils.exceptions import CommonException
import datetime
import uuid
import time
import json

from api.models import Order, OrderDetail


class OrderView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]

    def get(self, request, *args, **kwargs):
        res = BaseResponse()
        order_list = Order.objects.filter(account=request.user).order_by("-date")
        data = []
        for order in order_list:
            data.append({
                "order_number": order.order_number,
                "date": order.date.strftime("%Y-%m-%d %H:%M:%S"),
                "status": order.get_status_display(),
                "actual_amount": order.actual_amount,
                "orderdetail_list": [{
                                         "original_price": obj.original_price,
                                         "price": obj.price,
                                         "course_name": obj.content_object.name,
                                         "valid_period_display": obj.valid_period_display,
                                     } for obj in order.orderdetail_set.all()]
            })

        print("data", data)
        res.data = data

        return Response(res.dict)


