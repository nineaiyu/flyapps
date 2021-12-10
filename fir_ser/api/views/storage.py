#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/4

import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from api.base_views import storage_change, app_delete
from api.models import AppStorage, UserInfo, Apps
from api.utils.app.apputils import clean_history_apps
from api.utils.auth import ExpiringTokenAuthentication, StoragePermission
from api.utils.response import BaseResponse
from api.utils.serializer import StorageSerializer
from api.utils.storage.caches import MigrateStorageState
from api.utils.utils import upload_oss_default_head_img, get_choices_dict

logger = logging.getLogger(__name__)


class StorageView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [StoragePermission, ]

    def get(self, request):
        res = BaseResponse()
        res.storage_list = []
        storage_org_list = list(AppStorage.storage_choices)
        for storage_t in storage_org_list:
            if storage_t[0] not in [0, 3]:
                res.storage_list.append({'id': storage_t[0], 'name': storage_t[1]})

        act = request.query_params.get("act", None)
        if act == 'storage_type':
            res.download_auth_type_choices = get_choices_dict(AppStorage.download_auth_type_choices)
            return Response(res.dict)

        # [1,2] 表示七牛存储和阿里云存储
        storage_obj = AppStorage.objects.filter(user_id=request.user, storage_type__in=[1, 2])
        if storage_obj:
            storage_serializer = StorageSerializer(storage_obj, many=True)
            storage_data_lists = storage_serializer.data
            storage_lists = {}
            for storage_data in storage_data_lists:
                storage_type = storage_data.get("storage_type")
                storage_data['secret_key'] = ''
                if not storage_lists.get(storage_type):
                    storage_lists[storage_type] = []
                storage_lists[storage_type].append(storage_data)
            res.data = storage_data_lists

        use_storage_obj = request.user.storage
        if use_storage_obj:
            res.storage = use_storage_obj.id
        else:
            res.storage = -1  # 默认存储

        admin_storage = UserInfo.objects.filter(is_superuser=True).order_by('pk').first()
        res.is_admin_storage = False
        if admin_storage and admin_storage.uid == request.user.uid:
            res.is_admin_storage = True
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        logger.info(f"user {request.user} add new storage data:{data}")
        serializer = StorageSerializer(data=data, context={'user_obj': request.user})
        if serializer.is_valid():
            storage_obj = serializer.save()
            if storage_obj:
                if upload_oss_default_head_img(request.user, storage_obj):
                    res.msg = serializer.validated_data
                    logger.info(f"user {request.user} add new storage success")
                else:
                    storage_obj.delete()
                    logger.error(f"user {request.user} add new storage failed")
                    res.msg = "文件上传校验失败，请检查参数是否正确"
                    res.code = 1005
            else:
                logger.info(f"user {request.user} add new storage failed")
                res.msg = serializer.errors
                res.code = 1005
        else:
            logger.info(f"user {request.user} add new storage failed")
            res.msg = serializer.errors
            res.code = 1005
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        logger.info(f"user {request.user} update storage data:{data}")
        use_storage_id = data.get("use_storage_id", None)
        force = data.get("force", None)
        if use_storage_id:
            with MigrateStorageState(request.user.uid) as state:
                if state:
                    if not storage_change(use_storage_id, request.user, force):
                        res.code = 1006
                        res.msg = '修改失败'
                else:
                    res.code = 1007
                    res.msg = "数据迁移中,请耐心等待"

            return Response(res.dict)

        storage_id = data.get("id", None)
        if storage_id:
            if request.user.storage and storage_id == request.user.storage.id:
                res.msg = '存储正在使用中，无法修改'
                res.code = 1007
                return Response(res.dict)
            storage_obj = AppStorage.objects.filter(id=storage_id, user_id=request.user).first()
            storage_obj_bak = AppStorage.objects.filter(id=storage_id, user_id=request.user).first()
            serializer = StorageSerializer(instance=storage_obj, data=data, context={'user_obj': request.user},
                                           partial=True)
            if serializer.is_valid():
                new_storage_obj = serializer.save()
                if new_storage_obj:
                    if upload_oss_default_head_img(request.user, new_storage_obj):
                        res.msg = serializer.validated_data
                        logger.info(f"user {request.user} update storage success")
                    else:
                        storage_obj_bak.save()
                        logger.error(f"user {request.user} update storage failed")
                        res.msg = "文件上传校验失败，请检查参数是否正确"
                        res.code = 1005
                else:
                    logger.info(f"user {request.user} update storage failed")
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
                logger.error(f"user {request.user} delete storage id:{storage_id} success")
            except Exception as e:
                logger.error(f"user {request.user} delete storage id:{storage_id} failed Exception:{e}")
        else:
            res.code = 1004
            res.msg = '该存储不存在'
        return Response(res.dict)


class CleanStorageView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [StoragePermission, ]

    def post(self, request):
        res = BaseResponse()
        data = request.data
        logger.info(f"user {request.user} clean storage data:{data}")
        act = data.get('act', '')
        if act in ['history', 'all']:
            if request.user.check_password(data.get('confirm_pwd', '')):
                app_obj_lists = Apps.objects.filter(user_id=request.user).all()
                for app_obj in app_obj_lists:
                    if act == 'all':
                        res = app_delete(app_obj)
                    elif act == 'history':
                        clean_history_apps(app_obj, request.user, 1)
            else:
                res.code = 1007
                res.msg = "密码有误，请检查"
        else:
            res.code = 1007
            res.msg = "参数不合法，清理失败"
        return Response(res.dict)
