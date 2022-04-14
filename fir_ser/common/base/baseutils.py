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

from fir_ser.settings import SUPER_SIGN_ROOT

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


class AesBaseCrypt(object):

    def __init__(self):
        self.cipher = AESCipher(self.__class__.__name__)

    def get_encrypt_uid(self, key):
        return self.cipher.encrypt(key.encode('utf-8')).decode('utf-8')

    def get_decrypt_uid(self, enc):
        return self.cipher.decrypt(enc)


class AppleDeveloperUid(AesBaseCrypt):
    ...


class WeixinLoginUid(AesBaseCrypt):
    ...


def make_from_user_uuid(uid):
    random_str = uuid.uuid1().__str__().split("-")[0:-1]
    user_ran_str = uuid.uuid5(uuid.NAMESPACE_DNS, uid).__str__().split("-")
    user_ran_str.extend(random_str)
    new_str = "".join(user_ran_str)
    return new_str


def make_app_uuid(userinfo, bundleid):
    user_id = userinfo.uid
    app_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id + bundleid}").__str__().split("-")
    return "".join(app_uuid)


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


def get_cname_from_domain(domain, resolve_cname):
    dns_list = [
        ["119.29.29.29", "114.114.114.114"],
        ["223.5.5.5", "223.6.6.6"],
        ["8.8.8.8", "8.8.4.4"],
    ]
    dns_resolver = Resolver()
    domain = domain.lower().strip()
    count = 3
    while count:
        try:
            dns_resolver.nameservers = dns_list[len(dns_list) - count]
            if dns_resolver.resolve(domain, 'CNAME')[0].to_text() == resolve_cname:
                return True
        except Exception as e:
            logger.error(f"dns {dns_resolver.nameservers} resolve {domain} failed Exception:{e}")
        count -= 1
        time.sleep(0.3)
    if count <= 0:
        return None


def get_user_default_domain_name(domain_cname_obj):
    if domain_cname_obj:
        return domain_cname_obj.is_https, domain_cname_obj.domain_record
    return None, None


def get_server_domain_from_request(request, server_domain):
    if not (server_domain and len(server_domain) > 8):  # len('https://')
        http_host = request.META.get('HTTP_HOST')
        server_protocol = request.META.get('SERVER_PROTOCOL')
        protocol = 'https'
        if server_protocol == 'HTTP/1.1':
            protocol = 'http'
        server_domain = f"{protocol}://{http_host}"
    return server_domain


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


def get_real_ip_address(request):
    if request.META.get('HTTP_X_FORWARDED_FOR', None):
        return request.META.get('HTTP_X_FORWARDED_FOR')
    else:
        return request.META.get('REMOTE_ADDR')


def get_origin_domain_name(request):
    meta = request.META
    return request.META.get('HTTP_ORIGIN', meta.get('HTTP_REFERER', 'https://xxx/xxx')).split('//')[-1].split('/')[0]


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


def get_choices_dict(choices, disabled_choices=None):
    result = []
    choices_org_list = list(choices)
    for choice in choices_org_list:
        val = {'id': choice[0], 'name': choice[1], 'disabled': False}
        if disabled_choices and isinstance(disabled_choices, list) and choice[0] in disabled_choices:
            val['disabled'] = True
        result.append(val)
    return result


def get_choices_name_from_key(choices, key):
    choices_org_list = list(choices)
    for choice in choices_org_list:
        if choice[0] == key:
            return choice[1]
    return ''


def make_resigned(bin_url, img_url, bundle_id, app_version, name):
    ios_plist_tem = """<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
  <key>items</key>
  <array>
    <dict>
      <key>assets</key>
      <array>
        <dict>
          <key>kind</key>
          <string>software-package</string>
          <key>url</key>
          <string><![CDATA[{bin_url}]]></string>
        </dict>
        <dict>
          <key>kind</key>
          <string>display-image</string>
          <key>needs-shine</key>
          <integer>0</integer>
          <key>url</key>
          <string><![CDATA[{img_url}]]></string>
        </dict>
        <dict>
          <key>kind</key>
          <string>full-size-image</string>
          <key>needs-shine</key>
          <true/>
          <key>url</key>
          <string><![CDATA[{img_url}]]></string>
        </dict>
      </array>
      <key>metadata</key>
      <dict>
        <key>bundle-identifier</key>
        <string>{bundle_id}</string>
        <key>bundle-version</key>
        <string><![CDATA[{app_version}]]></string>
        <key>kind</key>
        <string>software</string>
        <key>title</key>
        <string><![CDATA[{name}]]></string>
      </dict>
    </dict>
  </array>
</dict>
</plist>""".format(bin_url=bin_url, img_url=img_url, bundle_id=bundle_id, app_version=app_version, name=name)
    logger.info(
        f"make_resigned bin_url {bin_url} ,img_url {img_url}, bundle_id {bundle_id}, app_version {app_version}, name {name}")
    return ios_plist_tem
