
from rest_framework.views import APIView
from api.utils.ali.api import ali_api
from api.utils.ali.tools import verify_signature
from rest_framework.response import Response
from api.models import Order
import datetime,time
from django.shortcuts import HttpResponse,redirect
from api.utils.response import BaseResponse

class AlipayTradeView(APIView):

    def get(self,request,*args,**kwargs):

       try:
            processed_dict = {}
            for key, value in self.request.query_params.items():
                processed_dict[key] = value
            # 校验签名
            verify_result = verify_signature(processed_dict, ali_api.pay.ali_public_key)

            if not verify_result:
                return HttpResponse("sign is invalid")

            out_trade_no = processed_dict.get("out_trade_no")  # 商户订单号
            redirect_to = "{0}?order_num={1}".format("http://47.94.172.250:8804/order/pay_success",out_trade_no)
            return redirect(redirect_to)

       except Exception as e:
          return HttpResponse("fail!")


    def post(self, request):
        """
        处理支付宝的notify_url

        支付宝对应交易的四种状态:
            1,WAIT_BUYER_PAY    交易创建，等待买家付款
            2,TRADE_CLOSED      未付款交易超时关闭，或支付完成后全额退款
            3,TRADE_SUCCESS     交易支付成功
            4,TRADE_FINISHED    交易结束，不可退款

        如果支付成功, 将要处理的事件:
            1, 订单状态更改为交易完成(变更状态后, 通过信号进行如下操作)
            2, 如果使用优惠券, 支付成功将要把优惠券的状态更改为已使用
            3, 如果使用余额, 将要进行扣除
        """
        processed_dict = {}
        for key, value in self.request.data.items():
            processed_dict[key] = value
        # 校验签名
        verify_result = verify_signature(processed_dict, ali_api.pay.ali_public_key)

        if not verify_result:
            return Response("fail")

        order_sn = processed_dict.get("out_trade_no", "")  # 商户网站唯一订单号
        trade_no = processed_dict.get("trade_no", "")  # 该交易在支付宝系统中的交易流水号。最长64位
        trade_status = processed_dict.get("trade_status", "")  # 支付宝系统的交易状态
        # 支付成功
        #   为放止支付宝重复请求, 获取到订单号并查询该订单的状态是否为交易完成, 如果交易完成, 即直接返回成功信号
        #   为该用户创建报名课程, 创建报名时间及结束时间
        #   区分LuffyX课程 和 付费课程
        #   当前策略LuffyX课程是不能加入购物车的
        if trade_status == "TRADE_SUCCESS":
            gmt_payment = processed_dict.get("gmt_payment")  # 买家付款时间 格式 yyyy-MM-dd HH:mm:ss
            passback_params = processed_dict.get("passback_params", "{}")  # 公共回传参数

            # 修改订单状态
            save_status = self.change_order_status(order_sn, trade_no, gmt_payment, "alipay",passback_params)
            if save_status is True:
                return Response("success")
        return Response("fail")


    def change_order_status(order_num, payment_number, gmt_payment, trade_type, extra_params):
        """交易成功修改订单相关的状态

        Parameters
        ----------
        order_num : string
            订单号

        payment_number : string or None
            第三方订单号

        gmt_payment : string
            交易时间(要根据不同的交易方式格式化交易时间)

        trade_type: string
            交易方式

        extra_params: string json
            交易回传参数

        Returns
        -------
        bool
        """
        try:
            exist_order = Order.objects.get(order_number=order_num)
            pay_time = datetime.datetime.strptime(gmt_payment, "%Y-%m-%d %H:%M:%S")

            if exist_order.status == 0:
                return True
            # 变更订单状态
            exist_order.payment_number = payment_number
            exist_order.status = 0
            exist_order.pay_time = pay_time
            exist_order.save(update_fields=("payment_number", "status", "pay_time", ),)
        except Exception as e:
            pass

        return True
