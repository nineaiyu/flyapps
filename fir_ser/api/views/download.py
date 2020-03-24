#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6
from rest_framework.views import APIView
from api.utils.response import BaseResponse
from rest_framework.response import Response
from fir_ser import settings
from api.utils.TokenManager import DownloadToken
import os

from api.utils.serializer import AppsSerializer
from api.models import Apps,AppReleaseInfo
from django.http import FileResponse
class DownloadView(APIView):
    '''
    文件下载接口
    '''
    # authentication_classes = [ExpiringTokenAuthentication, ]
    # parser_classes = (MultiPartParser,)

    def get(self,request,filename):

        # release_id = release_id.split(".")[1]
        res = BaseResponse()
        print(filename)
        downtoken = request.query_params.get("token", None)
        iostype = request.query_params.get("type",None)
        if not downtoken:
            res.code=1004
            res.msg="缺失token"
            return Response(res.dict)

        dtoken = DownloadToken()
        if dtoken.verify_token(downtoken,filename):
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            try:
                response = FileResponse(open(file_path, 'rb'))
            except Exception as e:
                print(e)
                response = FileResponse()
            response['content_type'] = "application/octet-stream"
            response['Content-Disposition'] = 'attachment; filename=' + filename
            return response
        else:
            res.code=1004
            res.msg="token校验失败"
            return Response(res.dict)


        #     #校验成功，可以下载数据
        #     apprelease_obj = AppReleaseInfo.objects.filter(release_id=release_id).first()
        #     if apprelease_obj:
        #         try:
        #             app_type="ipa"
        #             if apprelease_obj.release_type == 0:
        #                 app_type = "apk"
        #
        #             if iostype == "resigned.plist":
        #                 file_path=make_random_uuid()
        #
        #                 downtoken=dtoken.make_token([release_id])
        #                 domain_name = apprelease_obj.app_id.user_id.domain_name
        #                 if not domain_name:
        #                     ser_url = request.META.get("HTTP_HOST", "/")
        #                     SERVER_PROTOCOL = request.META.get("SERVER_PROTOCOL", "http/1.1")
        #                     ser_protocol = SERVER_PROTOCOL.split("/")[0].lower()
        #                     domain_name = "%s://%s" % (ser_protocol, ser_url)
        #                 bin_url = domain_name+"/download/"+\
        #                           release_id+"?token="+\
        #                           downtoken
        #                 img_url=apprelease_obj.icon_url
        #                 bundle_id = apprelease_obj.app_id.bundle_id
        #                 bundle_version = apprelease_obj.build_version
        #                 name = apprelease_obj.app_id.name
        #                 ios_plist_bytes = make_resigned(bin_url,img_url,bundle_id,bundle_version,name)
        #                 response = FileResponse(ios_plist_bytes)
        #                 response['content_type'] = "text/xml"
        #
        #
        #             else:
        #
        #                 apprelease_obj.app_id.count_hits+=1
        #                 apprelease_obj.app_id.save()
        #
        #                 file_path = os.path.join(settings.MEDIA_ROOT,"apps","%s"%(release_id+"."+app_type))
        #                 response = FileResponse(open(file_path, 'rb'))
        #                 response['content_type'] = "application/octet-stream"
        #             response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
        #             return response
        #         except Exception:
        #             raise Http404
        #         pass
        # else:
        #     res.code=1004
        #     res.msg="token校验失败"
        #     return Response(res.dict)

class DownloadTokenView(APIView):
    '''
    获取下载的token信息
    '''
    # authentication_classes = [ExpiringTokenAuthentication, ]
    # parser_classes = (MultiPartParser,)

    def get(self,request,short):
        res = BaseResponse()
        release_ids=[]

        release_id = request.query_params.get("release_id", None)
        if release_id:
            release_ids = [release_id]
            # res.data["release_id"] = release_id

        dtoken = DownloadToken()
        app_obj = Apps.objects.filter(short=short).first()
        # release_id = AppReleaseInfo.objects.filter(app_id=app_obj).first().release_id
        if not app_obj:
            res.code=1003
            res.msg="该应用不存在"
            return Response(res.dict)

        app_release_obj = AppReleaseInfo.objects.filter(app_id=app_obj,is_master=True).first()
        release_ids.append(app_release_obj.release_id)
        if app_obj.has_combo:
            release_ids.append(AppReleaseInfo.objects.filter(app_id=app_obj.has_combo,is_master=True).first().release_id)

        download_token = dtoken.make_token(release_ids)
        app_serializer = AppsSerializer(app_obj,context={"release_id":release_id,"download_token":download_token})
        res.data = app_serializer.data
        res.data["download_token"]=download_token
        return Response(res.dict)


