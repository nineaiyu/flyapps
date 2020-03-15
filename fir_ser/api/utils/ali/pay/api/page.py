#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2

"""
    PC支付场景
"""

import logging

from .base import BaseAliPayAPI

logger = logging.getLogger(__name__)


class AliPage(BaseAliPayAPI):

    def direct(self, subject, out_trade_no, total_amount, notify_url=None, return_url=None, **kwargs):
        """PC快速下单接口

        文档DOC地址: https://docs.open.alipay.com/270/alipay.trade.page.pay

        Parameters
        ----------

        subject : string
            订单标题

        out_trade_no : string
            商户订单号唯一凭证

        total_amount : string or float or int
            支付金额，单位元，精确到分

        notify_url: string

            支付宝服务器主动通知商户服务器里指定的页面http/https路径

            example: http://www.alipay.com/pay

        return_url: string

            同步返回地址，HTTP/HTTPS开头字符串

        kwargs : dict
            以下均为可选参数

            body : string
                订单描述

            goods_detail : json
                订单包含的商品列表信息，Json格式： {&quot;show_url&quot;:&quot;https://或http://打头的商品的展示地址&quot;}
                在支付时，可点击商品名称跳转到该地址

            passback_params : string
                公用回传参数，如果请求时传递了该参数，则返回给商户时会回传该参数。
                支付宝只会在异步通知时将该参数原样返回。
                本参数必须进行UrlEncode之后才可以发送给支付宝

            goods_type : int
                商品主类型：0; 虚拟类商品，1; 实物类商品（默认）

            extend_params :
                业务扩张参数(主要用于接入花呗分期)

        Returns
        -------
        dict
        """

        biz_content = {
            "subject": subject,
            "out_trade_no": out_trade_no,
            "total_amount": total_amount,
            "product_code": "FAST_INSTANT_TRADE_PAY",  # 销售产品码，目前仅支持这个类型
            # "qr_pay_mode":4
        }

        biz_content.update(**kwargs)

        return self._generate_url("alipay.trade.page.pay", biz_content, notify_url, return_url)
