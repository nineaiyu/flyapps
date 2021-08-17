#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/23

from .aliyunApi import AliMsgSender
from .emailApi import EmailMsgSender
from .jiguangApi import JiGuangMsgSender
from fir_ser.settings import THIRD_PART_CONFIG
import logging

logger = logging.getLogger(__name__)


def get_default_sender(send_type):
    """
        sender_type :
            0: 邮件
            1: 阿里云
            2: 极光
    """
    sender_lists = THIRD_PART_CONFIG.get('sender')
    for sender in sender_lists:
        if sender.get("active", None):
            sender_type = sender.get('type', None)
            auth = sender.get('auth', {})
            if sender_type == 0 and send_type == 0:
                return EmailMsgSender(**auth)
            if sender_type == 1:
                return AliMsgSender(**auth)
            elif sender_type == 2:
                return JiGuangMsgSender(**auth)
            else:
                continue
    return None


def get_sms_sender():
    return get_default_sender(1)


def get_email_sender():
    return get_default_sender(0)


class SendMessage(object):
    def __init__(self, send_type):
        """
        :param send_type:  sms or email
        """
        self.send_type = send_type
        try:
            if send_type == 'sms':
                self.sender = get_sms_sender()
            elif send_type == 'email':
                self.sender = get_email_sender()
            if self.sender is None:
                raise
        except Exception as e:
            logger.error(f"get {send_type} sender failed Exception:{e}")
            self.sender = None

    def send_email_msg(self, email, text):
        if self.send_type == 'email':
            status, msg = self.sender.send_email_msg(email, text)
            logger.info(f"send_email_msg target:{email} text:{text} status:{status} msg:{msg}")
            return status, msg

    def send_msg_by_act(self, target, code, act):
        status, msg = self.sender.send_msg_by_act(target, code, act)
        logger.info(f"send_{act}_msg target:{target} code:{code} status:{status} msg:{msg}")
        return status, msg
