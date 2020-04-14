#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/23

from api.models import AppStorage, UserInfo
from .aliyunApi import AliYunOss
from .qiniuApi import QiNiuOss
from .localApi import LocalStorage
import json, time, base64
from fir_ser.settings import THIRD_PART_CONFIG, CACHE_KEY_TEMPLATE
from django.core.cache import cache


class Storage(object):
    def __init__(self, user):
        try:
            self.storage = self.get_storage(user)
        except Exception as e:
            self.storage=None

    def get_upload_token(self, filename, expires=900):
        if self.storage:
            return self.storage.get_upload_token(filename, expires)

    def get_download_url(self, filename, expires=900, ftype=None, key=''):
        if self.storage:
            now = time.time()
            down_key = "_".join([key.lower(), CACHE_KEY_TEMPLATE.get('download_url_key'), filename])
            download_val = cache.get(down_key)
            if download_val:
                if download_val.get("time") > now - 60:
                    return download_val.get("download_url")

            download_url = self.storage.get_download_url(filename, expires, ftype)
            cache.set(down_key, {"download_url": download_url, "time": now + expires}, expires)
            return download_url

    def delete_file(self, filename, apptype=None):
        if self.storage:
            if apptype is not None:
                if apptype == 0:
                    filename = filename + '.apk'
                else:
                    filename = filename + '.ipa'
            return self.storage.del_file(filename)

    def get_storage(self, user):
        self.storage_obj = user.storage
        if self.storage_obj:
            auth = self.get_storage_auth(self.storage_obj)
            storage_key = "_".join([CACHE_KEY_TEMPLATE.get('user_storage_key'),user.uid,
                                    base64.b64encode(json.dumps(auth).encode("utf-8")).decode("utf-8")[0:64]])
            storage_type = self.storage_obj.storage_type
            new_storage_obj = cache.get(storage_key)
            if new_storage_obj:
                return new_storage_obj
            else:
                if storage_type == 1:
                    new_storage_obj = QiNiuOss(**auth)
                elif storage_type == 2:
                    new_storage_obj = AliYunOss(**auth)
                else:
                    new_storage_obj = LocalStorage(**auth)

                new_storage_obj.storage_type = storage_type
                cache.set(storage_key, new_storage_obj, 600)
                return new_storage_obj
        else:
            return self.get_default_storage(user)

    def get_default_storage(self,user):
        admin_storage = UserInfo.objects.first().storage
        if admin_storage:
            return self.get_storage(UserInfo)
        else:
            storage_lists = THIRD_PART_CONFIG.get('storage')
            for storage in storage_lists:
                if storage.get("active", None):
                    storage_type = storage.get('type', None)
                    auth = storage.get('auth', {})
                    storage_key = "_".join([CACHE_KEY_TEMPLATE.get('user_storage_key'),user.uid,
                                            base64.b64encode(json.dumps(auth).encode("utf-8")).decode("utf-8")[0:64]])
                    new_storage_obj = cache.get(storage_key)
                    if new_storage_obj:
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
                        return new_storage_obj
        return None

    def get_storage_type(self):
        if self.storage:
            return self.storage.storage_type

    def get_storage_auth(self, storage_obj):
        auth_dict = {
            'access_key': storage_obj.access_key,
            'secret_key': storage_obj.secret_key,
            'bucket_name': storage_obj.bucket_name,
            'domain_name': storage_obj.domain_name,
            'is_https': storage_obj.is_https
        }
        try:
            additionalparameters = json.loads(storage_obj.additionalparameters)
        except Exception as e:
            print(e)
            additionalparameters = {}
        return {**auth_dict, **additionalparameters}
