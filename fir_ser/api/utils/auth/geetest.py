#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: liuyu
# date: 2022/2/7
import hashlib
import logging

from common.libs.geetest.geetest_utils import first_register, second_validate

logger = logging.getLogger(__name__)


class GeeTestAuth(object):
    def __init__(self, unique_key='', ip_address=''):
        self.ip_address = ip_address
        self.unique_key = unique_key

    def generate(self):
        assert self.unique_key
        assert self.ip_address
        sha = hashlib.sha1(str(self.unique_key).encode("utf-8"))
        return first_register(sha.hexdigest(), self.ip_address)

    def valid(self, geetest_data):
        return second_validate(geetest_data).get("result", "") == "success"
