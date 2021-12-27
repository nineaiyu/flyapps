#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月 
# author: NinEveN
# date: 2020/4/17

# pip install pyjwt
import base64
import logging
import os
import time
from collections import namedtuple
from functools import wraps

import jwt
import requests
from django.conf import settings

from api.utils.crontab.iproxy import get_proxy_ip_from_cache

logger = logging.getLogger(__name__)


# https://developer.apple.com/documentation/appstoreconnectapi/creating_api_keys_for_app_store_connect_api
#  https://appstoreconnect.apple.com/access/api 去申请秘钥
#

# proxies = settings.APPLE_DEVELOPER_API_PROXY if settings.APPLE_DEVELOPER_API_PROXY else {}

# timeout = settings.APPLE_DEVELOPER_API_TIMEOUT if settings.APPLE_DEVELOPER_API_TIMEOUT else 120


def request_format_log(req):
    try:
        logger.info(f"url:{req.url} header:{req.headers} code:{req.status_code} body:{req.content}")
    except Exception as e:
        logger.error(e)
    return req


# 需要和model里面的对应起来
capability_info = [
    [],
    ["PUSH_NOTIFICATIONS"],
    [
        "PERSONAL_VPN",
        "PUSH_NOTIFICATIONS",
        "NETWORK_EXTENSIONS",
    ],
    [
        "PERSONAL_VPN",
        "PUSH_NOTIFICATIONS",
        "NETWORK_EXTENSIONS",
        "WALLET",
        "ICLOUD",
        "INTER_APP_AUDIO",
        "ASSOCIATED_DOMAINS",
        "APP_GROUPS",
        "HEALTHKIT",
        "HOMEKIT",
        "WIRELESS_ACCESSORY_CONFIGURATION",
        "APPLE_PAY",
        "DATA_PROTECTION",
        "SIRIKIT",
        "MULTIPATH",
        "HOT_SPOT",
        "NFC_TAG_READING",
        "CLASSKIT",
        "AUTOFILL_CREDENTIAL_PROVIDER",
        "ACCESS_WIFI_INFORMATION",
        "COREMEDIA_HLS_LOW_LATENCY",
    ]
]


def get_capability(s_type):
    return capability_info[s_type]


class DevicesAPI(object):
    # https://developer.apple.com/documentation/appstoreconnectapi/devices
    def __init__(self, base_uri, jwt_headers):
        self.headers = jwt_headers
        self.devices_url = '%s/devices' % base_uri

    def list_devices(self, query_parameters=None):
        """
        :param query_parameters:
        :return:
            200 DevicesResponse OK  Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json

        """
        params = {
            "fields[devices]": "addedDate, deviceClass, model, name, platform, status, udid",
            "filter[platform]": "IOS",
            "limit": 200
        }
        if query_parameters:
            for k, v in query_parameters.items():
                params[k] = v
        return request_format_log(
            requests.get(self.devices_url, params=params, headers=self.headers, proxies=self.proxies,
                         timeout=self.timeout))

    def list_enabled_devices(self):
        return self.list_devices({"filter[status]": "ENABLED"})

    def list_disabled_devices(self):
        return self.list_devices({"filter[status]": "DISABLED"})

    def list_device_by_device_id(self, device_id):
        return self.list_devices({"filter[id]": device_id})

    def register_device(self, device_name, device_udid, platform="IOS"):
        """
        :param device_name:
        :param device_udid:
        :param platform:
        :return:
            201 DeviceResponse Created Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json

        """
        json = {
            'data': {
                'type': 'devices',
                'attributes': {
                    'name': device_name,
                    'udid': device_udid,
                    'platform': platform  # IOS or MAC_OS
                }
            }
        }
        return request_format_log(
            requests.post(self.devices_url, json=json, headers=self.headers, proxies=self.proxies,
                          timeout=self.timeout))

    def read_device_information(self, device_id):
        """
        :param device_id:
        :return:
            200 DeviceResponse OK Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            404 ErrorResponse Not Found Resource not found. Content-Type: application/json
        """
        base_url = '%s/%s' % (self.devices_url, device_id)
        params = {
            "fields[devices]": "addedDate, deviceClass, model, name, platform, status, udid",
        }
        return request_format_log(
            requests.get(base_url, params=params, headers=self.headers, proxies=self.proxies, timeout=self.timeout))

    def enabled_device(self, device_id, device_name):
        return self.modify_registered_device(device_id, device_name, 'ENABLED')

    def disabled_device(self, device_id, device_name):
        return self.modify_registered_device(device_id, device_name, 'DISABLED')

    def modify_registered_device(self, device_id, device_name, status):
        """
        :param device_id:
        :param device_name:
        :param status:
        :return:
            200 DeviceResponse OK Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            404 ErrorResponse Not Found Resource not found. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        base_url = '%s/%s' % (self.devices_url, device_id)
        json = {
            'data': {
                'type': 'devices',
                'id': device_id,
                'attributes': {
                    'name': device_name,
                    'status': status
                }
            }
        }
        return request_format_log(
            requests.patch(base_url, json=json, headers=self.headers, proxies=self.proxies, timeout=self.timeout))


class BundleIDsAPI(object):
    # https://developer.apple.com/documentation/appstoreconnectapi/bundle_ids
    def __init__(self, base_uri, jwt_headers):
        self.headers = jwt_headers
        self.bundle_ids_url = '%s/bundleIds' % base_uri

    def register_bundle_id(self, bundle_id_name, bundle_id_identifier, platform="IOS", seed_id=''):
        """
        :param bundle_id_name:
        :param bundle_id_identifier:
        :param platform:
        :param seed_id:
        :return:
            201 BundleIdResponse Created Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        json = {
            'data': {
                'type': 'bundleIds',
                'attributes': {
                    'name': bundle_id_name,
                    'identifier': bundle_id_identifier,
                    'platform': platform,
                    'seedId': seed_id
                }
            }
        }
        return request_format_log(
            requests.post(self.bundle_ids_url, json=json, headers=self.headers, proxies=self.proxies,
                          timeout=self.timeout))

    def delete_bundle_id_by_id(self, bundle_id):
        """
        :param bundle_id:
        :return:
            204	No Content
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            404 ErrorResponse Not Found Resource not found. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        base_url = '%s/%s' % (self.bundle_ids_url, bundle_id)
        json = {}
        return request_format_log(
            requests.delete(base_url, json=json, headers=self.headers, proxies=self.proxies, timeout=self.timeout))

    def list_bundle_ids(self, query_parameters=None):
        """
        :param query_parameters:
        :return:
            200 BundleIdsResponse  OK  Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
        """
        params = {
            "fields[bundleIds]": "identifier, name, platform, profiles, seedId",
            # "filter[platform]": "IOS",
            "limit": 200
        }
        if query_parameters:
            for k, v in query_parameters.items():
                params[k] = v
        return request_format_log(
            requests.get(self.bundle_ids_url, params=params, headers=self.headers, proxies=self.proxies,
                         timeout=self.timeout))

    def list_bundle_id_by_identifier(self, identifier):
        return self.list_bundle_ids({"filter[identifier]": identifier})

    def list_bundle_id_by_id(self, bundle_id):
        return self.list_bundle_ids({"filter[id]": bundle_id})

    def modify_bundle_id(self, bundle_id, bundle_name):
        """
        :param bundle_id:
        :param bundle_name:
        :return:
            200 BundleIdResponse OK Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            404 ErrorResponse Not Found Resource not found. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        base_url = '%s/%s' % (self.bundle_ids_url, bundle_id)
        json = {
            'data': {
                'type': 'bundleIds',
                'id': bundle_id,
                'attributes': {
                    'name': bundle_name,
                }
            }
        }
        return request_format_log(
            requests.patch(base_url, json=json, headers=self.headers, proxies=self.proxies, timeout=self.timeout))


class BundleIDsCapabilityAPI(object):
    # https://developer.apple.com/documentation/appstoreconnectapi/bundle_id_capabilities
    def __init__(self, base_uri, jwt_headers):
        self.headers = jwt_headers
        self.bundle_ids_capability_url = '%s/bundleIdCapabilities' % base_uri

    def disable_capability(self, bundle_id, capability_type):
        """
        :param capability_type:
        :param bundle_id:
        :return:
            204	No Content
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            404 ErrorResponse Not Found Resource not found. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        base_url = '%s/%s_%s' % (self.bundle_ids_capability_url, bundle_id, capability_type)
        json = {}
        return request_format_log(
            requests.delete(base_url, json=json, headers=self.headers, proxies=self.proxies, timeout=self.timeout))

    def enable_capability(self, bundle_id, capability_type):
        """
        :param bundle_id:
        :param capability_type:
        :return:
            201 BundleIdCapabilityResponse Created Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        json = {
            'data': {
                'type': 'bundleIdCapabilities',
                'attributes': {
                    'capabilityType': capability_type,  # 'PUSH_NOTIFICATIONS',#PERSONAL_VPN
                    'settings': []
                },
                'relationships': {
                    'bundleId': {
                        'data': {
                            'id': bundle_id,
                            'type': 'bundleIds',
                        }
                    }
                }
            }
        }
        return request_format_log(
            requests.post(self.bundle_ids_capability_url, json=json, headers=self.headers, proxies=self.proxies,
                          timeout=self.timeout))


class ProfilesAPI(object):
    # https://developer.apple.com/documentation/appstoreconnectapi/profiles
    def __init__(self, base_uri, jwt_headers):
        self.headers = jwt_headers
        self.profiles_url = '%s/profiles' % base_uri

    def create_profile(self, bundle_id, certificate_id_list, profile_name, device_id_list,
                       profile_type='IOS_APP_ADHOC'):
        """

        :param bundle_id:
        :param certificate_id_list:
        :param profile_name:
        :param device_id_list:
        :param profile_type:
        :return:
            201 ProfileResponse Created Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        json = {
            'data': {
                'type': 'profiles',
                'attributes': {
                    'name': profile_name,
                    'profileType': profile_type,
                    # Possible values: IOS_APP_DEVELOPMENT, IOS_APP_STORE, IOS_APP_ADHOC, IOS_APP_INHOUSE,
                    # MAC_APP_DEVELOPMENT, MAC_APP_STORE, MAC_APP_DIRECT, TVOS_APP_DEVELOPMENT, TVOS_APP_STORE,
                    # TVOS_APP_ADHOC, TVOS_APP_INHOUSE, MAC_CATALYST_APP_DEVELOPMENT, MAC_CATALYST_APP_STORE,
                    # MAC_CATALYST_APP_DIRECT
                },
                'relationships': {
                    'bundleId': {
                        'data': {'id': bundle_id, 'type': 'bundleIds'}
                    },
                    'certificates': {
                        'data': [
                            {'id': certificate_id, 'type': 'certificates'} for certificate_id in certificate_id_list
                        ]
                    },
                    'devices': {
                        'data': [
                            {'id': device_id, 'type': 'devices'} for device_id in device_id_list
                        ]
                    },
                }
            }
        }
        return request_format_log(
            requests.post(self.profiles_url, json=json, headers=self.headers, proxies=self.proxies,
                          timeout=self.timeout))

    def delete_profile(self, profile_id):
        """
        :param profile_id:
        :return:
            204	No Content
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            404 ErrorResponse Not Found Resource not found. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        base_url = '%s/%s' % (self.profiles_url, profile_id)
        json = {}
        return request_format_log(
            requests.delete(base_url, json=json, headers=self.headers, proxies=self.proxies, timeout=self.timeout))

    def download_profile(self, profile_id):
        # n=base64.b64decode(profileContent)
        # with open('profilea','wb') as f:
        #     f.write(n)
        # print(n)
        pass

    def list_profiles(self, query_parameters=None):
        """

        :param query_parameters:
        :return:
            200 ProfilesResponse OK Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json

        """
        params = {
            "limit": 200
        }
        if query_parameters:
            for k, v in query_parameters.items():
                params[k] = v
        return request_format_log(
            requests.get(self.profiles_url, params=params, headers=self.headers, proxies=self.proxies,
                         timeout=self.timeout))

    def list_profile_by_profile_id(self, profile_id):
        return self.list_profiles({"filter[id]": profile_id, "include": ""})

    def list_profile_by_profile_name(self, profile_name):
        return self.list_profiles({"filter[name]": profile_name, "include": ""})


class CertificatesAPI(object):
    # https://developer.apple.com/documentation/appstoreconnectapi/certificates
    def __init__(self, base_uri, jwt_headers):
        self.headers = jwt_headers
        self.certificates_url = '%s/certificates' % base_uri

    def create_certificate(self, csr_content, certificate_type='IOS_DISTRIBUTION'):
        """
        :param csr_content:
        :param certificate_type:
        :return:
            201 CertificateResponse Created Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        json = {
            'data': {
                'type': 'certificates',
                'attributes': {
                    'csrContent': csr_content,
                    'certificateType': certificate_type,
                    # https://developer.apple.com/documentation/appstoreconnectapi/certificatetype
                }
            }
        }
        return request_format_log(
            requests.post(self.certificates_url, json=json, headers=self.headers, proxies=self.proxies,
                          timeout=self.timeout))

    def download_certificate(self, certificate_id):
        # req.json()['data'][0]['attributes']['certificateContent']
        # n=base64.b64decode(certificateContent)
        # with open('xxxxxx','wb') as f:
        #     f.write(n)
        # print(n)
        pass

    def list_certificate(self, query_parameters=None):
        """
        :param query_parameters:
        :return:
            200 CertificatesResponse  OK  Content-Type: application/json
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
        """
        params = {
            "fields[certificates]": "certificateContent, certificateType, csrContent, displayName, expirationDate, "
                                    "name, platform, serialNumber",
        }
        if query_parameters:
            for k, v in query_parameters.items():
                params[k] = v
        return request_format_log(
            requests.get(self.certificates_url, params=params, headers=self.headers, proxies=self.proxies,
                         timeout=self.timeout))

    def list_certificate_by_certificate_id(self, certificate_id):
        return self.list_certificate({"filter[id]": certificate_id, })

    def revoke_certificate(self, certificate_id):
        """
        :param certificate_id:
        :return:
            204	No Content
            400 ErrorResponse Bad Request An error occurred with your request. Content-Type: application/json
            403 ErrorResponse Forbidden Request not authorized. Content-Type: application/json
            404 ErrorResponse Not Found Resource not found. Content-Type: application/json
            409 ErrorResponse Conflict The provided resource data is not valid. Content-Type: application/json
        """
        base_url = '%s/%s' % (self.certificates_url, certificate_id)
        json = {}
        return request_format_log(
            requests.delete(base_url, json=json, headers=self.headers, proxies=self.proxies, timeout=self.timeout))


class BaseInfoObj(object):
    @staticmethod
    def filter(obj_lists, query_parameters=None):
        if not isinstance(obj_lists, list):
            obj_lists = [obj_lists]
        if query_parameters:
            new_obj_lists = []
            for obj in obj_lists:
                flag = True
                for k, v in query_parameters.items():
                    if getattr(obj, k) != v:
                        flag = False
                        continue
                if flag:
                    new_obj_lists.append(obj)
            return new_obj_lists
        return obj_lists

    @staticmethod
    def update(obj_lists, up_obj_list):
        conn_obj = []
        conn_obj.extend(obj_lists)
        if not isinstance(up_obj_list, list):
            up_obj_list = [up_obj_list]
        conn_obj.extend(up_obj_list)
        repeat_id = []
        repeat_obj = []
        for i in range(len(conn_obj) - 1):
            for j in range(i + 1, len(conn_obj)):
                if conn_obj[i].id == conn_obj[j].id:
                    repeat_obj.append(conn_obj[j])
                    repeat_id.append(conn_obj[i].id)
        new_list = []
        for ob in conn_obj:
            if ob.id in repeat_id:
                continue
            new_list.append(ob)
        new_list.extend(repeat_obj)
        return new_list

    @staticmethod
    def delete(obj_lists, up_obj_list):
        new_obj_list = []
        for obj in obj_lists:
            flag = True
            for up_obj in up_obj_list:
                if obj.id == up_obj.id:
                    flag = False
            if flag:
                new_obj_list.append(obj)
        return new_obj_list


class Devices(namedtuple("Devices", ["id", "addedDate", "name", "deviceClass", "model", "udid", "platform", "status"])):

    @classmethod
    def from_json_list(cls, json_list):
        new_cls_list = []
        for json in json_list:
            new_cls_list.append(cls.from_json(json))
        return new_cls_list

    @classmethod
    def from_json(cls, json):
        new_dict = {'id': json.get('id', '')}
        attributes = json.get("attributes", {})
        for k, v in attributes.items():
            new_dict[k] = v
        return cls(**new_dict)

    def copy_and_replace(self, **kwargs):
        return self._replace(**kwargs)


class BundleIds(namedtuple("BundleIds", ["id", "name", "identifier", "platform", "seedId", ]), ):
    @classmethod
    def from_json_list(cls, json_list):
        new_cls_list = []
        for json in json_list:
            new_cls_list.append(cls.from_json(json))
        return new_cls_list

    @classmethod
    def from_json(cls, json):
        new_dict = {'id': json.get('id', '')}
        attributes = json.get("attributes", {})
        for k, v in attributes.items():
            new_dict[k] = v
        return cls(**new_dict)

    def copy_and_replace(self, **kwargs):
        return self._replace(**kwargs)


class Profiles(namedtuple("Profiles",
                          ["id", "name", "profileState", "createdDate", "profileType", "profileContent", "uuid",
                           "platform",
                           "expirationDate"]), ):
    @classmethod
    def from_json_list(cls, json_list):
        new_cls_list = []
        for json in json_list:
            new_cls_list.append(cls.from_json(json))
        return new_cls_list

    @classmethod
    def from_json(cls, json):
        new_dict = {'id': json.get('id', '')}
        attributes = json.get("attributes", {})
        for k, v in attributes.items():
            new_dict[k] = v
        return cls(**new_dict)

    def copy_and_replace(self, **kwargs):
        return self._replace(**kwargs)

    def download_profile(self, filepath):
        dirname = os.path.dirname(filepath)
        if os.path.isdir(dirname) and os.path.exists(dirname):
            pass
        else:
            os.makedirs(dirname)
        n = base64.b64decode(self.profileContent)
        with open(filepath, 'wb') as f:
            f.write(n)
        return filepath


class Certificates(namedtuple("Certificates",
                              ["id", "serialNumber", "certificateContent", "displayName", "name", "csrContent",
                               "platform",
                               "expirationDate",
                               "certificateType"]), ):
    @classmethod
    def from_json_list(cls, json_list):
        new_cls_list = []
        for json in json_list:
            new_cls_list.append(cls.from_json(json))
        return new_cls_list

    @classmethod
    def from_json(cls, json):
        new_dict = {'id': json.get('id', '')}
        attributes = json.get("attributes", {})
        for k, v in attributes.items():
            new_dict[k] = v
        return cls(**new_dict)

    def copy_and_replace(self, **kwargs):
        return self._replace(**kwargs)

    def download_certificate(self, filepath):
        dirname = os.path.dirname(filepath)
        if os.path.isdir(dirname) and os.path.exists(dirname):
            pass
        else:
            os.makedirs(dirname)
        n = base64.b64decode(self.certificateContent)
        with open(filepath, 'wb') as f:
            f.write(n)
        return filepath


def call_function_try_attempts(try_attempts=5, sleep_time=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            flag = False
            res = ''
            for i in range(try_attempts):
                try:
                    res = func(*args, **kwargs)
                    flag = True
                    break
                except Exception as e:
                    if 'Cannot connect to proxy' in str(e) or 'Read timed out' in str(
                            e) or 'Max retries exceeded with' in str(e):
                        logger.error('access apple api failed . change proxy ip again')
                        get_proxy_ip_from_cache(True)
                    logger.warning(
                        f'exec {func} failed. Failed:{e} {try_attempts} times in total. now {sleep_time} later try '
                        f'again...{i}')
                    res = str(e)
                    if 'Authentication credentials are missing or invalid' in str(e):
                        raise Exception(res)
                    time.sleep(sleep_time)
            logger.info(f"exec {func} finished. time:{time.time() - start_time}")
            if not flag:
                logger.error(f'exec {func} failed after the maximum number of attempts. Failed:{res}')
                raise Exception(res)
            return res

        return wrapper

    return decorator


class AppStoreConnectApi(DevicesAPI, BundleIDsAPI, BundleIDsCapabilityAPI, ProfilesAPI, CertificatesAPI):
    BASE_URI = 'https://api.appstoreconnect.apple.com/v1'
    JWT_AUD = 'appstoreconnect-v1'
    JWT_ALG = 'ES256'

    def __init__(self, issuer_id, private_key_id, p8_private_key, exp_seconds=1200):
        """
        根据 Apple 文档，会话最长持续时间为 20 分钟：https : //developer.apple.com/documentation/appstoreconnectapi/generating_tokens_for_api_requests
        :param issuer_id:
        :param private_key_id:
        :param p8_private_key:
        :param exp_seconds: max 20*60
        """
        self.issuer_id = issuer_id
        self.private_key_id = private_key_id
        self.p8_private_key = p8_private_key
        self.exp_seconds = exp_seconds
        self.proxies = get_proxy_ip_from_cache()
        self.timeout = settings.APPLE_DEVELOPER_API_TIMEOUT if settings.APPLE_DEVELOPER_API_TIMEOUT else 120
        self.__make_jwt_headers()
        DevicesAPI.__init__(self, self.BASE_URI, self.headers)
        BundleIDsAPI.__init__(self, self.BASE_URI, self.headers)
        BundleIDsCapabilityAPI.__init__(self, self.BASE_URI, self.headers)
        ProfilesAPI.__init__(self, self.BASE_URI, self.headers)
        CertificatesAPI.__init__(self, self.BASE_URI, self.headers)
        self.rate_limit_info = {}

    def __set_rate_limit_info(self, req_headers):
        for par in req_headers.get('X-Rate-Limit').split(";"):
            if par:
                limit_info_list = par.split(":")
                self.rate_limit_info[limit_info_list[0]] = limit_info_list[1]
        user_rem_info = self.rate_limit_info
        if int(user_rem_info.get('user-hour-rem')) < 3595:
            logger.warning(f"user-hour-rem over limit. so get jwt headers")
            self.__init__(self.issuer_id, self.private_key_id, self.p8_private_key)
            self.rate_limit_info = user_rem_info
        logger.info(f"rate_limit_info:{self.rate_limit_info}")

    def __make_jwt_headers(self):
        data = {
            "iss": self.issuer_id,
            "iat": int(time.time()),
            "exp": int(time.time()) + self.exp_seconds,
            "aud": self.JWT_AUD,
        }
        jwt_headers = {
            "alg": self.JWT_ALG,
            "kid": self.private_key_id,
            "typ": "JWT"
        }
        jwt_encoded = jwt.encode(data, self.p8_private_key, algorithm=self.JWT_ALG, headers=jwt_headers)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.39 (KHTML, like Gecko) '
                          'Chrome/72.0.3626.109 Safari/537.39',
            'Authorization': 'Bearer %s' % jwt_encoded
        }
        self.headers = headers

    def __base_format(self, s_type, req, success_code):
        # self.__set_rate_limit_info(req.headers)
        if req.status_code == success_code:
            req_data = req.json()
            data = req_data.get('data')
            if isinstance(data, list) or isinstance(data, dict):
                obj = None
                if isinstance(data, dict):
                    data = [data]
                if s_type == 'devices':
                    obj = Devices.from_json_list(data)
                elif s_type == 'bundleIds':
                    obj = BundleIds.from_json_list(data)
                elif s_type == 'profiles':
                    obj = Profiles.from_json_list(data)
                elif s_type == 'certificates':
                    obj = Certificates.from_json_list(data)
                if len(obj) == 1:
                    return obj[0]
                return obj
            else:
                # self.__init_jwt_headers()
                raise Exception(f'error instance: {req.text}')
        elif req.status_code == 401:  # 授权问题
            raise Exception(req.text)
        elif req.status_code == 429:  # 请求超过每小时限制 {'user-hour-lim': '3600', 'user-hour-rem': '3586'}
            raise Exception(req.text)
        elif req.status_code == 500:
            time.sleep(60)
            raise Exception(req.text)
        else:
            raise Exception('unknown error: %s  code:%s' % (req.text, req.status_code))

    def __device_store(self, req, success_code=200):
        return self.__base_format('devices', req, success_code)

    def __profile_store(self, req, success_code=200):
        return self.__base_format('profiles', req, success_code)

    def __certificates_store(self, req, success_code=200):
        return self.__base_format('certificates', req, success_code)

    def __bundle_ids_store(self, req, success_code=200):
        return self.__base_format('bundleIds', req, success_code)

    @call_function_try_attempts()
    def get_all_devices(self):
        req = self.list_devices()
        return self.__device_store(req)

    def list_enabled_devices(self):
        req = super().list_enabled_devices()
        return self.__device_store(req)

    def get_all_bundle_ids(self):
        req = self.list_bundle_ids()
        return self.__bundle_ids_store(req)

    def get_all_profiles(self):
        req = self.list_profiles()
        return self.__profile_store(req)

    @call_function_try_attempts()
    def get_all_certificates(self):
        req = self.list_certificate()
        return self.__certificates_store(req)

    @call_function_try_attempts()
    def get_certificate_by_cid(self, certificate_id):
        req = self.list_certificate_by_certificate_id(certificate_id)
        return self.__certificates_store(req)

    def list_device_by_udid(self, udid):
        device_obj_list = BaseInfoObj.filter(self.get_all_devices(), {"udid": udid})
        if not device_obj_list:
            raise Exception('Device obj is None')
        if len(device_obj_list) != 1 and len(set([device_obj.udid for device_obj in device_obj_list])) != 1:
            raise Exception('more than one Device obj')
        return device_obj_list

    @call_function_try_attempts()
    def register_device(self, device_name, device_udid, platform="IOS"):
        device_obj_list = BaseInfoObj.filter(self.get_all_devices(), {"udid": device_udid})
        # 发现同一个开发者账户里面有两个一样的udid，奇了怪
        if device_obj_list and (
                len(device_obj_list) == 1 or len(set([device_obj.udid for device_obj in device_obj_list])) == 1):
            device_obj = device_obj_list[0]
            req = self.modify_registered_device(device_obj.id, device_name, 'ENABLED')
            return self.__device_store(req)
        else:
            req = super().register_device(device_name, device_udid, platform)
            return self.__device_store(req, 201)

    @call_function_try_attempts()
    def enabled_device(self, device_id, device_name, udid):
        if device_id and device_name:
            req = super().enabled_device(device_id, device_name)
            if req.status_code == 200:
                return self.__device_store(req)
        if udid:
            device_obj_list = self.list_device_by_udid(udid)
            for device_obj in device_obj_list:
                req = self.modify_registered_device(device_obj.id, device_obj.name, 'ENABLED')
                return self.__device_store(req)

    @call_function_try_attempts()
    def disabled_device(self, device_id, device_name, udid):
        if device_id and device_name:
            req = super().disabled_device(device_id, device_name)
            if req.status_code == 200:
                return self.__device_store(req)
        if udid:
            device_obj_list = self.list_device_by_udid(udid)
            for device_obj in device_obj_list:
                req = self.modify_registered_device(device_obj.id, device_obj.name, 'DISABLED')
                return self.__device_store(req)

    def list_bundle_ids_by_identifier(self, identifier):
        req = super().list_bundle_id_by_identifier(identifier)
        return self.__bundle_ids_store(req)

    def __do_success(self, req, status=200):
        if req.status_code == status:
            return True
        return False

    @call_function_try_attempts()
    def enable_capability_by_s_type(self, bundle_id, s_type):
        capability_list = get_capability(s_type)
        if capability_list:
            for capability in capability_list:
                req = super().enable_capability(bundle_id, capability)
                if self.__do_success(req, 201):
                    logger.info(f"{bundle_id} enable_capability {capability} success")
                else:
                    logger.warning(f"{bundle_id} enable_capability {capability} failed {req.content}")
        return True

    @call_function_try_attempts()
    def disable_capability_by_s_type(self, bundle_id, s_type=len(capability_info) - 1):
        capability_list = get_capability(s_type)
        if capability_list:
            for capability in capability_list:
                req = super().disable_capability(bundle_id, capability)
                if self.__do_success(req, 204):
                    logger.info(f"{bundle_id} enable_capability {capability} success")
                else:
                    logger.warning(f"{bundle_id} enable_capability {capability} failed {req.content}")
        return True

    def enable_push_vpn_capability(self, bundle_id):
        req = super().enable_capability(bundle_id, 'PUSH_NOTIFICATIONS')
        if self.__do_success(req, 201):
            req = super().enable_capability(bundle_id, 'PERSONAL_VPN')
            if self.__do_success(req, 201):
                return True
        return False

    def disable_push_vpn_capability(self, bundle_id):
        req = super().disable_capability(bundle_id, 'PUSH_NOTIFICATIONS')
        if self.__do_success(req, 204):
            req = super().disable_capability(bundle_id, 'PERSONAL_VPN')
            if self.__do_success(req, 204):
                return True
        return False

    @call_function_try_attempts()
    def register_bundle_id(self, bundle_id_name, bundle_id_identifier, platform="IOS", seed_id=''):
        identifier_obj = self.list_bundle_ids_by_identifier(bundle_id_identifier)
        if isinstance(identifier_obj, BundleIds):
            req = self.modify_bundle_id(identifier_obj.id, bundle_id_name)
            return self.__bundle_ids_store(req)
        else:
            req = super().register_bundle_id(bundle_id_name, bundle_id_identifier, platform, seed_id)
            return self.__bundle_ids_store(req, 201)

    @call_function_try_attempts()
    def register_bundle_id_enable_capability(self, bundle_id_name, bundle_id_identifier, s_type, platform="IOS",
                                             seed_id=''):
        bundle_ids = self.register_bundle_id(bundle_id_name, bundle_id_identifier, platform, seed_id)
        if isinstance(bundle_ids, BundleIds):
            if self.enable_capability_by_s_type(bundle_ids.id, s_type):
                return bundle_ids

    @call_function_try_attempts()
    def delete_bundle_by_identifier(self, identifier_id, identifier_name):
        if identifier_id:
            req = self.delete_bundle_id_by_id(identifier_id)
            if req.status_code == 204:
                return True
        identifier_obj = self.list_bundle_ids_by_identifier(identifier_name)
        if isinstance(identifier_obj, BundleIds):
            req = self.delete_bundle_id_by_id(identifier_obj.id)
            if req.status_code == 204:
                return True

    @call_function_try_attempts()
    def create_profile(self, profile_id, bundle_id, certificate_id, profile_name, device_id_list=None,
                       profile_type='IOS_APP_ADHOC'):
        if device_id_list is None:
            device_id_list = []
        if not device_id_list:
            device_id_list = [device.id for device in self.list_enabled_devices()]

        self.delete_profile_by_id(profile_id, profile_name)
        # profile_obj = self.list_profile_by_profile_name(profile_name)
        # if isinstance(profile_obj, Profiles):
        #     self.delete_profile_by_id(profile_obj.id, profile_name)

        req = super().create_profile(bundle_id, [certificate_id], profile_name, device_id_list)
        if req.status_code == 201:
            self.__profile_store(req, 201)
            return Profiles.from_json(req.json().get("data"))
        raise KeyError(req.text)

    def list_profile_by_profile_name(self, profile_name):
        req = super().list_profile_by_profile_name(profile_name)
        return self.__profile_store(req)

    @call_function_try_attempts()
    def delete_profile_by_id(self, profile_id, profile_name):
        if profile_id:
            req = super().delete_profile(profile_id)
            if self.__do_success(req, 204):
                return True
        profile_obj = self.list_profile_by_profile_name(profile_name)
        if profile_obj:
            req = super().delete_profile(profile_obj.id)
            if self.__do_success(req, 204):
                return True

    @call_function_try_attempts()
    def create_certificate(self, csr_content, certificate_type='IOS_DISTRIBUTION'):
        req = super().create_certificate(csr_content, certificate_type)
        if req.status_code == 201:
            return self.__certificates_store(req, 201)
        raise KeyError(req.text)

    @call_function_try_attempts()
    def revoke_certificate(self, certificate_id):
        req = super().revoke_certificate(certificate_id)
        if req.status_code == 204:
            return True
        return False
