#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 9月
# author: NinEveN
# date: 2020/9/24
from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models import UserInfo
from rest_framework.permissions import BasePermission
from fir_ser.settings import CACHE_KEY_TEMPLATE
from django.http.cookie import parse_cookie
import base64


def get_cookie_token(request):
    cookies = request.META.get('HTTP_COOKIE')
    if cookies:
        cookie_dict = parse_cookie(cookies)
        return cookie_dict.get('auth_token')


def get_user_from_api_token(request):
    if request.method == "OPTIONS":
        return None
    api_token = request.META.get("HTTP_APIAUTHORIZATION", request.query_params.get("api_token", None))
    user_obj = UserInfo.objects.filter(api_token=api_token).first()
    if not user_obj:
        raise AuthenticationFailed({"code": 1001, "error": "无效的api_token"})
    if user_obj.is_active:
        return user_obj, api_token
    else:
        raise AuthenticationFailed({"code": 1001, "error": "用户被禁用"})


def get_user_from_request_auth(request):
    if request.method == "OPTIONS":
        return None
    request_token = request.META.get("HTTP_AUTHORIZATION",
                                     request.META.get("HTTP_X_TOKEN",
                                                      request.query_params.get("token", get_cookie_token(request))))
    if request_token:
        try:
            format_token = base64.b64decode(request_token).decode()
            auth_token = format_token.split(":")[0]
            user_name = format_token.split(":")[1]
        except Exception:
            raise AuthenticationFailed({"code": 1001, "error": "token不合法"})

        if not auth_token:
            raise AuthenticationFailed({"code": 1001, "error": "缺少token"})

        auth_key = "_".join([CACHE_KEY_TEMPLATE.get('user_auth_token_key'), auth_token])

        cacheuserinfo = cache.get(auth_key)
        if not cacheuserinfo:
            raise AuthenticationFailed({"code": 1001, "error": "无效的token"})
        if user_name != cacheuserinfo.get('username', None):
            raise AuthenticationFailed({"code": 1001, "error": "token校验失败"})

        user_obj = UserInfo.objects.filter(uid=cacheuserinfo.get('uid', None),
                                           username=cacheuserinfo.get("username")).first()
        if not user_obj:
            raise AuthenticationFailed({"code": 1001, "error": "无效的token"})
        if user_obj.is_active:
            cache.set(auth_key, cacheuserinfo, 3600 * 24 * 7)
            return user_obj, auth_token
        else:
            raise AuthenticationFailed({"code": 1001, "error": "用户被禁用"})
    else:
        raise AuthenticationFailed({"code": 1001, "error": "无效的认证"})


class ExpiringTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        return get_user_from_request_auth(request)


class AdminTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        result = get_user_from_request_auth(request)
        if result:
            user_obj, token = result
            if user_obj and user_obj.role == 3:
                return result
            else:
                raise AuthenticationFailed({"code": 1001, "error": "无效的认证"})
        return result


class ApiTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        return get_user_from_api_token(request)


class StoragePermission(BasePermission):
    message = "权限不足"

    def has_permission(self, request, view):
        results = get_user_from_request_auth(request)
        if results and results[0]:
            return results[0].storage_active
        return True


class SuperSignPermission(BasePermission):
    message = "权限不足"

    def has_permission(self, request, view):
        results = get_user_from_request_auth(request)
        if results and results[0]:
            return results[0].supersign_active
        return True


class DownloadQrPermission(BasePermission):
    message = "权限不足"

    def has_permission(self, request, view):
        domain_type = request.query_params.get('domain_type', -1)
        results = get_user_from_request_auth(request)
        if results and results[0]:
            if domain_type == '0' and results[0].role < 2:
                return False
        return True
