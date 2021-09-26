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

from api.utils.baseutils import get_format_time
from fir_ser.settings import THIRDLOGINCONF, CACHE_KEY_TEMPLATE
from api.utils.mp.utils import WxMsgCryptBase

logger = logging.getLogger(__name__)
wx_login_info = THIRDLOGINCONF.wx_official


def format_req_json(j_data, func, *args, **kwargs):
    if j_data.get("errcode", -1) in [40001] or 'invalid credential' in j_data.get('errmsg', ''):
        logger.error(f"error j_data {j_data}")
        status, result = sync_wx_access_token(True)
        if not status:
            return result
        return func(*args, **kwargs)[1]
    return j_data


def sync_wx_access_token(force=False):
    wx_access_token_key = CACHE_KEY_TEMPLATE.get("wx_access_token_key")
    access_token_info = cache.get(wx_access_token_key)
    if not access_token_info or force:
        access_token_info = WxOfficialBase.make_wx_auth_obj().get_access_token()
        if access_token_info.get('errcode', -1) in [40013] or 'invalid appid' in access_token_info.get('errmsg', ''):
            return False, access_token_info
        expires_in = access_token_info.get('expires_in')
        if expires_in:
            cache.set(wx_access_token_key, access_token_info, expires_in - 60)
    return True, access_token_info


def get_wx_access_token_cache(c_count=1, ):
    if c_count > 5:
        return ''
    wx_access_token_key = CACHE_KEY_TEMPLATE.get("wx_access_token_key")
    access_token = cache.get(wx_access_token_key)
    if access_token:
        return access_token.get('access_token')
    status, result = sync_wx_access_token(True)
    if not status:
        return result
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
                        "type": "click",
                        "name": "官方地址",
                        "key": "flyapps"
                    },
                    {
                        "type": "view",
                        "name": "留言反馈",
                        "url": "https://flyapps.cn/gbook/"
                    },
                    {
                        "type": "click",
                        "name": "查询登录绑定",
                        "key": "query_bind"
                    },
                    {
                        "type": "click",
                        "name": "解除登录绑定",
                        "key": "unbind"
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
        return True, format_req_json(req.json(), make_wx_login_qrcode, scene_str, expire_seconds)
    logger.error(f"make wx login qrcode failed {req.status_code} {req.text}")
    return False, req.text


def get_userinfo_from_openid(open_id):
    t_url = f'https://api.weixin.qq.com/cgi-bin/user/info?access_token={get_wx_access_token_cache()}&openid={open_id}&lang=zh_CN'
    req = requests.get(t_url)
    if req.status_code == 200:
        return True, format_req_json(req.json(), get_userinfo_from_openid, open_id)
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
            logger.info(f"get access token {req.status_code} {req.text}")
            return req.json()
        logger.error(f"get access token failed {req.status_code} {req.text}")
        return req.text

    @classmethod
    def make_wx_auth_obj(cls):
        return cls(**wx_login_info.get('auth'))


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


class WxTemplateMsg(object):

    def send_msg(self, to_user, template_id, content):
        msg_uri = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={get_wx_access_token_cache()}'
        data = {
            "touser": to_user,
            "template_id": template_id,
            # "url": "http://weixin.qq.com/download",
            "topcolor": "#FF0000",
            "data": content
        }
        req = requests.post(msg_uri, json=data)
        if req.status_code == 200:
            return True, format_req_json(req.json(), get_userinfo_from_openid, to_user)
        logger.error(f"send msg from openid failed {req.status_code} {req.text}")
        return False, req.text

    def login_success_msg(self, to_user, wx_nick_name, username):
        """
        您进行了微信扫一扫登录操作
        系统帐号：yin.xiaogang
        登录系统：OA系统
        登录时间：2014-11-28 10:06:32
        如有疑问，请致电IT服务台400-888-8888 或 关注公众号在线反馈
        :param to_user:
        :param wx_nick_name:    微信昵称
        :param username:  flyapps 用户昵称
        :return:
        """
        now_time = get_format_time()
        msg_id = 'EJhBbxJvHdWnwwexaqb0lCC2sM7D7WMex5-yJvTL5sU'
        content_data = {
            "first": {
                "value": f"您的微信账户“{wx_nick_name}”进行了网站登录操作",
                "color": "#173177"
            },
            "keyword1": {
                "value": username,
                "color": "#173177"
            },
            "keyword2": {
                "value": "fly应用分发平台",
                "color": "#173177"
            },
            "keyword3": {
                "value": now_time.replace('_', ' '),
                "color": "#173177"
            },
            "remark": {
                "value": "感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(to_user, msg_id, content_data)

    def login_failed_msg(self, to_user, wx_nick_name):
        now_time = get_format_time()
        msg_id = '9rChJFw6nR0Wbp7SXsImh99qm6Dj1hrRWJo1NpEJ_3g'
        content_data = {
            "first": {
                "value": f"您的微信账户“{wx_nick_name}”登录失败",
                "color": "#173177"
            },
            "keyword1": {
                "value": "还未绑定用户，请通过手机或者邮箱登录账户之后进行绑定",
                "color": "#173177"
            },
            "keyword2": {
                "value": now_time.replace('_', ' '),
                "color": "#173177"
            },
            "remark": {
                "value": "感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(to_user, msg_id, content_data)

    def bind_success_msg(self, to_user, wx_nick_name, username):
        now_time = get_format_time()
        msg_id = 'twMMQn9AKZKevbZBYh8EcFMk7BnC5Y09FmDkZQEH43w'
        content_data = {
            "first": {
                "value": f"您的微信账户“{wx_nick_name}”绑定成功",
                "color": "#173177"
            },
            "keyword1": {
                "value": username,
                "color": "#173177"
            },
            "keyword2": {
                "value": now_time.replace('_', ' '),
                "color": "#173177"
            },
            "remark": {
                "value": "感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(to_user, msg_id, content_data)

    def bind_failed_msg(self, to_user, wx_nick_name, msg):
        now_time = get_format_time()
        msg_id = 'WIrRuHiDG0f976seBAmY-rjSil0AiT9E5l0PHrPnsfs'
        content_data = {
            "first": {
                "value": f"您的微信账户“{wx_nick_name}”绑定失败",
                "color": "#173177"
            },
            "keyword1": {
                "value": msg,
                "color": "#173177"
            },
            "keyword2": {
                "value": now_time.replace('_', ' '),
                "color": "#173177"
            },
            "remark": {
                "value": "每个微信只可以绑定一个登录账户，请先解绑，然后重新扫描绑定。感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(to_user, msg_id, content_data)

    def unbind_success_msg(self, to_user, wx_nick_name, username):
        now_time = get_format_time()
        msg_id = 'RabYMg8-jPGhonk957asbW17iLHSLp8BfEXnyesRZ60'
        content_data = {
            "first": {
                "value": f"您的微信账户“{wx_nick_name}”已经解除绑定",
                "color": "#173177"
            },
            "keyword1": {
                "value": username,
                "color": "#173177"
            },
            "keyword2": {
                "value": now_time.replace('_', ' '),
                "color": "#173177"
            },
            "keyword3": {
                "value": "解除绑定成功，您将无法使用微信扫描登录平台",
                "color": "#173177"
            },
            "remark": {
                "value": "如需重新绑定，请登陆平台，在个人资料进行绑定。感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(to_user, msg_id, content_data)

    def bind_query_success_msg(self, to_user, wx_nick_name, username, name, mobile, email):
        msg_id = 'yU15jLNSULagJTff01X67mDtDytBSs3iBpOBi8c7dvs'
        content_data = {
            "first": {
                "value": f"您的微信账户“{wx_nick_name}”绑定信息结果",
                "color": "#173177"
            },
            "keyword1": {
                "value": username,
                "color": "#173177"
            },
            "keyword2": {
                "value": name,
                "color": "#173177"
            },
            "keyword3": {
                "value": mobile,
                "color": "#173177"
            },
            "keyword4": {
                "value": email,
                "color": "#173177"
            },
            "remark": {
                "value": "感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(to_user, msg_id, content_data)

    def query_bind_info_failed_msg(self, to_user, wx_nick_name, action_msg, failed_msg):
        now_time = get_format_time()
        msg_id = 'uCxjYt216zRAv_sPZihKk4xp7-6pLmRW1oNLLW7L3oI'
        content_data = {
            "first": {
                "value": f"您的微信账户“{wx_nick_name}” {action_msg}失败了",
                "color": "#173177"
            },
            "keyword1": {
                "value": wx_nick_name,
                "color": "#173177"
            },
            "keyword2": {
                "value": action_msg,
                "color": "#173177"
            },
            "keyword3": {
                "value": failed_msg,
                "color": "#173177"
            },
            "keyword4": {
                "value": now_time.replace('_', ' '),
                "color": "#173177"
            },
            "remark": {
                "value": "暂无登录绑定信息，如需绑定，请登陆平台，在个人资料进行绑定。感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(to_user, msg_id, content_data)
