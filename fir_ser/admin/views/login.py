#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2021/4/11

import logging

from django.contrib import auth
from rest_framework.views import APIView

from admin.utils.utils import ApiResponse
from api.utils.auth import ExpiringTokenAuthentication
from api.utils.serializer import UserInfoSerializer
from api.utils.storage.caches import login_auth_failed
from api.utils.throttle import VisitRegister1Throttle, VisitRegister2Throttle
from api.utils.utils import get_captcha, valid_captcha, set_user_token
from fir_ser.settings import LOGIN

logger = logging.getLogger(__name__)


class LoginView(APIView):
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]

    def post(self, request):
        receive = request.data
        username = receive.get("username", None)
        code = 1000
        msg = 'success'
        data = None
        if LOGIN.get("captcha"):
            is_valid = valid_captcha(receive.get("captcha_key", None), receive.get("authcode", None), username)
        else:
            is_valid = True
        if is_valid:
            if login_auth_failed("get", username):
                password = receive.get("password")
                user = auth.authenticate(username=username, password=password)
                logger.info(f"username:{username}  password:{password}")
                if user:
                    if user.is_active:
                        if user.role == 3:
                            login_auth_failed("del", username)
                            key, user_info = set_user_token(user, request)
                            data = {
                                "username": user_info.username,
                                "token": key
                            }
                        else:
                            msg = "权限拒绝"
                            code = 1003
                    else:
                        msg = "用户被禁用"
                        code = 1005
                else:
                    login_auth_failed("set", username)
                    msg = "密码或者账户有误"
                    code = 1002
            else:
                code = 1006
                logger.error(f"username:{username} failed too try , locked")
                msg = "用户登录失败次数过多，已被锁定，请1小时之后再次尝试"
        else:
            code = 1001
            msg = "验证码有误"

        return ApiResponse(code=code, msg=msg, data=data)

    def get(self, request):
        data = {}
        if LOGIN.get("captcha"):
            data = get_captcha()
        return ApiResponse(data=data)


class LoginUserView(APIView):
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        serializer = UserInfoSerializer(request.user, )
        return ApiResponse(data=serializer.data)
