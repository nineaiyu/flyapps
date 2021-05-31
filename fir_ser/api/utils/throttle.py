#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/25

from rest_framework.throttling import SimpleRateThrottle
import hashlib

from rest_framework.exceptions import Throttled


class VisitShortThrottle(SimpleRateThrottle):
    """短连接用户访问频率限制1"""
    scope = "ShortAccessUser1"

    def get_cache_key(self, request, view):
        return 'short_access_' + self.get_ident(request) + hashlib.md5(
            request.META.get('HTTP_USER_AGENT', '').encode("utf-8")).hexdigest()


class InstallShortThrottle(SimpleRateThrottle):
    """短连接用户访问频率限制2"""
    scope = "ShortAccessUser2"

    def get_cache_key(self, request, view):
        return 'short_access_' + self.get_ident(request)


class InstallThrottle1(VisitShortThrottle):
    """短连接用户访问频率限制"""
    scope = "InstallAccess1"

    def get_cache_key(self, request, view):
        return 'install_access_' + self.get_ident(request) + hashlib.md5(
            request.META.get('HTTP_USER_AGENT', '').encode("utf-8")).hexdigest()


class InstallThrottle2(InstallThrottle1):
    """短连接用户访问频率限制"""
    scope = "InstallAccess2"


class LoginUserThrottle(SimpleRateThrottle):
    """登录用户访问频率限制"""
    scope = "LoginUser"

    def get_cache_key(self, request, view):
        if hasattr(request.user, 'uid'):
            return request.user.uid
        else:
            self.get_ident(request)


class VisitRegister1Throttle(SimpleRateThrottle):
    """注册或者登陆限速1"""
    scope = "RegisterUser1"

    def get_cache_key(self, request, view):
        return 'login_register_' + self.get_ident(request)


class VisitRegister2Throttle(SimpleRateThrottle):
    """注册或者登陆限速2"""
    scope = "RegisterUser2"

    def get_cache_key(self, request, view):
        return 'login_register_' + self.get_ident(request)


class GetAuthC1Throttle(SimpleRateThrottle):
    """注册或者登陆限速1"""
    scope = "GetAuthC1"

    def get_cache_key(self, request, view):
        return 'get_auth_' + self.get_ident(request)


class GetAuthC2Throttle(SimpleRateThrottle):
    """注册或者登陆限速2"""
    scope = "GetAuthC2"

    def get_cache_key(self, request, view):
        return 'get_auth_' + self.get_ident(request)
