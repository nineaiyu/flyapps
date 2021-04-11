#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2021/4/11

from django.contrib import auth
from api.models import Token, UserInfo
from rest_framework.response import Response
from api.utils.auth import ExpiringTokenAuthentication
from api.utils.serializer import UserInfoSerializer
from django.core.cache import cache
from rest_framework.views import APIView
import binascii
import os, datetime
from api.utils.utils import get_captcha, valid_captcha
from api.utils.response import BaseResponse
from fir_ser.settings import CACHE_KEY_TEMPLATE, LOGIN
from api.utils.storage.caches import login_auth_failed
import logging
from api.utils.throttle import VisitRegister1Throttle, VisitRegister2Throttle

logger = logging.getLogger(__name__)


class LoginView(APIView):
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]

    def generate_key(self):
        return binascii.hexlify(os.urandom(32)).decode()

    def post(self, request):
        response = BaseResponse()
        receive = request.data
        username = receive.get("username", None)
        if LOGIN.get("captcha"):
            is_valid = valid_captcha(receive.get("cptch_key", None), receive.get("authcode", None), username)
        else:
            is_valid = True
        if is_valid:
            if login_auth_failed("get", username):
                password = receive.get("password")
                user = auth.authenticate(username=username, password=password)
                logger.info("username:%s  password:%s" % (username, password))
                if user:
                    if user.is_active:
                        if user.role == 3:
                            login_auth_failed("del", username)
                            # update the token
                            key = self.generate_key()
                            now = datetime.datetime.now()
                            user_info = UserInfo.objects.get(pk=user.pk)
                            auth_key = "_".join([CACHE_KEY_TEMPLATE.get('user_auth_token_key'), key])
                            cache.set(auth_key, {'uid': user_info.uid, 'username': user_info.username}, 3600 * 24 * 7)
                            Token.objects.create(user=user, **{"access_token": key, "created": now})
                            response.data = {
                                "username": user_info.username,
                                "token": key
                            }
                        else:
                            response.msg = "权限拒绝"
                            response.code = 1003
                    else:
                        response.msg = "用户被禁用"
                        response.code = 1005
                else:
                    login_auth_failed("set", username)
                    response.msg = "密码或者账户有误"
                    response.code = 1002
            else:
                response.code = 1006
                logger.error("username:%s failed too try , locked" % (username,))
                response.msg = "用户登录失败次数过多，已被锁定，请1小时之后再次尝试"
        else:
            response.code = 1001
            response.msg = "验证码有误"

        return Response(response.dict)

    def get(self, request):
        response = BaseResponse()
        response.data = {}
        if LOGIN.get("captcha"):
            response.data = get_captcha()
        return Response(response.dict)


class LoginUserView(APIView):
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        response = BaseResponse()
        serializer = UserInfoSerializer(request.user, )
        data = serializer.data
        response.data = data
        return Response(response.dict)
