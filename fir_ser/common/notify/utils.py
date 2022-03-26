#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: wx
# author: liuyu
# data: 2022/3/23
import logging

from api.utils.modelutils import get_notify_email_queryset
from common.utils.sendmsg import get_sender_email_token

logger = logging.getLogger(__name__)


def notify_by_email(user_obj, message_type, msg):
    for notify_email in get_notify_email_queryset(user_obj, message_type):
        email = notify_email.get('email')
        if email:
            get_sender_email_token('email', email, 'msg', f'您好，{user_obj.first_name}，{msg}')
