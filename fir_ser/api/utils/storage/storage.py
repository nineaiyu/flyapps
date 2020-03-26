#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/23

from api.models import AppStorage, UserInfo
from .aliyunApi import AliYunOss
from .qiniuApi import QiNiuOss
from .localApi import LocalStorage
import json
from fir_ser import settings


class Storage(object):
    def __init__(self, user):
        self.storage = self.get_storage(user)

    def get_upload_token(self, filename, expires=600):
        if self.storage:
            return self.storage.get_upload_token(filename, expires)

    def get_download_url(self, filename, expires=600,ftype=None):
        if self.storage:
            return self.storage.get_download_url(filename, expires,ftype)

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
            storage_type = self.storage_obj.storage_type
            if storage_type == 1:
                new_storage_obj = QiNiuOss(**auth)
            elif storage_type == 2:
                new_storage_obj = AliYunOss(**auth)
            else:
                new_storage_obj = LocalStorage(**auth)
            return new_storage_obj
        else:
            return self.get_default_storage()

    def get_default_storage(self):
        admin_storage = UserInfo.objects.first().storage
        if admin_storage:
            return self.get_storage(UserInfo)
        else:
            storage_lists = settings.THIRD_PART_CONFIG.get('storage')
            for storage in storage_lists:
                if storage.get("active",None):
                    storage_type= storage.get('type',None)
                    auth = storage.get('auth',{})
                    if storage_type == 1:
                        new_storage_obj = QiNiuOss(**auth)
                    elif storage_type == 2:
                        new_storage_obj = AliYunOss(**auth)
                    else:
                        new_storage_obj = LocalStorage(**auth)
                    return new_storage_obj
        return None




    def get_storage_type(self):
        if self.storage_obj:
            return self.storage_obj.storage_type

    def get_storage_auth(self, storage_obj):
        auth_dict = {
            'access_key': storage_obj.access_key,
            'secret_key': storage_obj.secret_key,
            'bucket_name': storage_obj.bucket_name,
        }
        try:
            additionalparameters = json.loads(storage_obj.additionalparameters)
        except Exception as e:
            print(e)
            additionalparameters = {}
        return {**auth_dict, **additionalparameters}
