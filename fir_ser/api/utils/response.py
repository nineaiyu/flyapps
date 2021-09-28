#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: NinEveN
# date: 2021/4/16


class BaseResponse(object):
    def __init__(self):
        self.code = 1000
        self.msg = "success"
        self.data = None

    @property
    def dict(self):
        return self.__dict__
