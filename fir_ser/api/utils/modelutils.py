#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2021/4/16


import logging
import random
from urllib.parse import urljoin

from django.db.models import Count
from rest_framework.pagination import PageNumberPagination

from api.models import AppReleaseInfo, UserDomainInfo, DomainCnameInfo, UserAdDisplayInfo, RemoteClientInfo
from common.base.baseutils import get_server_domain_from_request, get_user_default_domain_name, get_real_ip_address, \
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


def get_app_download_domain(user_obj, request=None, app_obj=None, preview=False):
    # 如果有专属域名，则返回专属域名
    # 如果只配置了下载码域名，则返回下载码域名
    # 如果配置下载页域名，则返回下载页域名
    # 最后返回该用户系统默认域名
    base_user_domain = UserDomainInfo.objects.filter(is_enable=True, user_id=user_obj).all()
    if app_obj:
        app_domain_name = base_user_domain.filter(app_id=app_obj, domain_type=2).first()
        if app_domain_name:
            return app_domain_name.is_https, app_domain_name.domain_name

    qr_domain_name = base_user_domain.filter(app_id=None, domain_type=0).values_list('is_https', 'domain_name').first()
    download_domain_name = base_user_domain.filter(app_id=None, domain_type=1).all()
    if request:
        origin_domain_name = get_origin_domain_name(request)
        exist_download_obj = download_domain_name.filter(domain_name=origin_domain_name).first()
        if exist_download_obj:
            return exist_download_obj.is_https, exist_download_obj.domain_name

    download_domain_name = base_random_weight(download_domain_name, 'weight')
    if preview:
        if qr_domain_name:
            return qr_domain_name
    else:
        if qr_domain_name and not download_domain_name:
            return qr_domain_name
    if download_domain_name:
        return download_domain_name.is_https, download_domain_name.domain_name
    return get_user_default_domain_name(user_obj.default_domain_name)


def get_app_download_uri(request, user_obj, app_obj=None, preview=True):
    is_https, domain_name = get_app_download_domain(user_obj, request, app_obj, preview)
    if not (domain_name and len(domain_name) > 3):
        is_https, domain_name = get_user_default_domain_name(get_min_default_domain_cname_obj(True))
    server_domain = ''
    if domain_name and len(domain_name) > 3:
        protocol = 'https' if is_https else 'http'
        server_domain = f"{protocol}://{domain_name}"
    return get_server_domain_from_request(request, server_domain)


def get_min_default_domain_cname_obj(is_system=True):
    domain_queryset = DomainCnameInfo.objects.annotate(Count('userinfo')).filter(is_enable=True, is_system=is_system)
    if not domain_queryset:
        return DomainCnameInfo.objects.filter(is_enable=True, is_system=True).first()
    return min(domain_queryset, key=lambda x: x.userinfo__count)


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


def base_random_weight(obj, key):
    total = sum([getattr(ad_info, key) for ad_info in obj])  # 权重求和
    ra = random.uniform(0, total)  # 在0与权重和之前获取一个随机数
    curr_sum = 0
    ret = obj.first()
    for ad_info in obj:
        curr_sum += getattr(ad_info, key)  # 在遍历中，累加当前权重值
        if ra <= curr_sum:  # 当随机数<=当前权重和时，返回权重key
            ret = ad_info
            break
    return ret


def ad_random_weight(user_obj):
    ad_info_list = UserAdDisplayInfo.objects.filter(user_id=user_obj, is_enable=True).order_by('-created_time')
    return base_random_weight(ad_info_list, 'weight')


def add_remote_info_from_request(request, description):
    meta_info = request.META
    if request.user and request.user.id is not None:
        description = f"{request.user.uid}_{description}"
    remote_info = {
        'user_agent': meta_info.get('HTTP_USER_AGENT')[0:510],
        'remote_addr': get_real_ip_address(request),
        'method': meta_info.get('REQUEST_METHOD'),
        'uri_info': urljoin(meta_info.get('PATH_INFO'), meta_info.get('QUERY_STRING'))[0:255],
        'a_domain': get_origin_domain_name(request)[0:127],
        'description': description[0:255]
    }
    try:
        RemoteClientInfo.objects.create(**remote_info)
    except Exception as e:
        logger.error(e)


def get_redirect_server_domain(request, user_obj=None):
    is_https = False
    if user_obj:
        domain_name = get_user_domain_name(user_obj)
        if not domain_name:
            is_https, domain_name = get_user_default_domain_name(user_obj.default_domain_name)
    else:
        is_https, domain_name = get_user_default_domain_name(get_min_default_domain_cname_obj(True))
    protocol = 'https' if is_https else 'http'
    server_domain = f"{protocol}://{domain_name}"
    return get_server_domain_from_request(request, server_domain)


def check_app_domain_name_access(app_obj, access_domain_name, user_obj, extra_domain=None):
    if app_obj and access_domain_name:
        domain_list = []
        if extra_domain:
            domain_list.append(extra_domain)
        app_domain_name = get_app_domain_name(app_obj)
        if app_domain_name:
            domain_list.append(app_domain_name)
        user_domain_name = get_user_domain_name(user_obj)
        if user_domain_name:
            domain_list.append(user_domain_name)
        user_qr_domain_name = get_user_domain_name(user_obj, 0)
        if user_qr_domain_name:
            domain_list.append(user_qr_domain_name)
        if access_domain_name in domain_list:
            return True


class PageNumber(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = 100  # 最大页码数限制
