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
from api.models import AppStorage, UserInfo
from api.utils.utils import upload_oss_default_head_img
from api.utils.serializer import StorageSerializer
import logging

logger = logging.getLogger(__file__)


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
            res.storage = -1  # 默认存储

        res.storage_list = []
        storage_org_list = list(AppStorage.storage_choices)
        for storage_t in storage_org_list:
            if storage_t[0] in [0, 3]: continue
            res.storage_list.append({'id': storage_t[0], 'name': storage_t[1]})

        admin_storage = UserInfo.objects.filter(is_superuser=True).order_by('pk').first()
        res.is_admin_storage = False
        if admin_storage and admin_storage.uid == request.user.uid:
            res.is_admin_storage = True
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        logger.info("user %s add new storage data:%s" % (request.user, data))
        try:
            data['additionalparameters'] = json.dumps(data.get('additionalparameter', ''))
        except Exception as e:
            logger.error("user:%s additionalparameters %s dumps failed Exception:%s" % (
                request.user, data.get('additionalparameter', ''), e))

        serializer = StorageSerializer(data=data, context={'user_obj': request.user})
        if serializer.is_valid():
            storage_obj = serializer.save()
            if storage_obj:
                if upload_oss_default_head_img(request.user, storage_obj):
                    res.msg = serializer.validated_data
                    logger.info("user %s add new storage success" % (request.user))
                else:
                    storage_obj.delete()
                    logger.error("user %s add new storage failed" % (request.user))
                    res.msg = "文件上传校验失败，请检查参数是否正确"
                    res.code = 1005
            else:
                logger.info("user %s add new storage failed" % (request.user))
                res.msg = serializer.errors
                res.code = 1005
        else:
            logger.info("user %s add new storage failed" % (request.user))
            res.msg = serializer.errors
            res.code = 1005
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        logger.info("user %s update storage data:%s" % (request.user, data))

        use_storage_id = data.get("use_storage_id", None)
        if use_storage_id:
            try:
                if use_storage_id == -1:
                    UserInfo.objects.filter(pk=request.user.pk).update(storage=None)
                else:
                    UserInfo.objects.filter(pk=request.user.pk).update(storage_id=use_storage_id)
                del_cache_storage(request.user)
            except Exception as e:
                logger.error("update user %s storage failed Exception:%s" % (request.user, e))
                res.code = 1006
                res.msg = '修改失败'
            return Response(res.dict)

        storage_id = data.get("id", None)
        if storage_id:
            if storage_id == request.user.storage.id:
                res.msg = '存储正在使用中，无法修改'
                res.code = 1007
                return Response(res.dict)
            try:
                data['additionalparameters'] = json.dumps(data.get('additionalparameter', ''))
            except Exception as e:
                del data['additionalparameters']
                logger.error("user:%s additionalparameters %s dumps failed Exception:%s" % (
                    request.user, data.get('additionalparameter', ''), e))

            storage_obj = AppStorage.objects.filter(id=storage_id, user_id=request.user).first()
            storage_obj_bak = AppStorage.objects.filter(id=storage_id, user_id=request.user).first()
            serializer = StorageSerializer(instance=storage_obj, data=data, context={'user_obj': request.user},
                                           partial=True)
            if serializer.is_valid():
                new_storage_obj = serializer.save()
                if new_storage_obj:
                    if upload_oss_default_head_img(request.user, new_storage_obj):
                        res.msg = serializer.validated_data
                        logger.info("user %s update storage success" % (request.user))
                    else:
                        storage_obj_bak.save()
                        logger.error("user %s update storage failed" % (request.user))
                        res.msg = "文件上传校验失败，请检查参数是否正确"
                        res.code = 1005
                else:
                    logger.info("user %s update storage failed" % (request.user))
                    res.msg = serializer.errors
                    res.code = 1005
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
            try:
                AppStorage.objects.filter(user_id=request.user, id=storage_id).delete()
                logger.error("user %s delete storage id:%s success" % (request.user, storage_id))
            except Exception as e:
                logger.error("user %s delete storage id:%s failed Exception:%s" % (request.user, storage_id, e))
        else:
            res.code = 1004
            res.msg = '该存储不存在'
        return Response(res.dict)
