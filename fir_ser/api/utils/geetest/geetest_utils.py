#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/25

import requests
import json
import logging
from django.core.cache import cache as redis_connect
from fir_ser.settings import GEETEST_ID, GEETEST_KEY, GEETEST_BYPASS_URL, \
    GEETEST_BYPASS_STATUS_KEY
from api.utils.geetest.geetest_lib import GeetestLib

logger = logging.getLogger(__name__)


# 发送bypass请求，获取bypass状态并进行缓存（如何缓存可根据自身情况合理选择,这里是使用redis进行缓存）
def check_bypass_status():
    response = ""
    params = {"gt": GEETEST_ID}
    try:
        response = requests.get(url=GEETEST_BYPASS_URL, params=params)
    except Exception as e:
        logger.error(f"check_bypass_status failed Exception:{e}")
    if response and response.status_code == 200:
        logger.debug(f"check_bypass_status success {response.content}")
        bypass_status_str = response.content.decode("utf-8")
        bypass_status = json.loads(bypass_status_str).get("status")
        redis_connect.set(GEETEST_BYPASS_STATUS_KEY, bypass_status)
    else:
        bypass_status = "fail"
        redis_connect.set(GEETEST_BYPASS_STATUS_KEY, bypass_status)
    logger.debug(f"bypass状态已经获取并存入redis，当前状态为 {bypass_status}")


# 从缓存中取出当前缓存的bypass状态(success/fail)
def get_bypass_cache(count=3):
    bypass_status_cache = redis_connect.get(GEETEST_BYPASS_STATUS_KEY)
    if bypass_status_cache:
        return bypass_status_cache
    else:
        if count > 0:
            check_bypass_status()
            count -= 1
            return get_bypass_cache(count)
        else:
            return 'fail'


# 验证初始化接口，GET请求
def first_register(user_id, ip_address):
    # 必传参数
    #     digestmod 此版本sdk可支持md5、sha256、hmac-sha256，md5之外的算法需特殊配置的账号，联系极验客服
    # 自定义参数,可选择添加
    #     user_id 客户端用户的唯一标识，确定用户的唯一性；作用于提供进阶数据分析服务，可在register和validate接口传入，不传入也不影响验证服务的使用；若担心用户信息风险，可作预处理(如哈希处理)再提供到极验
    #     client_type 客户端类型，web：电脑上的浏览器；h5：手机上的浏览器，包括移动应用内完全内置的web_view；native：通过原生sdk植入app应用的方式；unknown：未知
    #     ip_address 客户端请求sdk服务器的ip地址
    bypass_status = get_bypass_cache()
    gt_lib = GeetestLib(GEETEST_ID, GEETEST_KEY)
    digestmod = "md5"
    param_dict = {"digestmod": digestmod, "user_id": user_id, "client_type": "web", "ip_address": ip_address}
    if bypass_status == "success":
        result = gt_lib.register(digestmod, param_dict)
    else:
        result = gt_lib.local_init()
    # 注意，不要更改返回的结构和值类型
    return json.loads(result.data)


# 二次验证接口，POST请求
def second_validate(rdata):
    challenge = rdata.get(GeetestLib.GEETEST_CHALLENGE, None)
    validate = rdata.get(GeetestLib.GEETEST_VALIDATE, None)
    seccode = rdata.get(GeetestLib.GEETEST_SECCODE, None)
    bypass_status = get_bypass_cache()
    gt_lib = GeetestLib(GEETEST_ID, GEETEST_KEY)
    if bypass_status == "success":
        result = gt_lib.success_validate(challenge, validate, seccode)
    else:
        result = gt_lib.fail_validate(challenge, validate, seccode)
    # 注意，不要更改返回的结构和值类型
    if result.status == 1:
        response = {"result": "success", "version": GeetestLib.VERSION}
    else:
        response = {"result": "fail", "version": GeetestLib.VERSION, "msg": result.msg}
    logger.info(f"geetest second_validate info {response}")
    return response
