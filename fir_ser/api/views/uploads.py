#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6
from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from django.http.multipartparser import MultiPartParser
from api.utils.randomstrings import make_from_user_uuid
from rest_framework.response import Response
from fir_ser import settings
from api.utils.app.analyze import AnalyzeUtil
import os

class UploadView(APIView):
    '''
    上传文件接口
    '''
    authentication_classes = [ExpiringTokenAuthentication, ]
    # parser_classes = (MultiPartParser,)

    def post(self, request,*args,**kwargs):
        res = BaseResponse()

        # 获取多个file
        files = request.FILES.getlist('file', None)
        for file_obj in files:
            # 将文件缓存到本地后上传
            try:
                app_type = file_obj.name.split(".")[-1]
                if app_type != "apk" and app_type != "ipa" :
                    raise
            except Exception as e:
                res.code = 1003
                res.msg = "错误的类型"
                return Response(res.dict)

            random_file_name = make_from_user_uuid(request.user)
            local_file = os.path.join(settings.MEDIA_ROOT,"apps","%s"%(random_file_name+"."+app_type))
            # 读取传入的文件
            try:
                destination = open(local_file, 'wb+')
                for chunk in file_obj.chunks():
                    # 写入本地文件
                    destination.write(chunk)
                destination.close()
            except Exception as e:
                res.code = 1003
                res.msg = "数据写入失败"
                return Response(res.dict)

            try:
                AnalyzeUtil("%s"%(random_file_name+"."+app_type),request)
            except Exception as e:
                res.code = 1003
                res.msg = "应用解析失败"
                return Response(res.dict)

        return Response(res.dict)


class UploadImgView(APIView):
    '''
    上传图片接口
    '''
    authentication_classes = [ExpiringTokenAuthentication, ]

    def post(self, request):
        res = BaseResponse()

        # 获取多个file
        files = request.FILES.getlist('file', None)
        uid = request.data.get("uid",None)
        print(uid)
        for file_obj in files:
            # 将文件缓存到本地后上传
            try:
                app_type = file_obj.name.split(".")[-1]
                if app_type in ['png','jpeg','jpg']:
                    #上传图片
                    pass
                else:
                    raise

            except Exception as e:
                res.code = 1003
                res.msg = "错误的类型"
                return Response(res.dict)

            random_file_name = make_from_user_uuid(request.user)
            local_file = os.path.join(settings.MEDIA_ROOT,"apps","%s"%(random_file_name+"."+app_type))
            # 读取传入的文件
            try:
                destination = open(local_file, 'wb+')
                for chunk in file_obj.chunks():
                    # 写入本地文件
                    destination.write(chunk)
                destination.close()
            except Exception as e:
                res.code = 1003
                res.msg = "数据写入失败"
                return Response(res.dict)


        return Response(res.dict)