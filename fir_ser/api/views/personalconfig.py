#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: getip
# author: liuyu
# date: 2022/3/28

import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import UserPersonalConfig
from api.utils.response import BaseResponse
from api.utils.serializer import PersonalConfigSerializer
from common.core.auth import ExpiringTokenAuthentication, SuperSignPermission
from common.core.sysconfig import UserConfig, Config
from common.utils.caches import del_cache_storage

logger = logging.getLogger(__name__)


def get_personal_config(request):
    config_type = request.query_params.get("config_type", None)
    if config_type == 'super_sign':
        personal_config = Config.DEVELOPER_STATUS_CONFIG
    elif config_type == 'preview_route':
        personal_config = ['PREVIEW_ROUTE_HASH']
    elif config_type == 'short_download_uri':
        personal_config = ['DOWNLOAD_DEPLOYMENT_URL']
    else:
        personal_config = []
    return personal_config


class PersonalConfigView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()

        config_key = request.query_params.get("config_key", None)
        personal_config = get_personal_config(request)
        personal_config_queryset = UserPersonalConfig.objects.filter(user_id=request.user,
                                                                     key__in=personal_config)
        if personal_config_queryset.count() != len(personal_config):
            for key in personal_config:
                UserConfig(request.user).set_default_value(key)
        if config_key:
            personal_config_queryset = personal_config_queryset.filter(key=config_key)

        personal_config_serializer = PersonalConfigSerializer(personal_config_queryset, many=True)
        res.data = personal_config_serializer.data
        res.count = personal_config_queryset.count()

        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        config_key = request.data.get("config_key", None)
        config_value = request.data.get("config_value", None)
        if config_key is not None and config_value is not None and config_key in get_personal_config(request):
            UserPersonalConfig.objects.filter(user_id=request.user, key=config_key).update(value=config_value)
            UserConfig(request.user).invalid_config_cache(config_key)
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        for key in get_personal_config(request):
            UserConfig(request.user).del_value(key)
            Config.invalid_config_cache(f'{key}_DES')
            if key == 'preview_route':
                # 清理缓存
                del_cache_storage(request.user)
        return Response(res.dict)
