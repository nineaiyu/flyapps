#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/29
import logging

from dns import rdatatype
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import UserDomainInfo, Apps, DomainCnameInfo
from api.utils.modelutils import get_user_domain_name, get_min_default_domain_cname_obj, PageNumber
from api.utils.response import BaseResponse
from api.utils.serializer import DomainNameSerializer, DomainCnameInfoSerializer
from common.base.baseutils import is_valid_domain, get_cname_from_domain, get_choices_dict, make_app_uuid, \
    format_cname_host
from common.core.auth import ExpiringTokenAuthentication
from common.core.sysconfig import UserConfig
from common.utils.caches import del_cache_response_by_short, reset_app_wx_easy_type, reset_short_response_cache
from fir_ser.settings import DOMAIN_CNAME_KEY

logger = logging.getLogger(__name__)


def get_domain_filter(request):
    filter_dict = {'user_id': request.user, 'app_id__app_id': None}
    app_id = request.query_params.get("app_id", request.data.get("app_id", None))
    domain_type = request.query_params.get("domain_type", request.data.get("domain_type", None))
    domain_name = request.query_params.get("domain_name", request.data.get("domain_name", ''))
    if app_id is not None:
        filter_dict['app_id__app_id'] = app_id
    if domain_type is not None:
        filter_dict['domain_type'] = domain_type
    if domain_name:
        filter_dict['domain_name'] = domain_name
    logger.info(f"domain filter {filter_dict}")
    return filter_dict


def auto_clean_download_cache(user_obj, user_domain_obj, app_obj, delete=False):
    if user_domain_obj:
        base_domain_queryset = UserDomainInfo.objects.filter(user_id=user_obj, is_enable=True).all()
        if user_domain_obj.domain_type in [0, 1]:
            if delete:
                user_domain_obj.delete()
            if base_domain_queryset.filter(domain_type__in=[0, 1]).count() == 0:
                reset_app_wx_easy_type(user_obj, None)
        else:
            reset_app_wx_easy_type(user_obj, app_obj)


def remove_domain_wx_easy(app_obj, user_obj):
    if app_obj and not get_user_domain_name(user_obj):
        app_obj.wxeasytype = True
        app_obj.save(update_fields=['wxeasytype'])
        del_cache_response_by_short(app_obj.app_id)


def add_new_domain_info(res, request, domain_name, domain_type):
    user_ipk = 0
    if UserConfig(request.user).PRIVATE_DOWNLOAD_PAGE:
        user_ipk = request.user.pk

    min_domain_cname_info_obj = get_min_default_domain_cname_obj(False, user_ipk)
    if min_domain_cname_info_obj:
        res.data = {
            'domain_record': min_domain_cname_info_obj.domain_record,
            'is_private': bool(min_domain_cname_info_obj.user_ipk)
        }
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
                data_dict['domain_type'] = 2
        UserDomainInfo.objects.create(**data_dict)


class DomainCnameView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        res.data = {'domain_name': '', 'domain_record': '', 'is_enable': False, 'is_private': False}
        user_domain_obj = UserDomainInfo.objects.filter(**get_domain_filter(request)).last()
        domain_type = request.query_params.get("domain_type", -1)

        user_domain_obj2 = UserDomainInfo.objects.filter(user_id=request.user, domain_type=domain_type,
                                                         is_enable=False).last()
        domain_name = request.query_params.get("domain_name", '')
        if user_domain_obj and (domain_name or user_domain_obj.domain_type in [0, 2] or (
                domain_name == '' and user_domain_obj.domain_type == 1 and user_domain_obj2)):
            res.data['domain_name'] = user_domain_obj.domain_name
            res.data['is_enable'] = user_domain_obj.is_enable
            if user_domain_obj.cname_id:
                res.data['domain_record'] = user_domain_obj.cname_id.domain_record
                res.data['is_private'] = bool(user_domain_obj.cname_id.user_ipk)
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
            # filter_dict = get_domain_filter(request)
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
                    kwargs = get_domain_filter(request)
                    kwargs['domain_name'] = domain_name
                    user_domain_obj = UserDomainInfo.objects.filter(**kwargs).first()
                    if user_domain_obj:
                        res.data = {
                            'domain_record': user_domain_obj.cname_id.domain_record,
                            'is_private': bool(user_domain_obj.cname_id.user_ipk)
                        }
                    else:
                        kwargs.pop('domain_name')
                        UserDomainInfo.objects.filter(**kwargs, is_enable=False).delete()
                        add_new_domain_info(res, request, domain_name, domain_type)
            else:
                kwargs = get_domain_filter(request)
                kwargs['domain_name'] = domain_name
                user_domain_obj = UserDomainInfo.objects.filter(**kwargs).first()
                if user_domain_obj:
                    res.data = {
                        'domain_record': user_domain_obj.cname_id.domain_record,
                        'is_private': bool(user_domain_obj.cname_id.user_ipk)
                    }
                else:
                    add_new_domain_info(res, request, domain_name, domain_type)
        else:
            res.code = 1002
            res.msg = "该域名校验失败，请检查"
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()

        kwargs = get_domain_filter(request)
        if kwargs.get('domain_type', -1) in [0, 2]:
            domain_name = kwargs.get('domain_name')
            if domain_name:
                kwargs.pop('domain_name')
        kwargs['is_enable'] = False

        user_domain_obj = UserDomainInfo.objects.filter(**kwargs).first()
        if user_domain_obj:
            cname = get_cname_from_domain(user_domain_obj.domain_name, user_domain_obj.cname_id.domain_record + '.')
            if cname:
                user_domain_obj_list = UserDomainInfo.objects.filter(domain_name=user_domain_obj.domain_name,
                                                                     is_enable=True).all()
                if len(user_domain_obj_list) < 2:
                    if len(user_domain_obj_list) == 1:
                        user_obj = user_domain_obj_list.first().user_id
                        app_obj = user_domain_obj_list.first().app_id
                        o_user_domain_obj = user_domain_obj_list.first()
                        auto_clean_download_cache(user_obj, o_user_domain_obj, app_obj, True)
                        user_domain_obj_list.delete()

                    if kwargs.get('domain_type', -1) in [0, 2]:
                        kwargs.pop('is_enable')
                        UserDomainInfo.objects.filter(**kwargs).delete()

                    user_domain_obj.is_enable = True
                    user_domain_obj.save()

                    app_id = request.data.get("app_id", None)
                    app_obj = None
                    if app_id:
                        app_obj = Apps.objects.filter(app_id=app_id).first()
                    auto_clean_download_cache(request.user, user_domain_obj, app_obj)
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

    def delete(self, request):
        res = BaseResponse()
        user_domain_obj = UserDomainInfo.objects.filter(**get_domain_filter(request)).first()
        if user_domain_obj:
            app_id = request.query_params.get("app_id", None)
            app_obj = None
            if app_id:
                app_obj = Apps.objects.filter(app_id=app_id).first()
            auto_clean_download_cache(request.user, user_domain_obj, app_obj, True)
        return Response(res.dict)


class DomainInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        search_key = request.query_params.get("search_key", None)
        obj_lists = UserDomainInfo.objects.filter(user_id=request.user)
        if search_key:
            obj_lists1 = obj_lists.filter(domain_name=search_key)
            if not obj_lists1:
                obj_lists = obj_lists.filter(app_id__name__contains=search_key)
            else:
                obj_lists = obj_lists1

        page_obj = PageNumber()
        domain_info_serializer = page_obj.paginate_queryset(
            queryset=obj_lists.order_by("-created_time").order_by('domain_type'),
            request=request,
            view=self)
        domain_info = DomainNameSerializer(domain_info_serializer, many=True, )
        res.data = domain_info.data
        res.count = obj_lists.count()

        res.domain_type_choices = get_choices_dict(UserDomainInfo.domain_type_choices)

        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        domain_name = request.data.get('domain_name', '')
        weight = request.data.get('weight', 10)
        is_https = request.data.get('is_https', 10)
        domain_type = request.data.get('domain_type', None)
        if domain_type is not None and weight and domain_name:
            domain_name_obj = UserDomainInfo.objects.filter(user_id=request.user, domain_name=domain_name,
                                                            domain_type=domain_type).all()
            if domain_name_obj and len(domain_name_obj) == 1:
                domain_name_obj.update(weight=weight, is_https=is_https)
                reset_short_response_cache(request.user, None)
        else:
            res.code = 1002
            res.msg = '参数有误'
        return Response(res.dict)


class DomainCnameInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        search_key = request.query_params.get("search_key", None)
        obj_lists = DomainCnameInfo.objects.filter(user_ipk=request.user.pk)
        if search_key:
            obj_lists = obj_lists.filter(domain_record=search_key)

        page_obj = PageNumber()
        domain_info_serializer = page_obj.paginate_queryset(
            queryset=obj_lists.order_by("-created_time"), request=request, view=self)
        domain_info = DomainCnameInfoSerializer(domain_info_serializer, many=True, )
        res.data = domain_info.data
        res.count = obj_lists.count()

        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        domain_record = request.data.get('domain_record')
        act = request.data.get('act')
        if domain_record and act:
            c_obj = DomainCnameInfo.objects.filter(user_ipk=request.user.pk, domain_record=domain_record).first()
            if not c_obj:
                res.code = 1003
                res.msg = '参数有误'
                return Response(res.dict)
            if act == 'check':
                resolve_cname = f"{request.user.uid}{make_app_uuid(request.user, domain_record)}"
                auth_domain_record = f'{DOMAIN_CNAME_KEY}.{domain_record}'
                if get_cname_from_domain(auth_domain_record, resolve_cname, rd_type=rdatatype.TXT):
                    c_obj.is_enable = True
                    c_obj.save(update_fields=['is_enable'])
                    return Response(res.dict)
                else:
                    res.code = 1004
                    res.msg = 'TXT解析错误，请检查或者稍后再试'
        else:
            res.code = 1002
            res.msg = '参数有误'
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        domain_info = request.data
        domain_record = domain_info.get('domain_record')
        ip_address = domain_info.get('ip_address')
        description = domain_info.get('description')
        if domain_record and ip_address:
            c_obj = DomainCnameInfo.objects.filter(user_ipk=request.user.pk, domain_record=domain_record)
            if not c_obj:
                DomainCnameInfo.objects.create(user_ipk=request.user.pk, domain_record=domain_record,
                                               ip_address=ip_address, description=description)

            res.data = {
                'a_type': 'DNS',
                'r_type': 'TXT',
                'host_r': f'{DOMAIN_CNAME_KEY}.{format_cname_host(domain_record)}',
                'cname_r': f"{request.user.uid}{make_app_uuid(request.user, domain_record)}",
                'domain_record': domain_record
            }
        else:
            res.code = 1001
            res.msg = "参数有误"
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        domain_record = request.query_params.get('domain_record')
        if domain_record:
            c_query_set = DomainCnameInfo.objects.filter(user_ipk=request.user.pk, domain_record=domain_record)
            if UserDomainInfo.objects.filter(user_id=request.user, cname_id=c_query_set.first(),
                                             is_enable=True).count():
                reset_short_response_cache(request.user, None)
            c_query_set.delete()
            if DomainCnameInfo.objects.filter(user_ipk=request.user.pk, is_enable=True).count() == 0:
                UserConfig(request.user).del_value('PRIVATE_DOWNLOAD_PAGE')
        return Response(res.dict)
