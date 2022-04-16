#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/22

# pip install aliyun-python-sdk-sts oss2

import hashlib
import json
import logging
import os
import re
import time

import oss2
from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest
from oss2 import SizedFileAdapter, determine_part_size
from oss2.models import PartInfo

from api.utils.modelutils import get_filename_form_file

logger = logging.getLogger(__name__)


# 以下代码展示了STS的用法，包括角色扮演获取临时用户的密钥、使用临时用户的密钥访问OSS。

# STS入门教程请参看  https://yq.aliyun.com/articles/57895
# STS的官方文档请参看  https://help.aliyun.com/document_detail/28627.html

# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
# 注意：AccessKeyId、AccessKeySecret为子用户的密钥。
# 子用户需要有  调用STS服务AssumeRole接口的权限
# 创建ram用户，授权 管理对象存储服务（OSS）权限
# RoleArn可以在控制台的“访问控制  > RAM角色管理  > 创建的ram用户  > 基本信息  > Arn”上查看。
#
# 以杭州区域为例，Endpoint可以是：
#   http://oss-cn-hangzhou.aliyuncs.com
#   https://oss-cn-hangzhou.aliyuncs.com
# 分别以HTTP、HTTPS协议访问。

def md5sum(src):
    m = hashlib.md5()
    m.update(src)
    return m.hexdigest()


class AliYunCdn(object):
    def __init__(self, key, is_https, domain_name):
        uri = 'https://' if is_https else 'http://'
        self.domain = uri + domain_name
        self.key = key

    # 鉴权方式A
    def a_auth(self, uri, exp):
        p = re.compile("^(http://|https://)?([^/?]+)(/[^?]*)?(\\?.*)?$")
        if not p:
            return None
        m = p.match(uri)
        scheme, host, path, args = m.groups()
        if not scheme: scheme = "http://"
        if not path: path = "/"
        if not args: args = ""
        rand = "0"  # "0" by default, other value is ok
        uid = "0"  # "0" by default, other value is ok
        ss_string = f"{path}-{exp}-{rand}-{uid}-{self.key}"
        hash_value = md5sum(ss_string.encode("utf-8"))
        auth_key = f"{exp}-{rand}-{uid}-{hash_value}"
        if args:
            return f"{scheme}{host}{path}{args}&auth_key={auth_key}"
        else:
            return f"{scheme}{host}{path}{args}?auth_key={auth_key}"

    def get_cdn_download_token(self, filename, expires=1800):
        uri = f"{self.domain}/{filename}"
        exp = int(time.time()) + expires
        download_url = self.a_auth(uri, exp)
        logger.info(f"make cdn download url {download_url}")
        return download_url


class StsToken(object):
    """AssumeRole返回的临时用户密钥
    :param str access_key_id: 临时用户的access key id
    :param str access_key_secret: 临时用户的access key secret
    :param int expiration: 过期时间，UNIX时间，自1970年1月1日UTC零点的秒数
    :param str security_token: 临时用户Token
    :param str request_id: 请求ID
    """

    def __init__(self):
        self.access_key_id = ''
        self.access_key_secret = ''
        self.expiration = 3600
        self.security_token = ''
        self.request_id = ''
        self.bucket = ''
        self.endpoint = ''


class AliYunOss(object):

    def __init__(self, access_key, secret_key, bucket_name, endpoint, sts_role_arn, is_https, domain_name=None,
                 download_auth_type=1, cnd_auth_key=None):
        self.access_key_id = access_key
        self.access_key_secret = secret_key
        self.bucket_name = bucket_name
        self.endpoint = endpoint
        self.sts_role_arn = sts_role_arn
        self.region_id = '-'.join(self.endpoint.split('.')[0].split("-")[1:3])
        self.is_https = is_https
        self.download_auth_type = download_auth_type
        self.cnd_auth_key = cnd_auth_key
        self.domain_name = domain_name
        self.bucket_get = None
        self.bucket = None
        self.make_auth_bucket('init_get', 1800, True)
        self.make_auth_bucket('init_auth', 1800)

    def fetch_sts_token(self, name, expires, only_put=False, only_get=False):
        """子用户角色扮演获取临时用户的密钥
        :param only_put:  是否只允许上传
        :param only_get: 是否只允许下载
        :param expires: 过期时间
        :param name: obj name
        :return StsToken: 临时用户密钥
        """
        clt = client.AcsClient(self.access_key_id, self.access_key_secret, self.region_id)
        req = AssumeRoleRequest.AssumeRoleRequest()

        req.set_accept_format('json')
        req.set_RoleArn(self.sts_role_arn)
        req.set_RoleSessionName(name)
        req.set_DurationSeconds(expires)
        p_action = "oss:GetObject"
        if only_put:
            p_action = ["oss:PutObject", "oss:AbortMultipartUpload"]
        if only_get:
            p_action = "oss:GetObject"
            name = '*'

        if only_get or only_put:
            policy = {
                "Statement": [
                    {
                        "Action": p_action,
                        "Effect": "Allow",
                        "Resource": [f"acs:oss:*:*:{self.bucket_name}/{name}"]
                    }
                ],
                "Version": "1"
            }
            req.set_Policy(json.dumps(policy))
        body = clt.do_action_with_exception(req)
        j = json.loads(oss2.to_unicode(body))
        token = StsToken()
        token.access_key_id = j['Credentials']['AccessKeyId']
        token.access_key_secret = j['Credentials']['AccessKeySecret']
        token.security_token = j['Credentials']['SecurityToken']
        token.request_id = j['RequestId']
        token.expiration = oss2.utils.to_unixtime(j['Credentials']['Expiration'], '%Y-%m-%dT%H:%M:%SZ')
        token.bucket = self.bucket_name
        token.endpoint = self.endpoint.replace('-internal', '')
        logger.info(f"get aliyun sts token {token.__dict__}")
        return token

    def get_upload_token(self, name, expires=1800):
        return self.fetch_sts_token(name, expires, only_put=True).__dict__

    def make_auth_bucket(self, name, expires, only_get=False):
        uri = 'https://' if self.is_https else 'http://'
        url = self.endpoint
        is_cname = False
        if self.domain_name and self.download_auth_type == 1:
            url = self.domain_name
            is_cname = True
        token = self.fetch_sts_token(name, expires, only_get=only_get)
        auth = oss2.StsAuth(token.access_key_id, token.access_key_secret, token.security_token)
        if only_get:
            self.bucket_get = oss2.Bucket(auth, uri + url, self.bucket_name, is_cname=is_cname)
        else:
            self.bucket = oss2.Bucket(auth, uri + url, self.bucket_name, is_cname=is_cname)

    def get_download_url(self, name, expires=1800, force_new=False):
        private_url = self.bucket_get.sign_url('GET', name, expires)
        return private_url

    def del_file(self, name):
        # self.fetch_sts_token(name,expires=300)
        # auth = oss2.StsAuth(self.token.access_key_id, self.token.access_key_secret, self.token.security_token)
        # bucket = oss2.Bucket(auth, self.endpoint,self.bucket_name)
        return self.bucket.delete_object(name)

    def rename_file(self, old_filename, new_filename):
        self.bucket.copy_object(self.bucket_name, old_filename, new_filename)
        return self.del_file(old_filename)

    def upload_file(self, local_file_full_path):
        return self.multipart_upload_file(local_file_full_path)

        if os.path.isfile(local_file_full_path):
            filename = os.path.basename(local_file_full_path)
            headers = {
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Cache-Control': ''
            }
            self.bucket.put_object_from_file(filename, local_file_full_path, headers)
            # with open(local_file_full_path, 'rb') as fileobj:
            #     # Seek方法用于指定从第1000个字节位置开始读写。上传时会从您指定的第1000个字节位置开始上传，直到文件结束。
            #     fileobj.seek(1000, os.SEEK_SET)
            #     # Tell方法用于返回当前位置。
            #     # current = fileobj.tell()
            #     self.bucket.put_object(os.path.basename(local_file_full_path), fileobj)
            return True
        else:
            logger.error(f"file {local_file_full_path} is not file")

    def download_file(self, name, local_file_full_path):
        dir_path = os.path.dirname(local_file_full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return self.bucket.get_object_to_file(name, local_file_full_path)

    def multipart_upload_file(self, local_file_full_path):
        if os.path.isfile(local_file_full_path):
            total_size = os.path.getsize(local_file_full_path)
            # determine_part_size方法用于确定分片大小。
            part_size = determine_part_size(total_size, preferred_size=1024 * 1024 * 10)
            filename = os.path.basename(local_file_full_path)
            headers = {
                'Content-Disposition': 'attachment; filename="%s"' % get_filename_form_file(filename).encode(
                    "utf-8").decode("latin1"),
                'Cache-Control': ''
            }
            # 初始化分片。
            # 如需在初始化分片时设置文件存储类型，请在init_multipart_upload中设置相关headers，参考如下。
            # headers = dict()
            # headers["x-oss-storage-class"] = "Standard"
            upload_id = self.bucket.init_multipart_upload(filename, headers=headers).upload_id
            parts = []

            # 逐个上传分片。
            with open(local_file_full_path, 'rb') as f:
                part_number = 1
                offset = 0
                while offset < total_size:
                    num_to_upload = min(part_size, total_size - offset)
                    # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                    result = self.bucket.upload_part(filename, upload_id, part_number,
                                                     SizedFileAdapter(f, num_to_upload))
                    parts.append(PartInfo(part_number, result.etag))

                    offset += num_to_upload
                    part_number += 1
            self.bucket.complete_multipart_upload(filename, upload_id, parts)
            return True
        else:
            logger.error(f"file {local_file_full_path} is not file")
