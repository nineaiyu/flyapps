#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 1月
# author: NinEveN
# date: 2022/1/6

from django.http import FileResponse
from rest_framework.response import Response

from common.base.baseutils import make_random_uuid


def file_response(stream, filename, content_type):
    return FileResponse(stream, as_attachment=True,
                        filename=filename,
                        content_type=content_type)


def mobileprovision_file_response(file_path):
    return file_response(open(file_path, 'rb'), make_random_uuid() + '.mobileprovision',
                         "application/x-apple-aspen-config")


class ApiResponse(Response):
    def __init__(self, code=1000, msg='success', data=None, status=None, headers=None, content_type=None, **kwargs):
        dic = {
            'code': code,
            'msg': msg
        }
        if data is not None:
            dic['data'] = data
        dic.update(kwargs)
        self._data = data
        # 对象来调用对象的绑定方法，会自动传值
        super().__init__(data=dic, status=status, headers=headers, content_type=content_type)

        # 类来调用对象的绑定方法，这个方法就是一个普通函数，有几个参数就要传几个参数
        # Response.__init__(data=dic,status=status,headers=headers,content_type=content_type)
