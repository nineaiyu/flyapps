#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/29

from rest_framework.views import APIView

from api.utils.baseutils import is_valid_domain, get_cname_from_domain
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from api.models import UserDomainInfo, DomainCnameInfo
from django.db.models import Count
import logging

from api.utils.storage.caches import set_default_app_wx_easy

logger = logging.getLogger(__name__)


class DomainCnameView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        res.data = {'domain_name': '', 'domain_record': '', 'is_enable': False}
        user_domain_obj = UserDomainInfo.objects.filter(user_id=request.user).first()
        if user_domain_obj:
            res.data['domain_name'] = user_domain_obj.domain_name
            res.data['is_enable'] = user_domain_obj.is_enable
            if user_domain_obj.cname_id:
                res.data['domain_record'] = user_domain_obj.cname_id.domain_record
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        domain_name = request.data.get("domain_name", None)
        if domain_name:
            domain_name = domain_name.strip(" ")
        if domain_name and len(domain_name) > 3 and is_valid_domain(domain_name):
            if UserDomainInfo.objects.filter(domain_name=domain_name, is_enable=True).count() != 0:
                res.code = 1001
                res.msg = "该域名已经被绑定，请更换其他域名"
            else:
                user_domian_obj = UserDomainInfo.objects.filter(user_id=request.user, domain_name=domain_name).first()
                if user_domian_obj:
                    res.data = {'cname_domain': user_domian_obj.cname_id.domain_record}
                else:
                    UserDomainInfo.objects.filter(user_id=request.user, is_enable=False).delete()
                    min_domian_cname_info_obj = min(
                        DomainCnameInfo.objects.annotate(Count('userdomaininfo')).filter(is_enable=True),
                        key=lambda x: x.userdomaininfo__count)
                    if min_domian_cname_info_obj:
                        res.data = {'cname_domain': min_domian_cname_info_obj.domain_record}
                        UserDomainInfo.objects.create(user_id=request.user, cname_id=min_domian_cname_info_obj,
                                                      domain_name=domain_name)
        else:
            res.code = 1002
            res.msg = "该域名校验失败，请检查"
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        user_domian_obj = UserDomainInfo.objects.filter(user_id=request.user).first()
        if user_domian_obj:
            cname = get_cname_from_domain(user_domian_obj.domain_name)
            if cname == user_domian_obj.cname_id.domain_record + '.':
                user_domian_obj.is_enable = True
                user_domian_obj.save()
                UserDomainInfo.objects.filter(domain_name=user_domian_obj.domain_name, is_enable=False).delete()
                set_default_app_wx_easy(request.user, True)
            else:
                res.code = 1003
                res.msg = "系统未检出到您的CNAME记录"
        else:
            res.code = 1004
            res.msg = "域名已经被绑定或者域名有误"
        return Response(res.dict)

    def delete(sele, request):
        res = BaseResponse()
        if UserDomainInfo.objects.filter(user_id=request.user).delete()[0]:
            set_default_app_wx_easy(request.user)
        return Response(res.dict)
