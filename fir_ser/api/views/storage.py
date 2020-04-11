#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/4

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from django.db.models import Sum
import os
from fir_ser import settings
from api.utils.app.randomstrings import make_from_user_uuid
from api.utils.storage.storage import Storage
from api.utils.storage.caches import del_cache_response_by_short,get_app_today_download_times
from api.models import Apps, AppReleaseInfo,AppStorage
from api.utils.serializer import StorageSerializer





class StorageView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    def get(self, request):
        res = BaseResponse()
        # [1,2] 表示七牛存储和阿里云存储
        storage_obj = AppStorage.objects.filter(user_id=request.user,storage_type__in=[1,2])
        if storage_obj:
            storage_serializer = StorageSerializer(storage_obj,many=True)
            storage_data_lists = storage_serializer.data
            storage_lists={}
            for storage_data in storage_data_lists:
                storage_type = storage_data.get("storage_type")
                if not storage_lists.get(storage_type):
                    storage_lists[storage_type]=[]
                storage_lists[storage_type].append(storage_data)
            res.data=storage_lists

        use_storage_obj = request.user.storage
        if use_storage_obj:
            res.storage=use_storage_obj.id
        else:
            res.storage = None

        return Response(res.dict)
