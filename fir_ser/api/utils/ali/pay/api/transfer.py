#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2

"""
    转账支付 `api`
"""

import logging

from .base import BaseAliPayAPI

logger = logging.getLogger(__name__)


class AliTransfer(BaseAliPayAPI):

    def transfer(self, out_biz_no, payee_account, amount, payee_real_name, is_verify=True, **kwargs):
        """转账接口

            在构建完成数据结构体之前进行验证码校验

            该方法加入了 业务代码, 业务若有变动, 请根据实际需求进行更改

        Parameters
        ----------
        out_biz_no : string
            商户转账唯一凭证

        payee_account : string
            收款方账户

        amount : string or int or float
            转账金额(单位: 元, 保留俩位小数, 最小转帐金额 0.1元)

        payee_real_name: string
            收款方真实姓名

        is_verify: bool, default: True
            是否进行验证码校验

        kwargs : dict
            以下均为可选参数

            payer_show_name : string
                付款方姓名

            remark : string
                转账备注（支持200个英文/100个汉字）。当付款方为企业账户，且转账金额达到（大于等于）50000元，remark不能为空。
                收款方可见，会展示在收款用户的收支详情中。

        Returns
        -------
        dict
        """

        # 如果需要校验, 获取验证码进行校验, 校验不通过直接响应校验不通过
        if is_verify:
            kwargs.pop("verify_code", None)

        biz_content = {
            "out_biz_no": out_biz_no,
            "payee_account": payee_account,
            "payee_type": "ALIPAY_LOGONID",  # 收款方账户类型
            "amount": amount,
            "payee_real_name": payee_real_name
        }

        biz_content.update(**kwargs)

        url = self._generate_url("alipay.fund.trans.toaccount.transfer", biz_content)

        return self._get(url)

    def query(self, out_biz_no, order_id, **kwargs):
        """转账交易查询接口.

       Parameters
       ----------
       out_biz_no : string
           商户转账唯一凭证

       order_id : string
           支付宝商户转账唯一凭证

       Returns
       -------
       dict
       """

        biz_content = {
            "out_biz_no": out_biz_no,
            "order_id": order_id
        }

        biz_content.update(kwargs)

        url = self._generate_url("alipay.fund.trans.order.query", biz_content)

        return self._get(url)
