from django.utils.translation import ugettext_lazy as _
from django.core.cache import cache

import datetime
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from rest_framework.exceptions import AuthenticationFailed
from api.models import Token, UserInfo
import pytz
import base64

class ExpiringTokenAuthentication(BaseAuthentication):
    def authenticate1(self, request):
        '''
        1 对token设置14天有效时间
        2 缓存存储

        :param request:
        :return:
        '''
        if request.method == "OPTIONS":
            return None
        token = request.META.get("HTTP_AUTHORIZATION")
        # 1 校验是否存在token字符串
        # 1.1 缓存校验
        user = cache.get(token)
        if user:
            print("缓存校验成功")
            return user, token
        # 1.2 数据库校验
        token_obj = Token.objects.filter(key=token).first()
        if not token_obj:
            raise AuthenticationFailed("认证失败!")
        # 2 校验是否在有效期内
        now = datetime.datetime.now()  # 2018-1-12- 0 0 0
        delta = now - token_obj.created
        state = delta < datetime.timedelta(weeks=2)
        if state:
            # 校验成功，写入缓存中
            delta = datetime.timedelta(weeks=2) - delta
            cache.set(token_obj.key, token_obj.user, min(delta.total_seconds(), 3600 * 24 * 7))
            print("数据库校验成功")
            return token_obj.user, token_obj.key
        else:
            raise AuthenticationFailed("认证超时！")

    def authenticate(self, request):
        if request.method == "OPTIONS":
            return None
        request_token = request.META.get("HTTP_AUTHORIZATION", request.query_params.get("token", None))
        try:
            format_token = base64.b64decode(request_token).decode()
            auth_token = format_token.split(":")[0]
            user_name = format_token.split(":")[1]

        except Exception:
            raise AuthenticationFailed({"code": 1001, "error": "token不合法"})

        if not auth_token:
            raise AuthenticationFailed({"code": 1001, "error": "缺少token"})
        token_obj = Token.objects.filter(access_token=auth_token).first()
        if not token_obj:
            raise AuthenticationFailed({"code": 1001, "error": "无效的token"})
        if user_name != token_obj.user.username:
            raise AuthenticationFailed({"code": 1001, "error": "token校验失败"})
        return token_obj.user, token_obj
