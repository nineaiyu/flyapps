#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/23

import logging
import time

from common.base.baseutils import get_dict_from_filter_fields
from common.base.magic import run_function_by_locker
from common.cache.storage import CloudStorageCache, LocalStorageCache, DownloadUrlCache
from common.core.sysconfig import Config
from common.libs.storage.aliyunApi import AliYunOss, AliYunCdn
from common.libs.storage.localApi import LocalStorage
from common.libs.storage.qiniuApi import QiNiuOss

logger = logging.getLogger(__name__)


def get_storage_auth(storage_obj):
    filter_fields = ['access_key', 'secret_key', 'bucket_name', 'domain_name', 'is_https', 'endpoint',
                     'sts_role_arn', 'cnd_auth_key', 'download_auth_type']
    return get_dict_from_filter_fields(filter_fields, storage_obj.__dict__)


@run_function_by_locker()
def get_oss_storage(user, assigned_storage_obj, use_default_storage, prefix):
    if use_default_storage:
        return get_storage_form_conf(user, prefix)
    if assigned_storage_obj:
        storage_obj = assigned_storage_obj
    else:
        storage_obj = user.storage

    if storage_obj:
        auth = get_storage_auth(storage_obj)
        storage_type = storage_obj.storage_type
        storage_cache = CloudStorageCache(auth, f'{user.uid}_{prefix}')
        storage_key, new_storage_obj = storage_cache.get_storage_key_and_cache()

        if new_storage_obj and not assigned_storage_obj:
            logger.info(f"user {user} get storage obj {storage_key} cache {new_storage_obj}")
            return new_storage_obj
        else:
            if storage_type == 1:
                new_storage_obj = QiNiuOss(**auth)
            elif storage_type == 2:
                new_storage_obj = AliYunOss(**auth)
            else:
                new_storage_obj = LocalStorage(**auth)
            logger.warning(f"user {user} make storage obj key:{storage_key} obj: {new_storage_obj}")
            new_storage_obj.storage_type = storage_type
            storage_cache.set_storage_cache(new_storage_obj, 600)
            return new_storage_obj
    else:
        logger.info(f"user {user} has not storage obj, so get default")
        # 不需要管理存储，直接从配置文件获取默认存储
        return get_storage_form_conf(user, prefix)


class Storage(object):
    def __init__(self, user, assigned_storage_obj=None, use_default_storage=False, prefix='default'):
        self.user = user
        self.prefix = prefix
        self.assigned_storage_obj = assigned_storage_obj
        self.use_default_storage = use_default_storage
        try:
            locker = {
                'locker_key': f"make_storage_cache_{user.uid}_{prefix}",
                "timeout": 60, "blocking_timeout": 6}
            self.storage = get_oss_storage(user, assigned_storage_obj, use_default_storage, prefix, locker=locker)
        except Exception as e:
            logger.error(f"get {user} storage failed Exception:{e}")
            self.storage = None

    def get_upload_token(self, filename, expires=900):
        if self.storage:
            return self.storage.get_upload_token(filename, expires)

    def get_download_url(self, filename, expires=900, key='', force_new=False):
        if self.storage:
            now = time.time()
            download_cache = DownloadUrlCache(key, filename)
            download_val = download_cache.get_storage_cache()
            if download_val and not force_new:
                if download_val.get("time") > now - 60:
                    return download_val.get("download_url")
            if self.storage.__dict__.get("download_auth_type", None) == 2:
                cdn_obj = AliYunCdn(self.storage.cnd_auth_key, self.storage.is_https, self.storage.domain_name)
                download_url = cdn_obj.get_cdn_download_token(filename, expires)
            else:
                download_url = self.storage.get_download_url(filename, expires, force_new=True)
            download_cache.set_storage_cache({"download_url": download_url, "time": now + expires}, expires)
            return download_url

    def delete_file(self, filename, app_type=None):
        if self.storage:
            if app_type is not None:
                if app_type == 0:
                    filename = filename + '.apk'
                else:
                    filename = filename + '.ipa'
            try:
                logger.warning(f"storage {self.storage} delete file  {filename}")
                return self.storage.del_file(filename)
            except Exception as e:
                logger.error(f"delete file {filename} failed  Exception {e}")

    def rename_file(self, old_filename, new_filename):
        if self.storage:
            try:
                return self.storage.rename_file(old_filename, new_filename)
            except Exception as e:
                logger.error(f"rename {old_filename} to {new_filename} failed  Exception {e}")

    def get_file_info(self, name):
        if self.storage:
            try:
                return self.storage.get_file_info(name)
            except Exception as e:
                logger.error(f"get file info {name} failed  Exception {e}")

    def upload_file(self, local_file_full_path):
        if self.storage:
            try:
                return self.storage.upload_file(local_file_full_path)
            except Exception as e:
                logger.error(f"oss upload  {local_file_full_path} failed  Exception {e}")

    def download_file(self, file_name, local_file_full_path):
        if self.storage:
            try:
                return self.storage.download_file(file_name, local_file_full_path)
            except Exception as e:
                logger.error(f"oss download  {local_file_full_path} failed  Exception {e}")

    def get_storage_type(self):
        if self.storage:
            return self.storage.storage_type

    def get_storage_uuid(self):
        if self.storage:
            if self.storage.storage_type == 1:
                return self.storage.access_key
            elif self.storage.storage_type == 2:
                return self.storage.access_key_id
            else:
                return self.storage.domain_name
        return id(self)


def get_local_storage(clean_cache=False):
    for storage in Config.STORAGE:
        storage_type = storage.get('type', None)
        if storage_type == 0:
            auth = storage.get('auth', {})
            storage_cache = LocalStorageCache(auth, "_system_")
            storage_key, new_storage_obj = storage_cache.get_storage_key_and_cache()
            if clean_cache:
                logger.info(f"system clean local storage obj cache storage_key {storage_key}")
                storage_cache.del_storage_cache()
            if new_storage_obj:
                logger.info(f"system get local storage obj cache {new_storage_obj}")
                return new_storage_obj
            else:
                new_storage_obj = LocalStorage(**auth)
                new_storage_obj.storage_type = 3
                storage_cache.set_storage_cache(new_storage_obj, 600)
                logger.info(f"system get local storage obj, from settings  storage {new_storage_obj}")
                return new_storage_obj


def get_storage_form_conf(user, prefix):
    for storage in Config.STORAGE:
        if storage.get("active", None):
            storage_type = storage.get('type', None)
            auth = storage.get('auth', {})
            storage_cache = CloudStorageCache(auth, f'system_{prefix}')
            storage_key, new_storage_obj = storage_cache.get_storage_key_and_cache()
            if new_storage_obj:
                logger.info(f"user {user} get default storage {storage_key} obj cache {new_storage_obj} ")
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
                storage_cache.set_storage_cache(new_storage_obj, 600)
                logger.warning(
                    f"user {user} has not storage obj, from settings  get default storage key:{storage_key} obj:{new_storage_obj}")
                return new_storage_obj
    return None
