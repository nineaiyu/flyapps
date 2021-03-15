#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/18
'''
本地存储api
'''
from api.utils.TokenManager import DownloadToken
from api.utils.storage.aliyunApi import AliYunCdn
from fir_ser import settings
import os
import logging

logger = logging.getLogger(__file__)


class LocalStorage(object):
    def __init__(self, domain_name, is_https, download_auth_type=1, cnd_auth_key=None):
        self.domain_name = domain_name
        self.is_https = is_https
        self.download_auth_type = download_auth_type
        self.cnd_auth_key = cnd_auth_key

    def get_upload_token(self, name, expires):
        dtoken = DownloadToken()
        return dtoken.make_token(name, expires)

    def get_base_url(self):
        uri = 'http://'
        if self.is_https:
            uri = 'https://'
        return "%s%s" % (uri, self.domain_name)

    def get_download_url(self, name, expires=600, force_new=False):
        dtoken = DownloadToken()
        download_url = '/'.join([self.get_base_url(), 'download', name])
        if self.download_auth_type == 1:
            download_url = "%s?%s=%s" % (
                download_url, settings.DATA_DOWNLOAD_KEY, dtoken.make_token(name, expires, force_new=force_new))
        elif self.download_auth_type == 2:
            cdn_obj = AliYunCdn(self.cnd_auth_key, self.is_https, self.domain_name)
            download_url = cdn_obj.get_cdn_download_token(name, expires)
        elif self.download_auth_type == 0:
            pass
        return download_url

    def del_file(self, name):
        file = os.path.join(settings.MEDIA_ROOT, name)
        try:
            if os.path.isfile(file):
                os.remove(file)
            return True
        except Exception as e:
            logger.error("delete file %s failed Exception %s" % (file, e))
            return False

    def rename_file(self, oldfilename, newfilename):
        try:
            os.rename(os.path.join(settings.MEDIA_ROOT, oldfilename), os.path.join(settings.MEDIA_ROOT, newfilename))
            return True
        except Exception as e:
            logger.error("rename_file file %s to %s failed Exception %s" % (oldfilename, newfilename, e))
            return False

    def upload_file(self, local_file_full_path):
        if os.path.isfile(local_file_full_path):
            return True
        return False
