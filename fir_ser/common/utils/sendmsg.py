#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/23

import logging

from common.cache.storage import TempCache
from common.core.sysconfig import Config
from common.libs.sendmsg.aliyunApi import AliMsgSender
from common.libs.sendmsg.emailApi import EmailMsgSender
from common.libs.sendmsg.jiguangApi import JiGuangMsgSender
from common.utils.token import generate_numeric_token_of_length, make_token, verify_token

logger = logging.getLogger(__name__)


class SendMessage(object):
    def __init__(self, sender_type):
        """
        :param sender_type:  sms or email
        """
        self.sender_type = sender_type
        try:
            self.sender = self.__get_default_sender()
            if self.sender is None:
                raise
        except Exception as e:
            logger.error(f"get {sender_type} sender failed Exception:{e}")
            self.sender = None

    def __get_default_sender(self):
        """
            sender_type :
                0: 邮件
                1: 阿里云
                2: 极光
        """
        for sender in Config.SENDER:
            if sender.get("active", None):
                sender_type = sender.get('type', None)
                auth = sender.get('auth', {})
                if sender_type == 0 and self.sender_type == 'email':
                    return EmailMsgSender(**auth)
                if sender_type == 1:
                    return AliMsgSender(**auth)
                elif sender_type == 2:
                    return JiGuangMsgSender(**auth)
                else:
                    continue
        return None

    def send_email_msg(self, email, text):
        if self.sender_type == 'email':
            status, msg = self.sender.send_email_msg(email, text)
            logger.info(f"send_email_msg target:{email} text:{text} status:{status} msg:{msg}")
            return status, msg

    def send_msg_by_act(self, target, code, act):
        status, msg = self.sender.send_msg_by_act(target, code, act)
        logger.info(f"send_{act}_msg target:{target} code:{code} status:{status} msg:{msg}")
        return status, msg


def get_sender_token(sender, user_id, target, action, msg=None):
    code = generate_numeric_token_of_length(6)
    if msg:
        code = msg
    if target in Config.WHITE_SENDER_LIST:
        code = str(Config.WHITE_SENDER_CODE)
    token = make_token(code, time_limit=300, key=user_id)
    TempCache(user_id, token).set_storage_cache(target, 60 * 5)
    if target in Config.WHITE_SENDER_LIST:
        return token, code
    if action in ('change', 'password', 'register', 'login', 'common'):
        sender.send_msg_by_act(target, code, action)
    elif action == 'msg':
        sender.send_email_msg(target, msg)
    else:
        logger.error(f"get_sender_token failed. action is {action}")
        return None, None
    return token, code


def get_sender_sms_token(key, phone, action, msg=None):
    sender = SendMessage('sms')
    if sender.sender:
        return get_sender_token(sender, key, phone, action, msg)
    return False, False


def is_valid_sender_code(key, token, code, success_once=False):
    return verify_token(token, code, success_once), TempCache(key, token).get_storage_cache()


def get_sender_email_token(key, email, action, msg=None):
    sender = SendMessage('email')
    if sender.sender:
        return get_sender_token(sender, key, email, action, msg)
    return False, False
