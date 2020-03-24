#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/18
'''
主要是调用七牛云存储，处理七牛云存储的逻辑
'''
from qiniu import Auth
from qiniu import BucketManager

class QiNiuOss(object):
    def __init__(self,access_key,secret_key,bucket_name,domain_name):
        access_key=access_key or "mTqfvkLVSTVb2_1ERjDlFS_WAHLSkpDxYr4e4fiJ"
        secret_key=secret_key or "0G9fXfgmi8h1-bmEsABYkE6apf8IuwKpj3hYLynv"
        self.bucket_name = bucket_name or 'fir-storage'
        self.domain_name = domain_name or 'fly-cdn.dvcloud.xin'
        self.qiniu_obj = Auth(access_key,secret_key)

    def get_upload_token(self,name,expires=1800):
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
        # print(token)
        return token

    def get_download_url(self,name,expires=1800):
        #有两种方式构造base_url的形式
        base_url = '%s/%s' % (self.domain_name, name)
        #或者直接输入url的方式下载
        #可以设置token过期时间
        private_url = self.qiniu_obj.private_download_url(base_url, expires=expires)
        print(private_url)
        return private_url

    def del_file(self,name):
        # 初始化BucketManager
        bucket = BucketManager(self.qiniu_obj)
        # 删除bucket_name 中的文件 key
        ret, info = bucket.delete(self.bucket_name, name)
        print(info)
        return ret

