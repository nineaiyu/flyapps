#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2

"""
    统一收单相关服务
"""

import logging

from .base import BaseAliPayAPI

logger = logging.getLogger(__name__)


class AliOrder(BaseAliPayAPI):

    def query(self, out_biz_no=None, trade_no=None, **kwargs):
        """统一收单线下交易查询.

       Parameters
       ----------
       out_biz_no : string
           订单支付时传入的商户订单号,和支付宝交易号不能同时为空。
           trade_no,out_trade_no如果同时存在优先取trade_no

       trade_no : string
           支付宝交易号，和商户订单号不能同时为空

       Returns
       -------
       dict
       """

        biz_content = {
            "out_biz_no": out_biz_no,
            "trade_no": trade_no
        }

        biz_content.update(kwargs)

        url = self._generate_url("alipay.trade.query", biz_content)

        return self._get(url)
