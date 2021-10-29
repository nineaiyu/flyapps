#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2021/4/16


from django.db.models import Count
import random
from api.models import AppReleaseInfo, UserDomainInfo, DomainCnameInfo, UserAdDisplayInfo, RemoteClientInfo
import logging
from urllib.parse import urljoin

from api.utils.baseutils import get_server_domain_from_request, get_user_default_domain_name, get_real_ip_address, \
    get_origin_domain_name

logger = logging.getLogger(__name__)


def get_app_d_count_by_app_id(app_id):
    d_count = 1
    binary_size = AppReleaseInfo.objects.filter(is_master=True, app_id__app_id=app_id).values('binary_size').first()
    if binary_size and binary_size.get('binary_size', 0) > 0:
        d_count += binary_size.get('binary_size') // 1024 // 1024 // 100
    return d_count


def get_user_domain_name(obj, domain_type=1):
    domain_name = UserDomainInfo.objects.filter(user_id=obj, is_enable=True, app_id=None,
                                                domain_type=domain_type).values_list('domain_name').first()
    if domain_name:
        return domain_name[0]
    return ''


def get_app_domain_name(obj):
    domain_name = UserDomainInfo.objects.filter(app_id=obj, is_enable=True, domain_type=2).values_list(
        'domain_name').first()
    if domain_name:
        return domain_name[0]
    return ''


def get_min_default_domain_cname_obj(is_system=True):
    return min(DomainCnameInfo.objects.annotate(Count('userinfo')).filter(is_enable=True, is_system=is_system),
               key=lambda x: x.userinfo__count)


def get_filename_form_file(filename):
    file_id_list = filename.split('.')
    if file_id_list[-1] in ['ipa', 'apk']:
        app_release_obj = AppReleaseInfo.objects.filter(release_id='.'.join(file_id_list[0:-1])).first()
        if app_release_obj:
            app_obj = app_release_obj.app_id
            if app_obj.type == 0:
                f_type = '.apk'
            else:
                f_type = '.ipa'
            return f"{app_obj.name}-{app_release_obj.app_version}-{app_obj.short}{f_type}"
    return filename


def ad_random_weight(user_obj):
    ad_info_list = UserAdDisplayInfo.objects.filter(user_id=user_obj, is_enable=True).order_by('-created_time')
    total = sum([ad_info.weight for ad_info in ad_info_list])  # 权重求和
    ra = random.uniform(0, total)  # 在0与权重和之前获取一个随机数
    curr_sum = 0
    ret = ad_info_list.first()
    for ad_info in ad_info_list:
        curr_sum += ad_info.weight  # 在遍历中，累加当前权重值
        if ra <= curr_sum:  # 当随机数<=当前权重和时，返回权重key
            ret = ad_info
            break
    return ret


def add_remote_info_from_request(request, description):
    meta_info = request.META
    remote_info = {
        'user_agent': meta_info.get('HTTP_USER_AGENT'),
        'remote_addr': get_real_ip_address(request),
        'method': meta_info.get('REQUEST_METHOD'),
        'uri_info': urljoin(meta_info.get('PATH_INFO'), meta_info.get('QUERY_STRING')),
        'a_domain': get_origin_domain_name(request),
        'description': description
    }
    RemoteClientInfo.objects.create(**remote_info)


def get_redirect_server_domain(request, user_obj=None, app_domain_name=None):
    is_https = False
    if user_obj:
        if app_domain_name and len(app_domain_name) > 3:
            domain_name = app_domain_name
        else:
            domain_name = get_user_domain_name(user_obj)
            if not domain_name:
                is_https, domain_name = get_user_default_domain_name(user_obj.default_domain_name)
    elif app_domain_name and len(app_domain_name) > 3:
        domain_name = app_domain_name
    else:
        is_https, domain_name = get_user_default_domain_name(get_min_default_domain_cname_obj(True))
    protocol = 'http'
    if is_https:
        protocol = 'https'
    server_domain = "%s://%s" % (protocol, domain_name)
    return get_server_domain_from_request(request, server_domain)


def check_app_domain_name_access(app_obj, access_domain_name, user_obj, extra_domain=None):
    if app_obj and access_domain_name:
        domain_list = []
        if extra_domain:
            domain_list.append(extra_domain)
        app_domain_name = get_app_domain_name(app_obj)
        if app_domain_name: domain_list.append(app_domain_name)
        user_domain_name = get_user_domain_name(user_obj)
        if user_domain_name: domain_list.append(user_domain_name)
        user_qr_domain_name = get_user_domain_name(user_obj, 0)
        if user_qr_domain_name: domain_list.append(user_qr_domain_name)
        if access_domain_name in domain_list:
            return True
