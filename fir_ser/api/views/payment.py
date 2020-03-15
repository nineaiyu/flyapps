from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from api.utils.auth import ExpiringTokenAuthentication
from django.core.exceptions import ObjectDoesNotExist
from api.utils.response import BaseResponse
from api.models import Course, CouponRecord, Coupon, PricePolicy,Order,OrderDetail
from api.utils.exceptions import CommonException

import random,datetime,time,os,sys
from api.utils.ali.api import ali_api

import redis
from django.conf import settings

REDIS_CONN = redis.Redis(decode_responses=True)

class PaymentView(APIView):
    '''
    模拟请求数据格式：

      {
      is_beli:true,
      course_list=[
                  {  course_id:1
                   default_price_policy_id:1,
                   coupon_record_id:2
                   },
                  { course_id:2
                   default_price_policy_id:4,
                   coupon_record_id:6
                   }
               ],
       global_coupon_id:3,
       pay_money:298

       }


     状态码：
         1000:  成功
         1001:  课程不存在
         1002:  价格策略不合法
         1003:  加入购物车失败
         1004:  获取购物车失败
         1005:  贝里数有问题
         1006:  优惠券异常
         1007:  优惠券未达到最低消费
         1008:  支付总价格异常

    '''
    authentication_classes = [ExpiringTokenAuthentication]

    def get_pay_url(self,request,order_number,final_price):

        # 4 调用支付宝支付接口(二维码页面)

        if request.META["HTTP_USER_AGENT"]:

            pay_api = ali_api.pay.pc

        elif request == "APP":
            pay_api = ali_api.pay.app

        else:
            pay_api = ali_api.pay.wap


        pay_url = pay_api.direct(
            subject="路飞学城",  # 商品简单描述
            out_trade_no=order_number,  # 商户订单号
            total_amount=final_price,  # 交易金额(单位: 元 保留俩位小数)
        )


        print("pay_url",pay_url)
        return pay_url

    def get_order_num(self):
        now=datetime.datetime.now()
        orderType="1"
        dateStr4yyyyMMddHHmmss="{0}{1}{2}".format(now.year,now.month,now.day)
        rand=str(random.randint(1000,9999))

        s=orderType+dateStr4yyyyMMddHHmmss+rand

        return s

    def post(self, request, *args, **kwargs):
        print(request.data)
        response = BaseResponse()
        # 1 获取数据
        user_id = request.user.pk
        global_coupon_id = request.data.get("global_coupon_id")
        pay_money = request.data.get("pay_money")
        course_list = request.data.get("course_list")
        is_beli = request.data.get("is_beli")
        now = datetime.datetime.now()
        try:
            # 2 校验数据
            # 2.2 校验课程
            course_price_list = []
            for course_dict in course_list:
                # 2.2.1 校验课程id

                course_id = course_dict.get("course_id")
                print("course_id",course_id)
                course_obj = Course.objects.get(pk=course_id)
                # 2.2.2 价格策略id
                if course_dict.get("default_price_policy_id") not in [obj.pk for obj in course_obj.price_policy.all()]:
                    raise CommonException("价格策略异常！", 1002)
                # 2.2.3 课程优惠券id

                price_policy_obj = PricePolicy.objects.get(pk=course_dict.get("default_price_policy_id"))
                course_dict["original_price"]=price_policy_obj.price
                course_dict["valid_period_display"]=price_policy_obj.get_valid_period_display()
                course_dict["valid_period"]=price_policy_obj.valid_period
                coupon_record_id = course_dict.get("coupon_record_id")
                if coupon_record_id:

                    coupon_record_list = CouponRecord.objects.filter(account=request.user,
                                                                     status=0,
                                                                     coupon__valid_begin_date__lt=now,
                                                                     coupon__valid_end_date__gt=now,
                                                                     coupon__content_type_id=14,
                                                                     coupon__object_id=course_id
                                                                     )
                    print("coupon_record_id",coupon_record_id)

                    if coupon_record_id and coupon_record_id not in [obj.pk for obj in coupon_record_list]:
                        raise CommonException("课程优惠券异常！", 1006)

                    # 计算循环课程的课程优惠券优惠后的价格
                    coupon_record_obj = CouponRecord.objects.get(pk=coupon_record_id)
                    rebate_price = self.cal_coupon_price(price_policy_obj.price, coupon_record_obj)
                    course_price_list.append(rebate_price)
                    course_dict["rebate_price"]=rebate_price
                else:
                    course_price_list.append(price_policy_obj.price)

            # 2.3 校验通用优惠券id
            global_coupon_record_list = CouponRecord.objects.filter(account=request.user,
                                                                    status=0,
                                                                    coupon__valid_begin_date__lt=now,
                                                                    coupon__valid_end_date__gt=now,
                                                                    coupon__content_type_id=14,
                                                                    coupon__object_id=None
                                                                    )
            if global_coupon_id and global_coupon_id not in [obj.pk for obj in global_coupon_record_list]:
                raise CommonException("通用优惠券异常", 1006)

            if global_coupon_id:
                global_coupon_record_obj = CouponRecord.objects.get(pk=global_coupon_id)
                final_price = self.cal_coupon_price(sum(course_price_list), global_coupon_record_obj)
            else:
                final_price=sum(course_price_list)
            # 2.4 计算实际支付价格与money做校验
            cost_beli_num=0
            if is_beli:
                final_price = final_price - request.user.beli / 10
                cost_beli_num=request.user.beli
                if final_price < 0:
                    final_price = 0
                    cost_beli_num=final_price*10
                print(final_price)

            if final_price != float(pay_money):
                raise CommonException(1008, "支付总价格异常！")

            # 3 生成订单记录
            # Order记录
            # orderDetail
            # orderDetail
            # orderDetail
            order_number=self.get_order_num()
            print("order_number",order_number)
            order_obj=Order.objects.create(
                payment_type=1,
                order_number=order_number,
                account=request.user,
                status=1,
                order_type=1,
                actual_amount=pay_money,
            )
            print("course_list",course_list)

            for course_item in course_list:
                OrderDetail.objects.create(
                    order=order_obj,
                    content_type_id=14,
                    object_id=course_item.get("course_id"),
                    original_price=course_item.get("original_price"),
                    price=course_item.get("rebate_price") or course_item.get("original_price"),
                    valid_period=course_item.get("valid_period"),
                    valid_period_display=course_item.get("valid_period_display"),
                )

            request.user.beli=request.user.beli-cost_beli_num
            request.user.save()
            REDIS_CONN.set(order_number+"|"+str(cost_beli_num),"",20)
            account_key=settings.ACCOUNT_KEY%(user_id,"*")
            REDIS_CONN.delete(*REDIS_CONN.keys(account_key))
            '''
               [
                  {  course_id:1
                     default_price_policy_id:1,
                     coupon_record_id:2
                   },
                  {
                     course_id:2
                     default_price_policy_id:4,
                     coupon_record_id:6
                   }
               ]
            '''


            response.data = self.get_pay_url(request,order_number,final_price)

        except ObjectDoesNotExist as e:
            response.code = 1001
            response.msg = "课程不存在！"
        except CommonException as e:
            response.code = e.code
            response.msg = e.error
        except Exception as e:
            response.code = 500
            response.msg = str(e)

        return Response(response.dict)

    def cal_coupon_price(self, price, coupon_record_obj):
        coupon_type = coupon_record_obj.coupon.coupon_type
        money_equivalent_value = coupon_record_obj.coupon.money_equivalent_value
        off_percent = coupon_record_obj.coupon.off_percent
        minimum_consume = coupon_record_obj.coupon.minimum_consume
        rebate_price = 0
        if coupon_type == 0:  # 立减券
            rebate_price = price - money_equivalent_value
            if rebate_price <= 0:
                rebate_price = 0
        elif coupon_type == 1:  # 满减券
            if minimum_consume > price:
                raise CommonException(1007, "优惠券未达到最低消费")
            else:
                rebate_price = price - money_equivalent_value
        elif coupon_type == 2:
            rebate_price = price * off_percent / 100

        return rebate_price


def get_pay_url(request):
    print('--->',request.GET.get("order_number"))
    pay_url = ali_api.pay.pc.direct(
        subject="python全栈课程",  # 商品简单描述
        out_trade_no=request.GET.get("order_number"),  # 商户订单号
        total_amount=request.GET.get("final_price"),  # 交易金额(单位: 元 保留俩位小数)
    )
    print("pay_url",pay_url)

    return JsonResponse({"pay_url":pay_url})

