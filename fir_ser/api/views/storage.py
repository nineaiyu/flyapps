#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/4

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
import json
from api.utils.storage.caches import del_cache_storage
from api.models import  AppStorage,UserInfo
from api.utils.serializer import StorageSerializer


class StorageView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        # [1,2] 表示七牛存储和阿里云存储
        storage_obj = AppStorage.objects.filter(user_id=request.user, storage_type__in=[1, 2])
        if storage_obj:
            storage_serializer = StorageSerializer(storage_obj, many=True)
            storage_data_lists = storage_serializer.data
            storage_lists = {}
            for storage_data in storage_data_lists:
                storage_type = storage_data.get("storage_type")
                if not storage_lists.get(storage_type):
                    storage_lists[storage_type] = []
                storage_lists[storage_type].append(storage_data)
            res.data = storage_data_lists

        use_storage_obj = request.user.storage
        if use_storage_obj:
            res.storage = use_storage_obj.id
        else:
            res.storage = -1 # 默认存储

        res.storage_list = []
        storage_org_list = list(AppStorage.storage_choices)
        for storage_t in storage_org_list:
            if storage_t[0] in [0, 3]: continue
            res.storage_list.append({'id': storage_t[0], 'name': storage_t[1]})

        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        try:
            data['additionalparameters'] = json.dumps(data.get('additionalparameter', ''))
        except Exception as e:
            print(e)

        serializer = StorageSerializer(data=data, context={'user_obj': request.user})
        if serializer.is_valid():
            serializer.save()
            res.msg = serializer.validated_data

        else:
            res.msg = serializer.errors
            res.code = 1005
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data

        use_storage_id=data.get("use_storage_id",None)
        if use_storage_id:
            try:
                if use_storage_id == -1:
                    UserInfo.objects.filter(pk=request.user.pk).update(storage=None)
                else:
                    UserInfo.objects.filter(pk=request.user.pk).update(storage_id=use_storage_id)
                del_cache_storage(request.user)
            except Exception as e:
                print(e)
                res.code=1006
                res.msg='修改失败'
            return Response(res.dict)

        try:
            data['additionalparameters'] = json.dumps(data.get('additionalparameter', ''))
        except Exception as e:
            print(e)

        storage_id = data.get("id", None)
        if storage_id:
            storage_obj = AppStorage.objects.filter(id=storage_id, user_id=request.user).first()
            serializer = StorageSerializer(instance=storage_obj, data=data, context={'user_obj': request.user},
                                           partial=True)
            if serializer.is_valid():
                serializer.save()
                res.msg = serializer.validated_data
            else:
                res.msg = serializer.errors
                res.code = 1005
        else:
            res.msg = '该存储不存在'
            res.code = 1007
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        storage_id = request.query_params.get("id", None)
        if storage_id:
            AppStorage.objects.filter(user_id=request.user, id=storage_id).delete()
        else:
            res.code = 1004
            res.msg = '该存储不存在'
        return Response(res.dict)
