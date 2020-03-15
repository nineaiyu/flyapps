#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/8/2

import json
import time
import uuid

from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

from base64 import encodebytes
from base64 import decodebytes


def format_params(params):
    """格式化参数

    """
    return sorted(
        ((k, v if not isinstance(v, dict) else json.dumps(v, separators=(',', ':'))) for k, v in params.items())
    )


def verify_signature(params, api_key):
    """验证签名

    """

    sign = params.pop("sign", "")

    if "sign_type" in params:
        params.pop("sign_type")

    # 针对字符串进行排序
    ordered_items = format_params(params)
    message = "&".join(u"{}={}".format(k, v) for k, v in ordered_items)
    # 验签
    signer = PKCS1_v1_5.new(api_key)
    digest = SHA256.new()
    digest.update(message.encode("utf8"))
    if signer.verify(digest, decodebytes(sign.encode("utf8"))):
        return True
    return False


def calculate_signature(params, api_key):
    """计算签名

    """
    signer = PKCS1_v1_5.new(api_key)
    signature = signer.sign(SHA256.new(params))
    # base64 编码，转换为unicode表示并移除回车
    sign = encodebytes(signature).decode("utf8").replace("\n", "")
    return sign


def get_uuid():
    """获取 `UUID`

    """
    return str(uuid.uuid4())


def get_iso_8061_date():
    """获取 `iso` 标准时间

    """
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
