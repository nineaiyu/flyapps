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

from api.utils.storage.caches import del_cache_response_by_short, reset_app_wx_easy_type, reset_short_response_cache

logger = logging.getLogger(__name__)


def get_domain_filter(request):
    filter_dict = {'user_id': request.user, 'app_id__app_id': None}
    app_id = request.query_params.get("app_id", request.data.get("app_id", None))
    domain_type = request.query_params.get("domain_type", request.data.get("domain_type", None))
    if app_id is not None:
        filter_dict['app_id__app_id'] = app_id
    if domain_type is not None:
        filter_dict['domain_type'] = domain_type
    logger.info(f"domain filter {filter_dict}")
    return filter_dict


def remove_domain_wx_easy(app_obj, user_obj):
    if app_obj and not get_user_domain_name(user_obj):
        app_obj.wxeasytype = True
        app_obj.save(update_fields=['wxeasytype'])
        del_cache_response_by_short(app_obj.app_id)


def add_new_domain_info(res, request, domain_name, domain_type):
    min_domain_cname_info_obj = get_min_default_domain_cname_obj(False)
    if min_domain_cname_info_obj:
        res.data = {'cname_domain': min_domain_cname_info_obj.domain_record}
        data_dict = {
            'user_id': request.user,
            'cname_id': min_domain_cname_info_obj,
            'domain_name': domain_name,
            'app_id': None,
            'domain_type': domain_type
        }
        app_id = request.data.get("app_id", None)
        if app_id:
            app_obj = Apps.objects.filter(app_id=app_id).first()
            if app_obj:
                data_dict['app_id'] = app_obj
        UserDomainInfo.objects.create(**data_dict)


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
        domain_type = request.data.get('domain_type', 1)
        force_bind = request.data.get('force_bind', 0)
        if domain_type not in [x[0] for x in list(UserDomainInfo.domain_type_choices)]:
            res.code = 1001
            res.msg = "绑定失败"
            return Response(res.dict)
        if domain_name:
            domain_name = domain_name.strip(" ")
        if domain_name and len(domain_name) > 3 and is_valid_domain(domain_name):
            filter_dict = get_domain_filter(request)
            if not force_bind:
                user_domain_obj = UserDomainInfo.objects.filter(domain_name=domain_name, is_enable=True).first()
                if user_domain_obj:
                    res.code = 1011
                    if user_domain_obj.user_id.uid == request.user.uid:
                        app_obj = user_domain_obj.app_id
                        if app_obj:
                            res.msg = f"该域名已经被应用 {app_obj.name} 绑定"
                        elif user_domain_obj.domain_type == 0:
                            res.msg = f"该域名已经被 应用下载码绑定"
                        else:
                            res.msg = f"该域名已经被 预览下载页绑定"
                    else:
                        res.msg = "该域名已经被其他用户绑定"
                    res.msg += "，请更换要绑定的域名，或者进行强制绑定域名"
                else:
                    user_domain_obj = UserDomainInfo.objects.filter(**get_domain_filter(request),
                                                                    domain_name=domain_name).first()
                    if user_domain_obj:
                        res.data = {'cname_domain': user_domain_obj.cname_id.domain_record}
                    else:
                        UserDomainInfo.objects.filter(**filter_dict, is_enable=False).delete()
                        add_new_domain_info(res, request, domain_name, domain_type)
            else:
                user_domain_obj = UserDomainInfo.objects.filter(**filter_dict,
                                                                domain_name=domain_name).first()
                if user_domain_obj:
                    res.data = {'cname_domain': user_domain_obj.cname_id.domain_record}
                else:
                    add_new_domain_info(res, request, domain_name, domain_type)
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
                user_domain_obj_list = UserDomainInfo.objects.filter(domain_name=user_domain_obj.domain_name,
                                                                     is_enable=True).all()
                if len(user_domain_obj_list) < 2:
                    if len(user_domain_obj_list) == 1:
                        user_obj = user_domain_obj_list.first().user_id
                        app_obj = user_domain_obj_list.first().app_id
                        user_domain_obj_list.delete()
                        reset_app_wx_easy_type(user_obj, app_obj)

                    user_domain_obj.is_enable = True
                    user_domain_obj.save(update_fields=["is_enable"])

                    app_id = request.data.get("app_id", None)
                    app_obj = None
                    if app_id:
                        app_obj = Apps.objects.filter(app_id=app_id).first()
                    reset_app_wx_easy_type(request.user, app_obj)
                else:
                    res.code = 1002
                    res.msg = "该域名查询校验失败，请检查"
            else:
                res.code = 1003
                res.msg = "系统未检出到您的CNAME记录"
        else:
            res.code = 1004
            res.msg = "域名已经被绑定或者域名有误"
        return Response(res.dict)

    def delete(sele, request):
        res = BaseResponse()
        user_domain_obj = UserDomainInfo.objects.filter(**get_domain_filter(request)).first()
        if user_domain_obj:
            app_id = request.query_params.get("app_id", None)
            app_obj = None
            if app_id:
                app_obj = Apps.objects.filter(app_id=app_id).first()
            reset_app_wx_easy_type(request.user, app_obj)
            user_domain_obj.delete()
        return Response(res.dict)
