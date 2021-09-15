#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/29

from rest_framework.views import APIView

from api.utils.baseutils import is_valid_domain, get_cname_from_domain, get_user_domain_name, \
    get_min_default_domain_cname_obj
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from api.models import UserDomainInfo, Apps
import logging

from api.utils.storage.caches import set_default_app_wx_easy, del_cache_response_by_short

logger = logging.getLogger(__name__)


def get_domain_filter(request):
    filter_dict = {'user_id': request.user, 'app_id__app_id': None}
    app_id = request.query_params.get("app_id", request.data.get("app_id", None))
    if app_id:
        filter_dict['app_id__app_id'] = app_id
    return filter_dict


class DomainCnameView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        res.data = {'domain_name': '', 'domain_record': '', 'is_enable': False}
        user_domain_obj = UserDomainInfo.objects.filter(**get_domain_filter(request)).first()
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
                user_domain_obj = UserDomainInfo.objects.filter(**get_domain_filter(request),
                                                                domain_name=domain_name).first()
                if user_domain_obj:
                    res.data = {'cname_domain': user_domain_obj.cname_id.domain_record}
                else:
                    UserDomainInfo.objects.filter(**get_domain_filter(request), is_enable=False).delete()
                    min_domain_cname_info_obj = get_min_default_domain_cname_obj(False)
                    if min_domain_cname_info_obj:
                        res.data = {'cname_domain': min_domain_cname_info_obj.domain_record}
                        data_dict = {
                            'user_id': request.user,
                            'cname_id': min_domain_cname_info_obj,
                            'domain_name': domain_name,
                            'app_id': None,
                        }
                        app_id = request.data.get("app_id", None)
                        if app_id:
                            app_obj = Apps.objects.filter(app_id=app_id).first()
                            if app_obj:
                                data_dict['app_id'] = app_obj
                        UserDomainInfo.objects.create(**data_dict)
        else:
            res.code = 1002
            res.msg = "该域名校验失败，请检查"
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        user_domain_obj = UserDomainInfo.objects.filter(**get_domain_filter(request)).first()
        if user_domain_obj:
            cname = get_cname_from_domain(user_domain_obj.domain_name)
            if cname == user_domain_obj.cname_id.domain_record + '.':
                user_domain_obj.is_enable = True
                user_domain_obj.save(update_fields=["is_enable"])
                UserDomainInfo.objects.filter(domain_name=user_domain_obj.domain_name, is_enable=False).delete()
                app_id = request.data.get("app_id", None)
                if app_id:
                    app_obj = Apps.objects.filter(app_id=app_id).first()
                    if app_obj:
                        app_obj.wxeasytype = False
                        app_obj.save(update_fields=['wxeasytype'])
                        del_cache_response_by_short(app_obj.app_id)
                else:
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
        if UserDomainInfo.objects.filter(**get_domain_filter(request)).delete()[0]:
            app_id = request.query_params.get("app_id", None)
            if app_id:
                app_obj = Apps.objects.filter(app_id=app_id).first()
                if app_obj and not get_user_domain_name(request.user):
                    app_obj.wxeasytype = True
                    app_obj.save(update_fields=['wxeasytype'])
                    del_cache_response_by_short(app_obj.app_id)
            else:
                set_default_app_wx_easy(request.user)
        return Response(res.dict)
