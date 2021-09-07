#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 9月 
# author: NinEveN
# date: 2021/9/6
from hashlib import sha1
import requests
import logging
import json

from django.core.cache import cache

from fir_ser.settings import THIRDLOGINCONF, CACHE_KEY_TEMPLATE
from api.utils.mp.utils import WxMsgCryptBase

logger = logging.getLogger(__name__)
wx_login_info = THIRDLOGINCONF.wx_official

def format_req_json(j_data,func,*args,**kwargs):
    if j_data.get("errcode")==40001 or 'invalid credential'  in j_data.get('errmsg',''):
        logger.error(f"error j_data {j_data}")
        sync_wx_access_token(True)
        return func(*args,**kwargs)[1]
    return j_data


def sync_wx_access_token(force=False):
    wx_access_token_key = CACHE_KEY_TEMPLATE.get("wx_access_token_key")
    access_token_info = cache.get(wx_access_token_key)
    if not access_token_info or force:
        access_token_info = make_wx_auth_obj().get_access_token()
        expires_in = access_token_info.get('expires_in')
        if expires_in:
            cache.set(wx_access_token_key, access_token_info, expires_in - 60)
    return access_token_info


def get_wx_access_token_cache(c_count=1,):
    if c_count > 10:
        return ''
    wx_access_token_key = CACHE_KEY_TEMPLATE.get("wx_access_token_key")
    access_token = cache.get(wx_access_token_key)
    if access_token:
        return access_token.get('access_token')
    sync_wx_access_token(True)
    return get_wx_access_token_cache(c_count + 1)


def create_menu():
    menu_json = {
        "button": [
            {
                "type": "click",
                "name": "赞",
                "key": "good"
            },
            {
                "name": "分发平台",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "官方地址",
                        "url": "https://flyapps.cn"
                    },
                    {
                        "type": "view",
                        "name": "留言反馈",
                        "url": "https://flyapps.cn/gbook/"
                    },
                ]
            },
            {
                "type": "media_id",
                "name": "联系我们",
                "media_id": "qvQxPuAb4GnUgjkxl2xVnbsnldxawf4DXM09biqgP30"
            }
        ]
    }
    p_url = f"https://api.weixin.qq.com/cgi-bin/menu/create?access_token={get_wx_access_token_cache()}"
    req = requests.post(url=p_url, data=json.dumps(menu_json, ensure_ascii=False).encode('utf-8'))
    print(req.json())


def show_qrcode_url(ticket):
    return f'https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket={ticket}'


def make_wx_login_qrcode(scene_str='web.login', expire_seconds=600):
    """
    :param scene_str: 场景值ID（字符串形式的ID），字符串类型，长度限制为1到64
    :param expire_seconds: 该二维码有效时间，以秒为单位。 最大不超过2592000（即30天），此字段如果不填，则默认有效期为30秒。
    :return: {
        "ticket":"gQH47joAAAAAAAAAASxodHRwOi8vd2VpeGluLnFxLmNvbS9xL2taZ2Z3TVRtNzJXV1Brb3ZhYmJJAAIEZ23sUwMEmm3sUw==",
        "expire_seconds":60,
        "url":"http://weixin.qq.com/q/kZgfwMTm72WWPkovabbI"
    }
    https://developers.weixin.qq.com/doc/offiaccount/Account_Management/Generating_a_Parametric_QR_Code.html
    """
    t_url = f'https://api.weixin.qq.com/cgi-bin/qrcode/create?access_token={get_wx_access_token_cache()}'
    data = {"expire_seconds": expire_seconds, "action_name": "QR_STR_SCENE",
            "action_info": {"scene": {"scene_str": scene_str}}}
    req = requests.post(t_url, json=data)
    if req.status_code == 200:
        return True, format_req_json(req.json(),make_wx_login_qrcode,scene_str,expire_seconds)
    logger.error(f"make wx login qrcode failed {req.status_code} {req.text}")
    return False, req.text


def get_userinfo_from_openid(open_id):
    t_url = f'https://api.weixin.qq.com/cgi-bin/user/info?access_token={get_wx_access_token_cache()}&openid={open_id}&lang=zh_CN'
    req = requests.get(t_url)
    if req.status_code == 200:
        return True, format_req_json(req.json(),get_userinfo_from_openid,open_id)
    logger.error(f"get userinfo from openid failed {req.status_code} {req.text}")
    return False, req.text


class WxOfficialBase(object):

    def __init__(self, app_id, app_secret, token, encoding_aes_key):
        self.app_id = app_id
        self.app_secret = app_secret
        self.token = token
        self.encoding_aes_key = encoding_aes_key

    def get_access_token(self):
        t_url = f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.app_id}&secret={self.app_secret}'
        req = requests.get(t_url)
        if req.status_code == 200:
            return req.json()
        logger.error(f"get access token failed {req.status_code} {req.text}")
        return req.text


def make_wx_auth_obj():
    return WxOfficialBase(**wx_login_info.get('auth'))


def check_signature(params):
    tmp_list = sorted([wx_login_info.get('auth', {}).get('token'), params.get("timestamp"), params.get("nonce")])
    tmp_str = "".join(tmp_list)
    tmp_str = sha1(tmp_str.encode("utf-8")).hexdigest()
    if tmp_str == params.get("signature"):
        return int(params.get("echostr"))
    return ''


class WxMsgCrypt(WxMsgCryptBase):
    def __init__(self):
        super().__init__(**wx_login_info.get('auth'))
