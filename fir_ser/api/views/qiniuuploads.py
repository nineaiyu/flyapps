#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6
from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from api.utils.randomstrings import make_from_user_uuid
from rest_framework.response import Response
from fir_ser import settings
from api.utils.app.analyze import AnalyzeUtil, get_random_short,SaveAppInfos
import os
from api.utils.qiniu.tools import QiNiu
from api.models import Apps
from api.utils.randomstrings import make_app_uuid


class QiNiuUploadView(APIView):

    authentication_classes = [ExpiringTokenAuthentication, ]
    def post(self, request):
        res = BaseResponse()
        # 1.接受 bundelid ，返回随机应用名称和短连接
        bundleid = request.data.get("bundleid", None)
        app_type = request.data.get("type", None)

        if bundleid and app_type:
            ap = 'apk'
            if app_type == 'iOS':
                ap='ipa'
            app_uuid = make_app_uuid(request.user, bundleid + ap)
            release_id = make_from_user_uuid(request.user)
            png_id = make_from_user_uuid(request.user)
            app_obj = Apps.objects.filter(app_id=app_uuid).first()
            print(app_obj)
            if app_obj:
                short = app_obj.short
            else:
                short = get_random_short()
            if app_type == 'iOS':
                upload_key = release_id+'.ipa'
            else:
                upload_key = release_id+'.apk'
            png_key = png_id+'.png'
            qiniu = QiNiu()
            res.data = {"app_uuid": app_uuid, "short": short,
                        "domain_name": request.user.domain_name,
                        "upload_token":qiniu.get_qiniu_upload_token(upload_key),
                        "upload_key":upload_key,
                        "png_token":qiniu.get_qiniu_upload_token(png_key),
                        "png_key":png_key}
        else:
            res.code = 1003

        return Response(res.dict)

    def put(self,request):
        res = BaseResponse()
        print(request.data)
        data=request.data
        appinfo={
            "labelname":data.get("appname"),
            "version":data.get("buildversion"),
            "versioncode":data.get("version"),
            "release_type":data.get("release_type"),
            "miniOSversion":data.get("miniosversion"),
            "changelog":data.get("changelog",'')
        }

        try:
            SaveAppInfos(data.get("upload_key"), request.user, appinfo,
                     data.get("bundleid"), data.get("png_key"), data.get("short"), data.get('filesize'))
        except Exception as e:
            print(e)
            res.code = 10003
        return Response(res.dict)

