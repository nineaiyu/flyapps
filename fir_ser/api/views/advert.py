#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 10月
# author: liuyu
# date: 2021/10/14
from rest_framework.views import APIView

from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication, UserAdInfoPermission
from rest_framework.response import Response
from api.models import UserAdDisplayInfo
from api.utils.serializer import UserAdInfoSerializer
from rest_framework.pagination import PageNumberPagination
import logging

from api.utils.storage.caches import reset_short_response_cache
from api.utils.storage.storage import Storage

logger = logging.getLogger(__name__)


class PageNumber(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class UserAdInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [UserAdInfoPermission, ]

    def get(self, request):

        res = BaseResponse()

        ad_name = request.query_params.get("search_key", None)
        ad_info_list = UserAdDisplayInfo.objects.filter(user_id=request.user)
        if ad_name:
            ad_info_list = ad_info_list.filter(ad_name=ad_name)

        page_obj = PageNumber()
        page_paginate_obj = page_obj.paginate_queryset(queryset=ad_info_list.order_by("-created_time"),
                                                       request=request,
                                                       view=self)
        page_serializer_obj = UserAdInfoSerializer(page_paginate_obj, many=True, )
        res.data = page_serializer_obj.data
        res.count = ad_info_list.count()
        return Response(res.dict)

    def put(self, request):
        data = request.data
        ad_pk = data.get("id", None)
        if ad_pk:
            ad_info_obj = UserAdDisplayInfo.objects.filter(user_id=request.user, pk=ad_pk).first()
            res = BaseResponse()
            update_fields = []
            logger.info(f"user {request.user}  ad_info {ad_info_obj} update input data {data}")
            f_fields = ["ad_name", "ad_uri", "description", "is_enable"]
            for f_f in f_fields:
                f_v = data.get(f_f)
                if f_v is not None and f_v != '':
                    setattr(ad_info_obj, f_f, f_v)
                    update_fields.append(f_f)
                else:
                    if f_f == 'description':
                        continue
                    else:
                        res.code = 1001
                        res.msg = '参数有误'
                        return Response(res.dict)
            try:
                weight = int(data.get("weight", ad_info_obj.weight))
                if 0 <= weight <= 100:
                    ad_info_obj.weight = weight
                    update_fields.append("weight")
            except Exception as e:
                logger.error(
                    f"ad_info {ad_info_obj} weight {data.get('weight', ad_info_obj.weight)} get failed Exception:{e}")

            try:
                ad_info_obj.save(update_fields=update_fields)
                logger.info(
                    f"user {request.user} ad_info {ad_info_obj} update now data {ad_info_obj.__dict__}")
                res.data = UserAdInfoSerializer(ad_info_obj).data
                reset_short_response_cache(request.user)
                return Response(res.dict)
            except Exception as e:
                logger.error(
                    f"user {request.user} ad_info {ad_info_obj} update error data {data} Exception {e}")
                res.code = 1001
                return Response(res.dict)

        return self.get(request)

    def post(self, request):
        data = request.data
        data_info = {}
        res = BaseResponse()
        f_fields = ["ad_name", "ad_uri", "description", "is_enable"]
        for f_f in f_fields:
            f_v = data.get(f_f)
            if f_v is not None and f_v != '':
                data_info[f_f] = f_v
            else:
                if f_f == 'description':
                    continue
                else:
                    res.code = 1001
                    res.msg = "参数有误，添加失败"
                    return Response(res.dict)

        try:
            weight = int(data.get("weight", 1))
            if 0 <= weight <= 100:
                data_info["weight"] = weight
        except:
            pass

        try:
            logger.error(f"user {request.user} add new ad {data.get('pk', '')} data {data_info}")
            ad_info_obj = UserAdDisplayInfo.objects.create(user_id=request.user, **data_info)
            res.data = UserAdInfoSerializer(ad_info_obj).data
            return Response(res.dict)
        except Exception as e:
            logger.error(f"user {request.user} add new ad {data_info} failed Exception:{e}")
            res.code = 1005
            res.msg = "广告名称已经存在，或者字段缺少"
            return Response(res.dict)

    def delete(self, request):
        ad_pk = request.query_params.get("pk", None)
        if ad_pk:
            ad_info_obj = UserAdDisplayInfo.objects.filter(user_id=request.user, pk=ad_pk).first()
            if ad_info_obj:
                storage = Storage(request.user)
                storage.delete_file(ad_info_obj.ad_pic)
                reset_short_response_cache(request.user)
                ad_info_obj.delete()

        return self.get(request)
