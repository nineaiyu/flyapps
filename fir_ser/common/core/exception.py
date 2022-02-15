#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 1月 
# author: NinEveN
# date: 2022/1/13
import logging

from rest_framework.views import exception_handler

from common.core.response import ApiResponse

logger = logging.getLogger(__file__)


def common_exception_handler(exc, context):
    logger.error(f'{context["view"].__class__.__name__} ERROR: {exc}')
    # context['view']  是TextView的对象，想拿出这个对象对应的类名
    ret = exception_handler(exc, context)  # 是Response对象，它内部有个data

    if not ret:  # drf内置处理不了，丢给django 的，我们自己来处理
        return ApiResponse(msg='error', result=str(exc))
    else:
        return ApiResponse(msg='error', status=ret.status_code, **ret.data, )
