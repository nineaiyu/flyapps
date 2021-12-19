#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2021/4/16

import base64
import datetime
import hashlib
import logging
import os
import random
import re
import time
import uuid

from Crypto import Random
from Crypto.Cipher import AES
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from dns.resolver import Resolver

from fir_ser.settings import SUPER_SIGN_ROOT, SERVER_DOMAIN

logger = logging.getLogger(__name__)


class AESCipher(object):

    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pack_data(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpack_data(cipher.decrypt(enc[AES.block_size:]))

    @staticmethod
    def _pack_data(s):
        return s + ((AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)).encode(
            'utf-8')

    @staticmethod
    def _unpack_data(s):
        data = s[:-ord(s[len(s) - 1:])]
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return data


def make_from_user_uuid(uid):
    random_str = uuid.uuid1().__str__().split("-")[0:-1]
    user_ran_str = uuid.uuid5(uuid.NAMESPACE_DNS, uid).__str__().split("-")
    user_ran_str.extend(random_str)
    new_str = "".join(user_ran_str)
    return new_str


def make_app_uuid(userinfo, bundleid):
    user_id = userinfo.uid
    app_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, "%s" % (user_id + bundleid)).__str__().split("-")
    fapp_uuid = "".join(app_uuid)
    return fapp_uuid


def make_random_uuid():
    random_str = uuid.uuid1().__str__().split("-")
    return "".join(random_str)


def file_format_path(user_obj, auth=None):
    cert_dir_name = make_app_uuid(user_obj, auth.get("issuer_id"))
    cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name)
    if not os.path.isdir(cert_dir_path):
        os.makedirs(cert_dir_path)
    file_format_path_name = os.path.join(cert_dir_path, cert_dir_name)
    return file_format_path_name


def get_profile_full_path(developer_obj, app_obj):
    cert_dir_name = make_app_uuid(developer_obj.user_id, developer_obj.issuer_id)
    cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name, "profile")
    provision_name = os.path.join(cert_dir_path, app_obj.app_id)
    return provision_name + '.mobileprovision'


def delete_app_profile_file(developer_obj, app_obj):
    file = get_profile_full_path(developer_obj, app_obj)
    try:
        if os.path.isfile(file):
            os.remove(file)
    except Exception as e:
        logger.error(
            f"delete_app_profile_file developer_obj:{developer_obj}  app_obj:{app_obj} file:{file} Exception:{e}")


def is_valid_domain(value):
    pattern = re.compile(
        r'^(([a-zA-Z])|([a-zA-Z][a-zA-Z])|'
        r'([a-zA-Z][0-9])|([0-9][a-zA-Z])|'
        r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
        r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )
    return True if pattern.match(value) else False


def is_telephone_number(telephone):
    if len(telephone) == 11:
        if re.match(r"^1(?:749)\d{7}$", telephone):
            return 'MSC'  # 海事卫星通信的
        elif re.match(r"^174(?:0[6-9]|1[0-2])\d{6}$", telephone):
            return 'MCC'  # 工信部应急通信的
        elif re.match(r"^1(?:349)\d{7}$", telephone):
            return 'CM_SMC'  # 中国移动卫星通信
        elif re.match(r"^1(?:740[0-5])\d{6}$", telephone):
            return 'CT_SMC'  # 中国电信卫星通信
        elif re.match(r"^1(?:47)\d{8}$", telephone):
            return 'CM_IDC'  # 中国移动上网数据卡
        elif re.match(r"^1(?:45)\d{8}$", telephone):
            return 'CU_IDC'  # 中国联通上网数据卡
        elif re.match(r"^1(?:49)\d{8}$", telephone):
            return 'CT_IDC'  # 中国电信上网数据卡
        elif re.match(r"^1(?:70[356]|65\d)\d{7}$", telephone):
            return 'CM_VNO'  # 中国移动虚拟运营商
        elif re.match(r"^1(?:70[4,7-9]|71\d|67\d)\d{7}$", telephone):
            return 'CU_VNO'  # 中国联通虚拟运营商
        elif re.match(r"^1(?:70[0-2]|62\d)\d{7}$", telephone):
            return 'CT_VNO'  # 中国电信虚拟运营商
        elif re.match(r"^1(?:34[0-8]|3[5-9]\d|5[0-2,7-9]\d|7[28]\d|8[2-4,7-8]\d|9[5,7,8]\d)\d{7}$", telephone):
            return 'CM_BO'  # 中国移动
        elif re.match(r"^1(?:3[0-2]|[578][56]|66|96)\d{8}$", telephone):
            return 'CU_BO'  # 中国联通
        elif re.match(r"^1(?:33|53|7[37]|8[019]|9[0139])\d{8}$", telephone):
            return 'CT_BO'  # 中国电信
        elif re.match(r"^1(?:92)\d{8}$", telephone):
            return 'CBN_BO'  # 中国广电
        else:
            return False
    elif len(telephone) == 13:
        if re.match(r"^14(?:40|8\d)\d{9}$", telephone):
            return 'CM_IoT'  # 中国移动物联网数据卡
        elif re.match(r"^14(?:00|6\d)\d{9}$", telephone):
            return 'CU_IoT'  # 中国联通物联网数据卡
        elif re.match(r"^14(?:10)\d{9}$", telephone):
            return 'CT_IoT'  # 中国电信物联网数据卡
        else:
            return False
    else:
        return False


def is_valid_phone(value):
    # phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
    # return True if str(value) and re.search(phone_pat, str(value)) else False
    logger.info(f"valid phone {value}")
    return str(value) and is_telephone_number(str(value))


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def get_dict_from_filter_fields(filter_fields, data):
    filter_data = {}
    for filed in filter_fields:
        f_value = data.get(filed, None)
        if f_value:
            if f_value == 'true':
                f_value = True
            if f_value == 'false':
                f_value = False
            filter_data[filed] = f_value
    return filter_data


def format_storage_selection(storage_info_list, storage_choice_list):
    storage_info_list.append({'id': -1, 'storage_type': 3, 'name': '默认存储'})
    for storage_choice in storage_choice_list:
        storage_choice['storage_info'] = []
        for storage_info in storage_info_list:
            if storage_info.get('storage_type') == storage_choice.get('id', ):
                storage_choice['storage_info'].append(
                    {'name': storage_info.get('name', ''), 'id': storage_info.get('id', '')})
    for storage_choice in storage_choice_list:
        if not storage_choice['storage_info']:
            storage_choice_list.remove(storage_choice)
    return storage_choice_list


def get_cname_from_domain(domain):
    dns_list = [
        ["8.8.8.8", "8.8.4.4"],
        ["119.29.29.29", "114.114.114.114"],
        ["223.5.5.5", "223.6.6.6"],
    ]
    dns_resolver = Resolver()
    domain = domain.lower().strip()
    count = 3
    while count:
        try:
            dns_resolver.nameservers = dns_list[len(dns_list) - count]
            return dns_resolver.resolve(domain, 'CNAME')[0].to_text()
        except Exception as e:
            logger.error(f"dns {dns_resolver.nameservers} resolve {domain} failed Exception:{e}")
        count -= 1
        time.sleep(0.3)
    if count <= 0:
        return str(None)


def get_user_default_domain_name(domain_cname_obj):
    if domain_cname_obj:
        return domain_cname_obj.is_https, domain_cname_obj.domain_record
    return None, None


def get_server_domain_from_request(request, server_domain):
    if not server_domain or not server_domain.startswith("http"):
        http_host = request.META.get('HTTP_HOST')
        server_protocol = request.META.get('SERVER_PROTOCOL')
        protocol = 'https'
        if server_protocol == 'HTTP/1.1':
            protocol = 'http'
        server_domain = "%s://%s" % (protocol, http_host)
    return server_domain


def get_http_server_domain(request):
    server_domain = SERVER_DOMAIN.get('POST_UDID_DOMAIN', None)
    return get_server_domain_from_request(request, server_domain)


def get_post_udid_url(request, short):
    server_domain = get_http_server_domain(request)
    path_info_lists = [server_domain, "udid", short]
    return "/".join(path_info_lists)


def format_apple_date(s_date):
    try:
        f_date = datetime.datetime.strptime(s_date, '%Y-%m-%dT%H:%M:%S.000+0000')
    except Exception as e:
        f_date = datetime.datetime.strptime(s_date, '%Y-%m-%dT%H:%M:%S.000+00:00')

    if not timezone.is_naive(f_date):
        f_date = timezone.make_naive(f_date, timezone.utc)
    return f_date


def get_format_time():
    now = timezone.now()
    if not timezone.is_naive(now):
        now = timezone.make_naive(now, timezone.utc)
    return now.strftime('%Y-%m-%d_%H:%M:%S')


def check_app_password(app_password, password):
    if app_password != '':
        if password is None:
            return None
    if app_password.lower() != password.strip().lower():
        return None
    return True


def get_real_ip_address(request):
    if request.META.get('HTTP_X_FORWARDED_FOR', None):
        return request.META.get('HTTP_X_FORWARDED_FOR')
    else:
        return request.META.get('REMOTE_ADDR')


def get_origin_domain_name(request):
    meta = request.META
    return request.META.get('HTTP_ORIGIN', meta.get('HTTP_REFERER', 'http://xxx/xxx')).split('//')[-1].split('/')[0]


def format_get_uri(domain, short, data):
    uri = ''
    for k, v in data.items():
        if v:
            uri += f'&{k}={v}'
    if uri:
        uri = '?' + uri[1:]
    return f'{domain}/{short}{uri}'


def get_order_num(order_type=1):
    now = datetime.datetime.now()
    date_str = "{0}{1}{2}{3}{4}{5}{6}".format(order_type, now.year, now.month, now.day, now.hour, now.minute,
                                              now.second)
    return date_str + str(random.randint(1000, 9999)) + str(random.randint(1000, 9999)) + str(
        random.randint(1000, 9999))
