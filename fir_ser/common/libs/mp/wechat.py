#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 9月 
# author: NinEveN
# date: 2021/9/6
import json
import logging
import urllib
from hashlib import sha1

import requests
from django.urls import reverse

from common.base.baseutils import get_format_time
from common.cache.storage import WxTokenCache
from common.core.sysconfig import Config
from common.libs.mp.utils import WxMsgCryptBase
from common.libs.storage.localApi import LocalStorage

logger = logging.getLogger(__name__)


def format_req_json(j_data, func, *args, **kwargs):
    if j_data.get("errcode", -1) in [40001] or 'invalid credential' in j_data.get('errmsg', ''):
        logger.error(f"error j_data {j_data}")
        status, result = sync_wx_access_token(True)
        if not status:
            return result
        return func(*args, **kwargs)[1]
    logger.info(f'j_data:{j_data}')
    return j_data


def sync_wx_access_token(force=False):
    wx_cache = WxTokenCache()
    access_token_info = wx_cache.get_storage_cache()
    if not access_token_info or force:
        access_token_info = WxOfficialBase.make_wx_auth_obj().get_access_token()
        if access_token_info.get('errcode', -1) in [40013] or 'invalid appid' in access_token_info.get('errmsg', ''):
            return False, access_token_info
        expires_in = access_token_info.get('expires_in')
        if expires_in:
            wx_cache.set_storage_cache(access_token_info, expires_in - 60)
    return True, access_token_info


def get_wx_access_token_cache(c_count=1, ):
    if c_count > 5:
        return ''
    access_token = WxTokenCache().get_storage_cache()
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
        return cls(**Config.THIRDLOGINCONF.get('auth'))


def check_signature(params):
    tmp_list = sorted(
        [Config.THIRDLOGINCONF.get('auth', {}).get('token'), params.get("timestamp"), params.get("nonce")])
    tmp_str = "".join(tmp_list)
    tmp_str = sha1(tmp_str.encode("utf-8")).hexdigest()
    if tmp_str == params.get("signature"):
        return int(params.get("echostr"))
    return ''


class WxMsgCrypt(WxMsgCryptBase):
    def __init__(self):
        super().__init__(**Config.THIRDLOGINCONF.get('auth'))


class WxTemplateMsg(object):

    def __init__(self, to_user, wx_nick_name):
        self.to_user = to_user
        self.wx_nick_name = wx_nick_name

    def send_msg(self, template_id, content):
        if not Config.THIRDLOGINCONF.get('active'):
            return False, f'weixin status is disabled'
        msg_uri = f'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={get_wx_access_token_cache()}'
        data = {
            "touser": self.to_user,
            "template_id": template_id,
            # "url": "http://weixin.qq.com/download",
            "topcolor": "#FF0000",
            "data": content
        }
        req = requests.post(msg_uri, json=data)
        if req.status_code == 200:
            return True, format_req_json(req.json(), self.send_msg, self.to_user, template_id, content)
        logger.error(f"send msg from openid failed {req.status_code} {req.text}")
        return False, req.text

    def login_success_msg(self, username):
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
                "value": f"您的微信账户“{self.wx_nick_name}”进行了网站登录操作",
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
        return self.send_msg(msg_id, content_data)

    def login_failed_msg(self):
        now_time = get_format_time()
        msg_id = '9rChJFw6nR0Wbp7SXsImh99qm6Dj1hrRWJo1NpEJ_3g'
        content_data = {
            "first": {
                "value": f"您的微信账户“{self.wx_nick_name}”登录失败",
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
        return self.send_msg(msg_id, content_data)

    def bind_success_msg(self, username):
        now_time = get_format_time()
        msg_id = 'twMMQn9AKZKevbZBYh8EcFMk7BnC5Y09FmDkZQEH43w'
        content_data = {
            "first": {
                "value": f"您的微信账户“{self.wx_nick_name}”绑定成功",
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
        return self.send_msg(msg_id, content_data)

    def bind_failed_msg(self, msg):
        now_time = get_format_time()
        msg_id = 'WIrRuHiDG0f976seBAmY-rjSil0AiT9E5l0PHrPnsfs'
        content_data = {
            "first": {
                "value": f"您的微信账户“{self.wx_nick_name}”绑定失败",
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
        return self.send_msg(msg_id, content_data)

    def unbind_success_msg(self, username):
        now_time = get_format_time()
        msg_id = 'RabYMg8-jPGhonk957asbW17iLHSLp8BfEXnyesRZ60'
        content_data = {
            "first": {
                "value": f"您的微信账户“{self.wx_nick_name}”已经解除绑定",
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
        return self.send_msg(msg_id, content_data)

    def bind_query_success_msg(self, username, name, mobile, email, description):
        msg_id = 'yU15jLNSULagJTff01X67mDtDytBSs3iBpOBi8c7dvs'
        content_data = {
            "first": {
                "value": f"您的微信账户“{self.wx_nick_name}”绑定信息结果",
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
                "value": f"{description}感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(msg_id, content_data)

    def query_bind_info_failed_msg(self, action_msg, failed_msg):
        now_time = get_format_time()
        msg_id = 'uCxjYt216zRAv_sPZihKk4xp7-6pLmRW1oNLLW7L3oI'
        content_data = {
            "first": {
                "value": f"您的微信账户“{self.wx_nick_name}” {action_msg}失败了",
                "color": "#173177"
            },
            "keyword1": {
                "value": self.wx_nick_name,
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
        return self.send_msg(msg_id, content_data)

    def auth_code_msg(self, code, expire_date):
        msg_id = 'vRCegZatP18LAe9ytLirwfL1CFyzaCQwM89hMAKsUAA'
        content_data = {
            "first": {
                "value": f"您好，“{self.wx_nick_name}”",
                "color": "#173177"
            },
            "keyword1": {
                "value": code,
                "color": "#173177"
            },
            "keyword2": {
                "value": f"{expire_date}内有效",
                "color": "#173177"
            },
            "remark": {
                "value": "若非本人操作，可能您的帐号存在安全风险，请及时修改密码",
                "color": "#173177"
            },
        }
        return self.send_msg(msg_id, content_data)

    def something_not_enough_msg(self, title, username, balance_msg, desc_msg):
        msg_id = '34UZQuncRei2t6kRN6k4FGRiwzxU8GyvufnrV3hqEHI'
        content_data = {
            "first": {
                "value": title,
                "color": "#173177"
            },
            "keyword1": {
                "value": username,
                "color": "#173177"
            },
            "keyword2": {
                "value": balance_msg,
                "color": "#173177"
            },
            "remark": {
                "value": desc_msg,
                "color": "#173177"
            },
        }
        return self.send_msg(msg_id, content_data)

    def download_times_not_enough_msg(self, username, download_times, desc_msg="感谢您的关注"):
        return self.something_not_enough_msg(f"您好，“{self.wx_nick_name}”，您当前账户下载次数不足，望您尽快充值!", username,
                                             f"{download_times} 下载次数", desc_msg)

    def apple_developer_devices_not_enough_msg(self, username, devices_count, desc_msg="感谢您的关注"):
        return self.something_not_enough_msg(f"您好，“{self.wx_nick_name}”，您当前账户签名余额不足，望您尽快添加!", username,
                                             f"{devices_count} 设备数", desc_msg)

    def cert_expired_msg(self, developer_id, cert_id, expired_time):
        msg_id = '59sF_30TZ3gB6ugE7BHzv2-LDBnh_3cOn6R-85bvZ0E'
        content_data = {
            "first": {
                "value": f'你好，“{self.wx_nick_name}“，您苹果开发者证书即将到期',
                "color": "#173177"
            },
            "keyword1": {
                "value": developer_id,
                "color": "#173177"
            },
            "keyword2": {
                "value": cert_id,
                "color": "#173177"
            },
            "keyword3": {
                "value": expired_time,
                "color": "#173177"
            },
            "remark": {
                "value": "为了保证您开发者可用，请您尽快更新开发者证书，感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(msg_id, content_data)

    def pay_success_msg(self, product_name, price, pay_type, pay_time, order, description):
        msg_id = 'LjlbeavVnGk5j2BhSblPudt_ts3gw9b_ydXS_C1uW6g'
        content_data = {
            "first": {
                "value": f'你好，“{self.wx_nick_name}“，下载次数充值成功',
                "color": "#173177"
            },
            "keyword1": {
                "value": product_name,
                "color": "#173177"
            },
            "keyword2": {
                "value": price,
                "color": "#173177"
            },
            "keyword3": {
                "value": pay_type,
                "color": "#173177"
            },
            "keyword4": {
                "value": pay_time,
                "color": "#173177"
            },
            "keyword5": {
                "value": order,
                "color": "#173177"
            },
            "remark": {
                "value": f"{description}，感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(msg_id, content_data)

    def operate_failed_msg(self, first_name, operate_context, failed_msg, operate_time, description):
        msg_id = 'Hnrk5iXRjbaCTVpSIyC5KC8cwFNDgplNUzPsnyDXRLo'
        content_data = {
            "first": {
                "value": f'你好，“{self.wx_nick_name}“，签名失败了',
                "color": "#173177"
            },
            "keyword1": {
                "value": first_name,
                "color": "#173177"
            },
            "keyword2": {
                "value": operate_context,
                "color": "#173177"
            },
            "keyword3": {
                "value": failed_msg,
                "color": "#173177"
            },
            "keyword4": {
                "value": operate_time,
                "color": "#173177"
            },
            "remark": {
                "value": f"{description}，感谢您的关注",
                "color": "#173177"
            },
        }
        return self.send_msg(msg_id, content_data)


class WxWebLogin(object):
    """
    通过网页授权，获取用户授权信息【公众号已经无法获取用户的昵称头像等隐私信息】
    https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/Wechat_webpage_authorization.html
    """

    def __init__(self):
        self.openid = None
        self.access_token = None
        auth_info = Config.THIRDLOGINCONF.get('auth')
        self.app_id = auth_info.get('app_id')
        self.app_secret = auth_info.get('app_secret')

    def make_auth_uri(self):
        """
        第一步： 用户通过微信客户端打开该URI
        :return:
        """
        # url = 'https://app.hehelucky.cn/api/v1/fir/server/wxweb'  # 该url是前端页面，用户微信跳转，后端页面也行
        local_storage = LocalStorage(**Config.IOS_PMFILE_DOWNLOAD_DOMAIN)
        url = f'{local_storage.get_base_url()}{reverse("mp.web.login")}'
        encode_url = urllib.parse.quote(url, safe='/', encoding=None, errors=None)
        code_url = f'https://open.weixin.qq.com/connect/oauth2/authorize?appid={self.app_id}&redirect_uri={encode_url}&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'
        return code_url

    def get_wx_token(self, code):
        """
        第二步： 获取授权之后，微信会携带code并且自动跳转,然后通过code获取授权token，自测该token只能获取该用户信息，无法获取其他用户信息
        :param code:
        :return:
            {
              "access_token":"ACCESS_TOKEN",
              "expires_in":7200,
              "refresh_token":"REFRESH_TOKEN",
              "openid":"OPENID",
              "scope":"SCOPE"
            }
        """
        t_url = f'https://api.weixin.qq.com/sns/oauth2/access_token?appid={self.app_id}&secret={self.app_secret}&code={code}&grant_type=authorization_code'
        req = requests.get(t_url)
        if req.status_code == 200:
            logger.info(f"get access token {req.status_code} {req.text}")
            auth_info = req.json()
            self.access_token = auth_info.get('access_token')
            self.openid = auth_info.get('openid')
            return auth_info
        return {}

    def get_user_info(self):
        """
        第三步： 通过token获取用户信息
        :return:
        """
        t_url = f'https://api.weixin.qq.com/sns/userinfo?access_token={self.access_token}&openid={self.openid}&lang=zh_CN'
        req = requests.get(t_url)
        if req.status_code == 200:
            req.encoding = 'utf-8'
            return req.json()
        return {}
