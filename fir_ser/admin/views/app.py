#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: liuyu
# date: 2021/4/11

import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from admin.utils import AppsPageNumber
from api.base_views import app_delete
from api.models import AppReleaseInfo, Apps
from api.utils.TokenManager import verify_token
from api.utils.auth import AdminTokenAuthentication
from api.utils.response import BaseResponse
from api.utils.serializer import AdminAppsSerializer, AdminAppReleaseSerializer
from api.utils.storage.caches import del_cache_response_by_short, get_download_url_by_cache
from common.base.baseutils import get_dict_from_filter_fields

logger = logging.getLogger(__name__)


class AppInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "type", "name", "short", "bundle_id", "domain_name", "user_id", "status"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-updated_time")
        page_obj = AppsPageNumber()
        obj_list = Apps.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminAppsSerializer(page_serializer, many=True)
        res.data = serializer.data
        res.total = obj_list.count()
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        app_obj = Apps.objects.filter(pk=pk).first()
        if app_obj:
            data['pk'] = pk
            serializer_obj = AdminAppsSerializer(app_obj, data=data, partial=True)
            if serializer_obj.is_valid():
                serializer_obj.save()
                res.data = serializer_obj.data
                del_cache_response_by_short(app_obj.app_id)
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        if not pk:
            res.code = 1003
            res.msg = "参数错误"
        else:
            res = app_delete(Apps.objects.filter(pk=pk).first())
        return Response(res.dict)


class AppReleaseInfoView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        filter_fields = ["id", "release_id", "app_id"]
        filter_data = get_dict_from_filter_fields(filter_fields, request.query_params)
        sort = request.query_params.get("sort", "-created_time")
        if not filter_data.get('app_id', None):
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        page_obj = AppsPageNumber()
        obj_list = AppReleaseInfo.objects.filter(**filter_data).order_by(sort)
        page_serializer = page_obj.paginate_queryset(queryset=obj_list, request=request,
                                                     view=self)
        serializer = AdminAppReleaseSerializer(page_serializer, many=True)
        res.data = serializer.data
        res.total = obj_list.count()
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        pk = data.get("id", None)
        app_id = data.get("app_id", None)
        if not pk or not app_id:
            res.code = 1003
            res.msg = "参数错误"
            return Response(res.dict)
        app_obj = AppReleaseInfo.objects.filter(pk=pk, app_id=app_id).first()
        if app_obj:
            data['pk'] = pk
            serializer_obj = AdminAppReleaseSerializer(app_obj, data=data, partial=True)
            if serializer_obj.is_valid():
                serializer_obj.save()
                res.data = serializer_obj.data
                del_cache_response_by_short(app_obj.app_id.app_id)
                return Response(res.dict)
        res.code = 1004
        res.msg = "数据校验失败"
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        downtoken = data.get("token", None)
        app_id = data.get("app_id", None)
        release_id = data.get("release_id", None)

        if not downtoken or not app_id or not release_id:
            res.code = 1004
            res.msg = "参数丢失"
            return Response(res.dict)

        if verify_token(downtoken, release_id):
            app_obj = Apps.objects.filter(pk=app_id).values("pk", 'user_id', 'type').first()
            release_obj = AppReleaseInfo.objects.filter(app_id=app_id, release_id=release_id).count()
            if app_obj and release_obj:
                if app_obj.get("type") == 0:
                    app_type = '.apk'
                else:
                    app_type = '.ipa'
                download_url, extra_url = get_download_url_by_cache(app_obj, release_id + app_type, 600)
                res.data = {"download_url": download_url, "extra_url": extra_url}
                return Response(res.dict)
        else:
            res.code = 1004
            res.msg = "token校验失败"
            return Response(res.dict)
        res.code = 1006
        res.msg = "该应用不存在"
        return Response(res.dict)
