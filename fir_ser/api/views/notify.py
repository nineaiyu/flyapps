#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: notify
# author: liuyu
# data: 2022/3/25


import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import NotifyReceiver, ThirdWeChatUserInfo, NotifyConfig, UserInfo
from api.utils.modelutils import PageNumber
from api.utils.response import BaseResponse
from api.utils.serializer import NotifyReceiverSerializer, NotifyConfigSerializer
from common.base.baseutils import get_choices_dict, get_choices_name_from_key
from common.core.auth import ExpiringTokenAuthentication

logger = logging.getLogger(__name__)


class NotifyConfigView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        config_pk = request.query_params.get('pk')

        obj_lists = NotifyConfig.objects.filter(user_id=request.user).order_by('message_type').order_by("-create_time")
        if config_pk:
            obj_lists = obj_lists.filter(pk=config_pk).first()
            info = NotifyConfigSerializer(obj_lists)
            res.data = info.data
            return Response(res.dict)

        info = NotifyConfigSerializer(obj_lists.all(), many=True).data
        res.count = obj_lists.count()
        message_type_choices = get_choices_dict(NotifyConfig.message_type_choices)
        for message_info in message_type_choices:
            message_info['data'] = []
            for notify_config_info in info:
                if notify_config_info['message_type'] == message_info['id']:
                    message_info['data'].append(notify_config_info)
            if len(message_info['data']) == 0:
                data_info = NotifyConfigSerializer(NotifyConfig.objects.filter(pk=-1).first()).data
                data_info['config_name'] = message_info['name']
                data_info['message_type'] = message_info['id']
                data_info['m_type'] = message_info['id']
                data_info['id'] = -1
                message_info['data'].append(data_info)
        res.message_type_choices = message_type_choices
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        act = data.get('act', '')
        if act and act != 'get':
            threshold = data.get('threshold', {})
            if threshold:
                notify_available_downloads = threshold.get('notify_available_downloads')
                notify_available_signs = threshold.get('notify_available_signs')

                if notify_available_downloads is not None:
                    request.user.notify_available_downloads = notify_available_downloads
                if notify_available_signs is not None:
                    request.user.notify_available_signs = notify_available_signs
                if notify_available_downloads is not None or notify_available_signs is not None:
                    request.user.save(update_fields=['notify_available_downloads', 'notify_available_signs'])

        res.data = UserInfo.objects.filter(pk=request.user.pk).values('notify_available_downloads',
                                                                      'notify_available_signs').first()
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        config_pk = data.get('config')
        receiver_ids = data.get('receiver')
        enable_email = data.get('enable_email')
        enable_weixin = data.get('enable_weixin')
        m_type = data.get('m_type')
        if config_pk and config_pk == -1 and m_type is not None:
            notify_config_obj = NotifyConfig.objects.filter(user_id=request.user, message_type=int(m_type)).filter()
            if not notify_config_obj:
                notify_config_obj = NotifyConfig.objects.create(user_id=request.user, message_type=int(m_type),
                                                                config_name=get_choices_name_from_key(
                                                                    NotifyConfig.message_type_choices, int(m_type)))
        else:
            notify_config_obj = NotifyConfig.objects.filter(user_id=request.user, pk=config_pk).first()
        if notify_config_obj:
            if isinstance(receiver_ids, list):
                notify_config_obj.sender.set(
                    NotifyReceiver.objects.filter(user_id=request.user, pk__in=receiver_ids).all())
            if enable_weixin is not None:
                notify_config_obj.enable_weixin = enable_weixin
            if enable_email is not None:
                notify_config_obj.enable_email = enable_email
            if enable_weixin is not None or enable_email is not None:
                notify_config_obj.save(update_fields=['enable_email', 'enable_weixin'])

        return Response(res.dict)


class NotifyReceiverView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        config_pk = request.query_params.get('config')
        message_type = request.query_params.get('message_type')

        obj_lists = NotifyReceiver.objects.filter(user_id=request.user)

        config_obj_lists = NotifyConfig.objects.filter(user_id=request.user)
        if config_pk and config_pk != '-1':
            res.senders = config_obj_lists.values('sender').filter(pk=config_pk).all()
            config_obj = config_obj_lists.filter(pk=config_pk).first()
            if config_obj:
                res.config = {'config_name': config_obj.config_name,
                              'id': config_obj.pk, 'm_type': config_obj.message_type,
                              'message_type': config_obj.get_message_type_display()}
        if config_pk and config_pk == '-1' and message_type is not None:
            res.senders = config_obj_lists.values('sender').filter(pk=config_pk).all()
            config_name = get_choices_name_from_key(NotifyConfig.message_type_choices, int(message_type))
            res.config = {'config_name': config_name, 'id': -1, 'message_type': config_name,
                          'm_type': message_type}

        page_obj = PageNumber()
        obj_info_serializer = page_obj.paginate_queryset(queryset=obj_lists.order_by("-create_time"),
                                                         request=request,
                                                         view=self)
        info = NotifyReceiverSerializer(obj_info_serializer, many=True, )
        res.data = info.data
        res.count = obj_lists.count()
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        receiver_name = data.get('receiver_name')
        description = data.get('description')
        wxopenid = data.get('wxopenid')
        email = data.get('email')
        if receiver_name:
            data_info = {
                'receiver_name': receiver_name,
                'description': description,
            }
            wx_obj = None
            if wxopenid:
                wx_obj = ThirdWeChatUserInfo.objects.filter(user_id=request.user, openid=wxopenid).first()
                if wx_obj:
                    data_info['weixin'] = wx_obj
            if email:
                data_info['email'] = email
            try:
                NotifyReceiver.objects.create(user_id=request.user, **data_info)
                if wx_obj:
                    wx_obj.enable_notify = True
                    wx_obj.save(update_fields=['enable_notify'])
            except Exception as e:
                logger.error(f"{request.user} notify receiver add failed . data:{data} Exception:{e}")
                res.code = 1001
                res.msg = '数据有误或者已经存在该接收人信息'
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        pk = request.query_params.get('id')
        if pk:
            NotifyReceiver.objects.filter(user_id=request.user, pk=pk).delete()
        return Response(res.dict)
