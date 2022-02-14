#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: NinEveN
# date: 2022/2/14

class DBRouter(object):
    def db_for_read(self, model, **hints):
        #
        # if model._meta.model_name == 'Price':
        #     return 'db1'
        # else:
        #     return 'default'
        return 'slave'

    def db_for_write(self, model, **hints):
        return 'default'
