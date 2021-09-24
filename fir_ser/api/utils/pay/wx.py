#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/18

from api.utils.pay.wxpay import WeChatPay, WeChatPayType
from datetime import datetime, timedelta
from api.utils.storage.caches import update_order_info, update_order_status
import json
import logging

logger = logging.getLogger('pay')


class Weixinpay(object):
    def __init__(self, name, p_type, auth):
        self.p_type = p_type
        self.wx_config = auth
        self.name = name
        self.wxpay = self.__get_wx_pay()

    def __get_wx_pay(self):
        return WeChatPay(wechatpay_type=WeChatPayType.NATIVE,
                         mchid=self.wx_config.get('MCH_ID'),
                         parivate_key=self.wx_config.get('APP_PRIVATE_KEY'),
                         cert_serial_no=self.wx_config.get('SERIAL_NO'),
                         appid=self.wx_config.get('APP_ID'),
                         notify_url="%s/%s" % (self.wx_config.get('APP_NOTIFY_URL'), self.name),
                         apiv3_key=self.wx_config.get('API_V3_KEY')
                         )

    def get_pay_pc_url(self, out_trade_no, total_amount, passback_params):
        passback_params.update({'name': self.name})
        time_expire = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S+08:00")
        code, data = self.wxpay.pay(
            description=self.wx_config.get('SUBJECT'),
            out_trade_no=out_trade_no,
            amount={
                'total': total_amount,  # 订单总金额，单位为分。示例值：100
                'currency': 'CNY'
            },
            time_expire=time_expire,
            attach=json.dumps(passback_params),
        )
        result = {'type': self.p_type, 'url': json.loads(data).get('code_url', ''), 'out_trade_no': out_trade_no}
        logger.info(f"微信支付连接生成成功 {result}")
        return result

    def valid_order(self, request):
        headers = {
            'Wechatpay-Signature': request.META.get('HTTP_WECHATPAY_SIGNATURE'),
            'Wechatpay-Timestamp': request.META.get('HTTP_WECHATPAY_TIMESTAMP'),
            'Wechatpay-Nonce': request.META.get('HTTP_WECHATPAY_NONCE'),
            'Wechatpay-Serial': request.META.get('HTTP_WECHATPAY_SERIAL'),
        }
        result = self.wxpay.decrypt_callback(headers, request.body.decode('utf-8'))
        if result:
            logger.info(f"付款成功，等待下一步验证 {result}")
            data = json.loads(result)
            passback_params = data.get("attach", "")
            out_trade_no = data.get("out_trade_no", "")
            if passback_params:
                ext_parms = json.loads(passback_params)
                user_id = ext_parms.get("user_id")
                transaction_id = data.get("transaction_id", "")
                return update_order_info(user_id, out_trade_no, transaction_id, 0)
            else:
                logger.error(f"passback_params {passback_params}  user_id not exists")
        else:
            logger.error(f"消息解密失败 {request.body}")
        return False

    def update_order_status(self, out_trade_no):
        code, data = self.wxpay.query(out_trade_no=out_trade_no)
        # (0, '交易成功'), (1, '待支付'), (2, '订单已创建'),  (3, '退费申请中'), (4, '已退费'), (5, '主动取消'), (6, '超时取消')
        data = json.loads(data)
        logger.info(f"out_trade_no: {out_trade_no} info:{data}")
        if code == 200:
            trade_status = data.get("trade_state", '')
            if trade_status in ['SUCCESS']:
                update_order_status(out_trade_no, 0)
            elif trade_status in ['NOTPAY']:
                update_order_status(out_trade_no, 2)
        elif code == 404:
            update_order_status(out_trade_no, 1)
