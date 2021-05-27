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

logger = logging.getLogger(__file__)


class SendMessage(object):
    def __init__(self, type):
        '''
        :param type:  sms or email
        '''
        self.type = type
        try:
            if type == 'sms':
                self.sender = self._get_sms_sender()
            elif type == 'email':
                self.sender = self._get_email_sender()
            if self.sender is None:
                raise
        except Exception as e:
            logger.error("get %s sender failed Exception:%s" % (type, e))
            self.sender = None

    def send_register_msg(self, target, code):
        status, msg = self.sender.send_register_msg(target, code)
        logger.info("send_register_msg target:%s code:%s status:%s msg:%s" % (target, code, status, msg))
        return status, msg

    def send_change_msg(self, target, code):
        status, msg = self.sender.send_change_msg(target, code)
        logger.info("send_change_msg target:%s code:%s status:%s msg:%s" % (target, code, status, msg))
        return status, msg

    def send_login_msg(self, target, code):
        status, msg = self.sender.send_login_msg(target, code)
        logger.info("send_login_msg target:%s code:%s status:%s msg:%s" % (target, code, status, msg))
        return status, msg

    def send_email_msg(self, email, text):
        if self.type == 'email':
            status, msg = self.sender.send_email_msg(email, text)
            logger.info("send_email_msg target:%s text:%s status:%s msg:%s" % (email, text, status, msg))
            return status, msg

    def _get_email_sender(self):
        return self._get_default_sender(0)

    def _get_sms_sender(self):
        return self._get_default_sender(1)

    def _get_default_sender(self, type):
        '''
            sender_type :
                0: 邮件
                1: 阿里云
                2: 极光
        '''
        sender_lists = THIRD_PART_CONFIG.get('sender')
        for sender in sender_lists:
            if sender.get("active", None):
                sender_type = sender.get('type', None)
                auth = sender.get('auth', {})
                if sender_type == 0 and type == 0:
                    return EmailMsgSender(**auth)
                if sender_type == 1:
                    return AliMsgSender(**auth)
                elif sender_type == 2:
                    return JiGuangMsgSender(**auth)
                else:
                    continue
        return None
