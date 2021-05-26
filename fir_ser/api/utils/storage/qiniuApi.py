#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/18
'''
主要是调用七牛云存储，处理七牛云存储的逻辑
'''
from qiniu import Auth, put_file, etag
from qiniu import BucketManager
import os, requests
import logging

logger = logging.getLogger(__file__)


class QiNiuOss(object):
    def __init__(self, access_key, secret_key, bucket_name, domain_name, is_https):
        access_key = access_key
        secret_key = secret_key
        self.bucket_name = bucket_name
        self.domain_name = domain_name
        self.is_https = is_https
        self.qiniu_obj = Auth(access_key, secret_key)

    def get_upload_token(self, name, expires=1800):
        # 生成上传 Token，可以指定过期时间等
        # 上传策略示例
        # https://developer.qiniu.com/kodo/manual/1206/put-policy
        policy = {
            # 'callbackUrl':'https://requestb.in/1c7q2d31',
            # 'callbackBody':'filename=$(fname)&filesize=$(fsize)'
            # 'persistentOps':'imageView2/1/w/200/h/200'
        }
        # 3600为token过期时间，秒为单位。3600等于一小时
        token = self.qiniu_obj.upload_token(self.bucket_name, name, expires, policy)
        return token

    def get_download_url(self, name, expires=1800, force_new=False):
        # 有两种方式构造base_url的形式
        uri = 'http://'
        if self.is_https:
            uri = 'https://'
        base_url = '%s%s/%s' % (uri, self.domain_name, name)
        # 或者直接输入url的方式下载
        # 可以设置token过期时间
        private_url = self.qiniu_obj.private_download_url(base_url, expires=expires)
        return private_url

    def del_file(self, name):
        # 初始化BucketManager
        bucket = BucketManager(self.qiniu_obj)
        # 删除bucket_name 中的文件 key
        ret, info = bucket.delete(self.bucket_name, name)
        return ret

    def rename_file(self, oldfilename, newfilename):
        bucket = BucketManager(self.qiniu_obj)
        ret, info = bucket.move(self.bucket_name, oldfilename, self.bucket_name, newfilename)
        return ret

    def upload_file(self, local_file_full_path):
        if os.path.isfile(local_file_full_path):
            filename = os.path.basename(local_file_full_path)
            token = self.get_upload_token(filename)
            ret, info = put_file(token, filename, local_file_full_path)
            if ret['key'] == filename and ret['hash'] == etag(local_file_full_path):
                return True

    def download_file(self, name, local_file_full_path):
        dir_path = os.path.dirname(local_file_full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        req = requests.get(self.get_download_url(name))
        if req.status_code != 200:
            logger.error("download  file %s failed %s" % (name, req.content))
            return False
        try:
            with open(local_file_full_path, "wb") as f:
                for chunk in req.iter_content(chunk_size=5120):
                    if chunk:
                        f.write(chunk)
            logger.info("save download  file %s success" % local_file_full_path)
            return True
        except Exception as e:
            logger.error("check download file and move file %s failed Exception %s" % (local_file_full_path, e))
            return False
