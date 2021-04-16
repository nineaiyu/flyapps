#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/18
# pip install alipay-sdk-python==3.3.398

# !/usr/bin/env python
# -*- coding: utf-8 -*-


from api.utils.alipay import AliPay
from api.utils.alipay.utils import AliPayConfig
from fir_ser.settings import PAY_CONFIG
from datetime import datetime, timedelta
from api.utils.storage.caches import update_order_info, update_order_status
import json
import logging

logger = logging.getLogger(__file__)


class Alipay(object):
    def __init__(self):
        self.ali_config = PAY_CONFIG.get("ALI")
        self.alipay = self.__get_ali_pay()

    def __get_ali_pay(self):
        return AliPay(
            appid=self.ali_config.get("APP_ID"),
            app_notify_url=self.ali_config.get("APP_NOTIFY_URL"),
            app_private_key_string=self.ali_config.get("APP_PRIVATE_KEY"),
            alipay_public_key_string=self.ali_config.get("ALI_PUBLIC_KEY"),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=False,  # 默认False
            verbose=True,  # 输出调试数据
            config=AliPayConfig(timeout=15)  # 可选, 请求超时时间
        )

    def get_pay_pc_url(self, out_trade_no, total_amount, passback_params):
        time_expire = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        order_string = self.alipay.api_alipay_trade_page_pay(
            out_trade_no=out_trade_no,
            total_amount=total_amount,
            subject=self.ali_config.get("SUBJECT"),
            body="充值 %s 元" % total_amount,
            time_expire=time_expire,
            return_url=self.ali_config.get("RETURN_URL"),
            notify_url=self.ali_config.get("APP_NOTIFY_URL"),
            passback_params=json.dumps(passback_params)
        )

        return "https://openapi.alipay.com/gateway.do?%s" % order_string

    def valid_order(self, data):
        signature = data.pop("sign")
        success = self.alipay.verify(data, signature)
        if success and data["trade_status"] in ("TRADE_SUCCESS", "TRADE_FINISHED"):
            logger.info("付款成功，等待下一步验证 %s" % data)
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
                    logger.error("passback_params %s  user_id not exists" % passback_params)
            else:
                logger.error("APP_ID 校验失败 response: %s  server: %s" % (app_id, self.ali_config.get("APP_ID")))
        return False

    def update_order_status(self, out_trade_no):
        data = self.alipay.api_alipay_trade_query(out_trade_no=out_trade_no)
        # (0, '交易成功'), (1, '待支付'), (2, '订单已创建'),  (3, '退费申请中'), (4, '已退费'), (5, '主动取消'), (6, '超时取消')
        code = data.get("code", '')
        logger.info("out_trade_no: %s info:%s"%(out_trade_no, data))
        if code == '10000':
            trade_status = data.get("trade_status", '')
            if trade_status in ['TRADE_SUCCESS']:
                update_order_status(out_trade_no, 0)
            elif trade_status in ['WAIT_BUYER_PAY']:
                update_order_status(out_trade_no, 2)
        elif code == '40004':
            update_order_status(out_trade_no, 1)
