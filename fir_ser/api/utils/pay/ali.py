#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/18
# pip install alipay-sdk-python==3.3.398


from api.utils.pay.alipay import AliPay
from api.utils.pay.alipay.utils import AliPayConfig
from datetime import datetime, timedelta
from api.utils.storage.caches import update_order_info, update_order_status
import json
import logging

logger = logging.getLogger(__name__)


class Alipay(object):
    def __init__(self, name, p_type, auth):
        self.p_type = p_type
        self.name = name
        self.ali_config = auth
        self.alipay = self.__get_ali_pay()

    def __get_ali_pay(self):
        return AliPay(
            appid=self.ali_config.get("APP_ID"),
            app_notify_url="%s/%s" % (self.ali_config.get("APP_NOTIFY_URL"), self.name),
            app_private_key_string=self.ali_config.get("APP_PRIVATE_KEY"),
            alipay_public_key_string=self.ali_config.get("ALI_PUBLIC_KEY"),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False,  # 默认False
            verbose=True,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
        )

    def get_pay_pc_url(self, out_trade_no, total_amount, passback_params):
        passback_params.update({'name': self.name})
        time_expire = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        order_string = self.alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=total_amount / 100,
            subject=self.ali_config.get("SUBJECT"),
            body="充值 %s 元" % str(total_amount / 100),
            time_expire=time_expire,
            return_url=self.ali_config.get("RETURN_URL"),
            passback_params=json.dumps(passback_params)
        )

        return {'type': self.p_type, 'url': "https://openapi.alipay.com/gateway.do?%s" % order_string,
                'out_trade_no': out_trade_no}

    def valid_order(self, request):
        data = request.data.copy().dict()
        signature = data.pop("sign")
        success = self.alipay.verify(data, signature)
        if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            logger.info(f"付款成功，等待下一步验证 {data}")
            app_id = data.get("app_id", "")
            if app_id == self.ali_config.get("APP_ID"):
                out_trade_no = data.get("out_trade_no", "")  # 服务器订单号
                passback_params = data.get("passback_params", "")
                if passback_params:
                    ext_parms = json.loads(passback_params)
                    user_id = ext_parms.get("user_id")
                    payment_number = data.get("trade_no", "")
                    return update_order_info(user_id, out_trade_no, payment_number, 1)
                else:
                    logger.error(f"passback_params {passback_params}  user_id not exists")
            else:
                logger.error(f"APP_ID 校验失败 response: {app_id}  server: {self.ali_config.get('APP_ID')}")
        return False

    def update_order_status(self, out_trade_no):
        data = self.alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
        code = data.get("code", '')
        logger.info(f"out_trade_no: {out_trade_no} info:{data}")
        if code == '10000':
            trade_status = data.get("trade_status", '')
            if trade_status in ['TRADE_SUCCESS']:
                update_order_status(out_trade_no, 0)
            elif trade_status in ['WAIT_BUYER_PAY']:
                update_order_status(out_trade_no, 2)
        elif code == '40004':
            update_order_status(out_trade_no, 1)
