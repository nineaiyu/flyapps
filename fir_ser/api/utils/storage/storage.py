#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/23

from api.models import UserInfo
from .aliyunApi import AliYunOss, AliYunCdn
from .qiniuApi import QiNiuOss
from .localApi import LocalStorage
import json, time, base64
from api.utils.baseutils import get_dict_from_filter_fields
from fir_ser.settings import THIRD_PART_CONFIG, CACHE_KEY_TEMPLATE
from django.core.cache import cache
import logging

logger = logging.getLogger(__file__)


class Storage(object):
    def __init__(self, user, storage_obj=None, use_default_storage=False):
        try:
            self.storage = self.get_storage(user, storage_obj, use_default_storage)
        except Exception as e:
            logger.error("get %s storage failed Exception:%s" % (user, e))
            self.storage = None

    def get_upload_token(self, filename, expires=900):
        if self.storage:
            return self.storage.get_upload_token(filename, expires)

    def get_download_url(self, filename, expires=900, key='', force_new=False):
        if self.storage:
            now = time.time()
            down_key = "_".join([key.lower(), CACHE_KEY_TEMPLATE.get('download_url_key'), filename])
            download_val = cache.get(down_key)
            if download_val and not force_new:
                if download_val.get("time") > now - 60:
                    return download_val.get("download_url")
            if self.storage.__dict__.get("download_auth_type", None) == 2:
                cdn_obj = AliYunCdn(self.storage.cnd_auth_key, self.storage.is_https, self.storage.domain_name)
                download_url = cdn_obj.get_cdn_download_token(filename, expires)
            else:
                download_url = self.storage.get_download_url(filename, expires, force_new=True)
            cache.set(down_key, {"download_url": download_url, "time": now + expires}, expires)
            return download_url

    def delete_file(self, filename, apptype=None):
        if self.storage:
            if apptype is not None:
                if apptype == 0:
                    filename = filename + '.apk'
                else:
                    filename = filename + '.ipa'
            try:
                logger.info("storage %s delete file  %s" % (self.storage, filename))
                return self.storage.del_file(filename)
            except Exception as e:
                logger.error("delete file  %s  failed  Exception %s" % (filename, e))

    def rename_file(self, oldfilename, newfilename):
        if self.storage:
            try:
                return self.storage.rename_file(oldfilename, newfilename)
            except Exception as e:
                logger.error("rename %s to %s failed  Exception %s" % (oldfilename, newfilename, e))

    def upload_file(self, local_file_full_path):
        if self.storage:
            try:
                return self.storage.upload_file(local_file_full_path)
            except Exception as e:
                logger.error("oss upload  %s failed  Exception %s" % (local_file_full_path, e))

    def download_file(self, file_name, local_file_full_path):
        if self.storage:
            try:
                return self.storage.download_file(file_name, local_file_full_path)
            except Exception as e:
                logger.error("oss download  %s failed  Exception %s" % (local_file_full_path, e))

    def get_storage(self, user, storage_obj, use_default_storage):
        if storage_obj:
            self.storage_obj = storage_obj
        else:
            self.storage_obj = user.storage
        if use_default_storage:
            self.storage_obj = None

        if self.storage_obj:
            auth = self.get_storage_auth()
            storage_key = "_".join([CACHE_KEY_TEMPLATE.get('user_storage_key'), user.uid,
                                    base64.b64encode(json.dumps(auth).encode("utf-8")).decode("utf-8")[0:64]])
            storage_type = self.storage_obj.storage_type
            new_storage_obj = cache.get(storage_key)
            if new_storage_obj and not storage_obj:
                logger.info("user %s get storage obj cache %s" % (user, new_storage_obj))
                return new_storage_obj
            else:
                if storage_type == 1:
                    new_storage_obj = QiNiuOss(**auth)
                elif storage_type == 2:
                    new_storage_obj = AliYunOss(**auth)
                else:
                    new_storage_obj = LocalStorage(**auth)
                logger.warning("user %s make storage obj %s" % (user, new_storage_obj))
                new_storage_obj.storage_type = storage_type
                cache.set(storage_key, new_storage_obj, 600)
                return new_storage_obj
        else:
            logger.info("user %s has not storage obj, so get default" % user)
            return self.get_default_storage(user, storage_obj, False)

    def get_default_storage(self, user, storage_obj, use_default_storage):
        admin_obj = UserInfo.objects.filter(is_superuser=True).order_by('pk').first()
        if admin_obj and admin_obj.storage:
            logger.info("user %s has not storage obj, from admin "
                        "get default storage" % user)
            return self.get_storage(admin_obj, storage_obj, use_default_storage)
        else:
            storage_lists = THIRD_PART_CONFIG.get('storage')
            for storage in storage_lists:
                if storage.get("active", None):
                    storage_type = storage.get('type', None)
                    auth = storage.get('auth', {})
                    storage_key = "_".join([CACHE_KEY_TEMPLATE.get('user_storage_key'), 'default',
                                            base64.b64encode(json.dumps(auth).encode("utf-8")).decode("utf-8")[0:64]])
                    new_storage_obj = cache.get(storage_key)
                    if new_storage_obj:
                        logger.info("user %s get default storage obj cache %s" % (user, new_storage_obj))
                        return new_storage_obj
                    else:
                        if storage_type == 1:
                            new_storage_obj = QiNiuOss(**auth)
                            new_storage_obj.storage_type = 1
                        elif storage_type == 2:
                            new_storage_obj = AliYunOss(**auth)
                            new_storage_obj.storage_type = 2
                        else:
                            new_storage_obj = LocalStorage(**auth)
                            new_storage_obj.storage_type = 3
                        cache.set(storage_key, new_storage_obj, 600)
                        logger.warning("user %s has not storage obj, admin already has not storage obj, from settings "
                                       "get default storage %s" % (user, new_storage_obj))
                        return new_storage_obj
        return None

    def get_storage_type(self):
        if self.storage:
            return self.storage.storage_type

    def get_storage_auth(self):
        filter_fields = ['access_key', 'secret_key', 'bucket_name', 'domain_name', 'is_https', 'endpoint',
                         'sts_role_arn', 'cnd_auth_key', 'download_auth_type']
        return get_dict_from_filter_fields(filter_fields, self.storage_obj.__dict__)


def get_local_storage(clean_cache=False):
    storage_lists = THIRD_PART_CONFIG.get('storage')
    for storage in storage_lists:
        storage_type = storage.get('type', None)
        if storage_type == 0:
            auth = storage.get('auth', {})
            storage_key = "_".join(['local_storage_', CACHE_KEY_TEMPLATE.get('user_storage_key'), "_system_",
                                    base64.b64encode(json.dumps(auth).encode("utf-8")).decode("utf-8")[0:64]])
            if clean_cache:
                logger.info("system clean local storage obj cache storage_key %s" % storage_key)
                cache.delete(storage_key)
            new_storage_obj = cache.get(storage_key)
            if new_storage_obj:
                logger.info("system get local storage obj cache %s" % new_storage_obj)
                return new_storage_obj
            else:
                new_storage_obj = LocalStorage(**auth)
                new_storage_obj.storage_type = 3
                cache.set(storage_key, new_storage_obj, 600)
                logger.info("system get local storage obj, from settings "
                            "storage %s" % new_storage_obj)
                return new_storage_obj
