#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 12月 
# author: NinEveN
# date: 2021/12/22
import base64
import json
import logging

from django.core.cache import cache
from django.utils import timezone

from fir_ser.settings import CACHE_KEY_TEMPLATE

logger = logging.getLogger(__name__)


class RedisCacheBase(object):
    def __init__(self, cache_key):
        self.cache_key = cache_key

    def __getattribute__(self, item):
        if isinstance(item, str) and item != 'cache_key':
            if hasattr(self, "cache_key"):
                logger.debug(f'act:{item} cache_key:{super().__getattribute__("cache_key")}')
        return super().__getattribute__(item)

    def get_storage_cache(self):
        return cache.get(self.cache_key)

    def get_storage_key_and_cache(self):
        return self.cache_key, cache.get(self.cache_key)

    def set_storage_cache(self, value, timeout=600):
        return cache.set(self.cache_key, value, timeout)

    def del_storage_cache(self):
        return cache.delete(self.cache_key)

    def incr(self, amount=1):
        return cache.incr(self.cache_key, amount)

    def expire(self, timeout):
        return cache.expire(self.cache_key, timeout=timeout)

    def iter_keys(self):
        if not self.cache_key.endswith('*'):
            self.cache_key = f"{self.cache_key}*"
        return cache.iter_keys(self.cache_key)

    def get_many(self):
        return cache.get_many(self.cache_key)

    def del_many(self):
        for delete_key in cache.iter_keys(self.cache_key):
            cache.delete(delete_key)
        return True


class CloudStorageCache(RedisCacheBase):
    def __init__(self, auth, uid):
        if auth == '*':
            bid = auth
        else:
            bid = base64.b64encode(json.dumps(auth).encode("utf-8")).decode("utf-8")[0:64]
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('user_storage_key')}_{uid}_{bid}"

        super().__init__(self.cache_key)


class LocalStorageCache(RedisCacheBase):
    def __init__(self, auth, uid):
        bid = base64.b64encode(json.dumps(auth).encode("utf-8")).decode("utf-8")[0:64]
        self.cache_key = f"local_storage_{CACHE_KEY_TEMPLATE.get('user_storage_key')}_{uid}_{bid}"
        super().__init__(self.cache_key)


class DownloadUrlCache(RedisCacheBase):
    def __init__(self, key, filename):
        self.cache_key = f"{key.lower()}_{CACHE_KEY_TEMPLATE.get('download_url_key')}_{filename}"
        super().__init__(self.cache_key)


class UserTokenCache(RedisCacheBase):
    def __init__(self, key):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('user_auth_token_key')}_{key}"
        super().__init__(self.cache_key)


class IpProxyListCache(RedisCacheBase):
    def __init__(self):
        self.cache_key = CACHE_KEY_TEMPLATE.get("ip_proxy_store_list_key")
        super().__init__(self.cache_key)


class IpProxyActiveCache(RedisCacheBase):
    def __init__(self, issuer_id):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('ip_proxy_store_active_key')}_{issuer_id}"
        super().__init__(self.cache_key)


class TokenManagerCache(RedisCacheBase):
    def __init__(self, key, release_id):
        self.cache_key = f"{key.lower()}_{CACHE_KEY_TEMPLATE.get('make_token_key')}_{release_id}"
        super().__init__(self.cache_key)


class AdPicShowCache(RedisCacheBase):
    def __init__(self, key, short):
        self.cache_key = f"{key.lower()}_{CACHE_KEY_TEMPLATE.get('ad_pic_show_key')}_{short}"
        super().__init__(self.cache_key)


class TempCache(RedisCacheBase):
    def __init__(self, key, token):
        self.cache_key = base64.b64encode(f"{key}:{token}".encode("utf-8")).decode("utf-8")
        super().__init__(self.cache_key)


class WxTokenCache(RedisCacheBase):
    def __init__(self):
        self.cache_key = CACHE_KEY_TEMPLATE.get("wx_access_token_key")
        super().__init__(self.cache_key)


class WxTicketCache(RedisCacheBase):
    def __init__(self, ticket):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('wx_ticket_info_key')}_{ticket}"
        super().__init__(self.cache_key)


class AppInstanceCache(RedisCacheBase):
    def __init__(self, app_id):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('app_instance_key')}_{app_id}"
        super().__init__(self.cache_key)


class AppDownloadTimesCache(RedisCacheBase):
    def __init__(self, app_id):
        self.init_many_keys(app_id)
        super().__init__(self.cache_key)

    def init_many_keys(self, app_id):
        bmp_key = CACHE_KEY_TEMPLATE.get('download_times_key')
        if isinstance(app_id, list):
            self.cache_key = []
            for key in app_id:
                self.cache_key.append(f"{bmp_key}_{key}")
        else:
            self.cache_key = f"{bmp_key}_{app_id}"


class AppDownloadTodayTimesCache(RedisCacheBase):
    def __init__(self, app_id):
        self.init_many_keys(app_id)
        super().__init__(self.cache_key)

    def init_many_keys(self, app_id):
        now = timezone.now()
        tmp_key = CACHE_KEY_TEMPLATE.get("download_today_times_key")
        bmp_key = f"{tmp_key}_{now.year}_{now.month}_{now.day}"
        if isinstance(app_id, list):
            self.cache_key = []
            for key in app_id:
                self.cache_key.append(f"{bmp_key}_{key}")
        else:
            self.cache_key = f"{bmp_key}_{app_id}"


class AppDownloadShortCache(RedisCacheBase):
    def __init__(self, key, short):
        self.cache_key = f"{key.lower()}_{CACHE_KEY_TEMPLATE.get('download_short_key')}_{short}"
        super().__init__(self.cache_key)


class AppDownloadShortShowCache(RedisCacheBase):
    def __init__(self, key, short):
        self.cache_key = f"{key.lower()}_{CACHE_KEY_TEMPLATE.get('download_short_show_key')}_{short}"
        super().__init__(self.cache_key)


class UploadTmpFileNameCache(RedisCacheBase):
    def __init__(self, filename):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('upload_file_tmp_name_key')}_{filename}"
        super().__init__(self.cache_key)


class UserCanDownloadCache(RedisCacheBase):
    def __init__(self, user_id):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('user_can_download_key')}_{user_id}"
        super().__init__(self.cache_key)


class UserFreeDownloadTimesCache(RedisCacheBase):
    def __init__(self, user_id):
        now = timezone.now()
        tmp_key = CACHE_KEY_TEMPLATE.get('user_free_download_times_key')
        self.cache_key = f"{tmp_key}_{now.year}_{now.month}_{now.day}_{user_id} "
        super().__init__(self.cache_key)


class SignUdidQueueCache(RedisCacheBase):
    def __init__(self, prefix_key):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('ipa_sign_udid_queue_key')}_{prefix_key}"
        super().__init__(self.cache_key)


class SystemConfigCache(RedisCacheBase):
    def __init__(self, prefix_key):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('sysconfig_key')}_{prefix_key}"
        super().__init__(self.cache_key)


class TaskStateCache(RedisCacheBase):
    def __init__(self, app_pk, task_id):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('task_state_key')}_{app_pk}_{task_id}"
        super().__init__(self.cache_key)


class PendingStateCache(RedisCacheBase):
    def __init__(self, locker_key):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('pending_state_key')}_{locker_key}"
        super().__init__(self.cache_key)


class WxLoginBindCache(RedisCacheBase):
    def __init__(self, unique_key):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('wx_login_bind_key')}_{unique_key}"
        super().__init__(self.cache_key)


class NotifyLoopCache(RedisCacheBase):
    def __init__(self, uid, unique_key):
        self.cache_key = f"{CACHE_KEY_TEMPLATE.get('notify_loop_msg_key')}_{uid}_{unique_key}"
        super().__init__(self.cache_key)
