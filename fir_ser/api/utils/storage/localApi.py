#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/18
"""
本地存储api
"""
from api.utils.TokenManager import make_token
from api.utils.storage.aliyunApi import AliYunCdn
from fir_ser import settings
import os
import logging

logger = logging.getLogger(__name__)


class LocalStorage(object):
    def __init__(self, domain_name, is_https, download_auth_type=1, cnd_auth_key=None):
        self.domain_name = domain_name
        self.is_https = is_https
        self.download_auth_type = download_auth_type
        self.cnd_auth_key = cnd_auth_key

    @staticmethod
    def get_upload_token(name, expires):
        return make_token(name, expires)

    def get_base_url(self):
        uri = 'http://'
        if self.is_https:
            uri = 'https://'
        return f"{uri}{self.domain_name}"

    def get_download_url(self, name, expires=600, force_new=False):
        download_url = '/'.join([self.get_base_url(), 'download', name])
        if self.download_auth_type == 1:
            download_url = f"{download_url}?{settings.DATA_DOWNLOAD_KEY}={make_token(name, expires, force_new=force_new)}"
        elif self.download_auth_type == 2:
            cdn_obj = AliYunCdn(self.cnd_auth_key, self.is_https, self.domain_name)
            download_url = cdn_obj.get_cdn_download_token(name, expires)
        elif self.download_auth_type == 0:
            pass
        return download_url

    @staticmethod
    def del_file(name):
        file = os.path.join(settings.MEDIA_ROOT, name)
        try:
            if os.path.isfile(file):
                os.remove(file)
            return True
        except Exception as e:
            logger.error(f"delete file {file} failed Exception {e}")
            return False

    @staticmethod
    def rename_file(old_filename, new_filename):
        try:
            os.rename(os.path.join(settings.MEDIA_ROOT, old_filename), os.path.join(settings.MEDIA_ROOT, new_filename))
            return True
        except Exception as e:
            logger.error(f"rename_file file {old_filename} to {new_filename} failed Exception {e}")
            return False

    @staticmethod
    def upload_file(local_file_full_path):
        if os.path.isfile(local_file_full_path):
            return True
        return False
