#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/18
'''
本地存储api
'''
from api.utils.TokenManager import DownloadToken
from fir_ser import settings
import os

class LocalStorage(object):
    def __init__(self,**kwargs):
        self.domain_name = kwargs.get('domain_name')

    def get_upload_token(self,name,expires):
        dtoken = DownloadToken()
        return dtoken.make_token(name,expires)

    def get_download_url(self,name,expires=1800,ftype=None):
        dtoken = DownloadToken()
        base_url = '/'.join([self.domain_name,'download', name])
        download_url = base_url + "?token=" + dtoken.make_token(name,expires)
        if ftype:
            download_url = download_url + '&ftype=' + ftype
        return download_url

    def del_file(self,name):
        try:
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
            return True
        except Exception as e:
            print(e)
            return False

