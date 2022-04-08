#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/22

from django.conf import settings
from django.core.mail import send_mail

from common.base.magic import import_from_string


class EmailMsgSender(object):
    def __init__(self, email_host, email_port, use_tls, use_ssl, subject, username, password, form, template_code):
        self.email_host = email_host
        self.email_port = email_port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.use_ssl = use_ssl
        self.form = form
        self.subject = subject
        self.template_code = template_code
        self.set_settings()

    def set_settings(self):
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        settings.EMAIL_HOST = self.email_host
        settings.EMAIL_PORT = self.email_port
        settings.EMAIL_HOST_USER = self.username
        settings.EMAIL_HOST_PASSWORD = self.password
        settings.EMAIL_FROM = self.form
        settings.EMAIL_USE_TLS = self.use_tls
        settings.EMAIL_USE_SSL = self.use_ssl

    def send_msg(self, template_code, email, code):
        try:
            html_content_obj = import_from_string(template_code)
            content = html_content_obj(code)
            response = send_mail(self.subject % {'code': ''}, content, self.form, [email], html_message=content)
            if response == 1:
                return True, 'OK'
            else:
                return False, 'Send Email Failed'
        except Exception as e:
            return False, e

    def send_email_msg(self, email, text):
        try:
            response = send_mail("重要消息通知", text, self.form, [email], html_message=text)
        except Exception as e:
            return -1, e
        return response, text

    def send_msg_by_act(self, phone, code, act):
        if act not in self.template_code.keys():
            return False, f'act {act} not found'
        return self.send_msg(self.template_code.get(act), phone, code)
