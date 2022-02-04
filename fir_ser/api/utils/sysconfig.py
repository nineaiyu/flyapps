#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 2月
# author: liuyu
# date: 2022/2/4

import json
import logging

from rest_framework import serializers

from api.models import SystemConfig
from common.cache.storage import SystemConfigCache
from config import BASECONF, API_DOMAIN, MOBILEPROVISION, WEB_DOMAIN

logger = logging.getLogger(__name__)


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = "__all__"


def invalid_config_cache():
    SystemConfigCache('*').del_many()


# def make_json_value(value, default):
#     try:
#         if isinstance(value, str):
#             value = json.loads(value)
#         if isinstance(value, dict):
#             return value
#     except Exception as e:
#         logger.warning(f"sysconfig make json value failed {value} Exception:{e}")
#         return default


class ConfigCacheBase(object):
    def __init__(self, px=''):
        self.px = px

    def get_value_from_db(self, key):
        sys_obj = SystemConfig.objects.filter(key=key).first()
        return SystemConfigSerializer(sys_obj).data

    def get_value(self, key, data=None):
        if data is None:
            data = {}
        cache = SystemConfigCache(key)
        cache_data = cache.get_storage_cache()
        if cache_data is not None and cache_data.get('key', '') == key:
            return cache_data.get('value')
        db_data = self.get_value_from_db(key)
        d_key = db_data.get('key', '')
        if d_key != key and data is not None:
            db_data['value'] = data
            db_data['key'] = key
        cache.set_storage_cache(db_data, timeout=0)
        return db_data.get('value')

    def set_value(self, key, value):
        if not isinstance(value, str):
            value = json.dumps(value)
        SystemConfig.objects.update_or_create(key=key, defaults={'value': value})
        SystemConfigCache(key).del_storage_cache()

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except Exception as e:
            logger.error(f"__getattribute__ Error  {e}  {name}")
            return self.get_value(name)

    @property
    def MOBILEPROVISION(self):
        return self.get_value('MOBILEPROVISION') if self.get_value('MOBILEPROVISION') else MOBILEPROVISION

    @property
    def API_DOMAIN(self):
        return self.get_value('API_DOMAIN') if self.get_value('API_DOMAIN') else API_DOMAIN

    @property
    def WEB_DOMAIN(self):
        return self.get_value('WEB_DOMAIN') if self.get_value('WEB_DOMAIN') else WEB_DOMAIN

    @property
    def POST_UDID_DOMAIN(self):
        return self.get_value('POST_UDID_DOMAIN') if self.get_value('POST_UDID_DOMAIN') else self.API_DOMAIN

    @property
    def FILE_UPLOAD_DOMAIN(self):
        return self.get_value('FILE_UPLOAD_DOMAIN') if self.get_value('FILE_UPLOAD_DOMAIN') else self.API_DOMAIN


class BaseConfCache(ConfigCacheBase):
    def __init__(self):
        super(BaseConfCache, self).__init__()

    @property
    def IOS_PMFILE_DOWNLOAD_DOMAIN(self):
        # 验证码，ios 描述文件和plist文件下载域名，该域名用于后端，一般为api访问域名
        return {
            "domain_name": self.API_DOMAIN.split("://")[1],
            'is_https': True if self.API_DOMAIN.split("://")[0] == "https" else False,
        }

    @property
    def DEFAULT_THROTTLE_RATES(self):
        """
        暂时无用
        :return:
        """
        return super().get_value('DEFAULT_THROTTLE_RATES', BASECONF.DEFAULT_THROTTLE_RATES)


class IpaConfCache(ConfigCacheBase):
    def __init__(self):
        super(IpaConfCache, self).__init__()

    @property
    def MOBILE_CONFIG_SIGN_SSL(self):
        return super().get_value('MOBILE_CONFIG_SIGN_SSL', {
            # 描述文件是否签名，默认是关闭状态；如果开启，并且ssl_key_path 和 ssl_pem_path 正常，则使用填写的ssl进行签名,否则默认不签名
            'open': True,
            'ssl_key_path': '/data/cert/%s.key' % self.API_DOMAIN.split("://")[1],
            'ssl_pem_path': '/data/cert/%s.pem' % self.API_DOMAIN.split("://")[1]
        })

    @property
    def DEFAULT_MOBILEPROVISION(self):
        return super().get_value('DEFAULT_MOBILEPROVISION', {
            # 默认描述文件路径或者下载路径，用户企业签名或者超级签名 跳转 [设置 - 通用 - 描述文件|设备管理] 页面
            # 如果配置了path路径，则走路径，如果配置了url，则走URL，path 优先级大于url优先级
            'enterprise': {
                'url': self.MOBILEPROVISION,
                # 'path': os.path.join(BASE_DIR,'files', 'embedded.mobileprovision'),
            },
            'supersign': {
                # 超级签名，如果self 为True，则默认用自己的描述文件，否则同企业配置顺序一致,自己的配置文件有时候有问题
                'self': False,
                'url': self.MOBILEPROVISION,
                # 'path': os.path.join(BASE_DIR,'files', 'embedded.mobileprovision'),
            }
        })

    @property
    def APPLE_DEVELOPER_API_PROXY(self):
        return super().get_value('APPLE_DEVELOPER_API_PROXY', {
            # 代理的作用，主要是为了加快苹果api的访问，在国内会出现卡死，访问超时等问题，怀疑是被苹果服务器拦截了
            # 'http': '47.243.172.202:17897',
            # 'https': '47.243.172.202:17897'
        })

    @property
    def APPLE_DEVELOPER_API_PROXY_LIST(self):
        return super().get_value('APPLE_DEVELOPER_API_PROXY_LIST', [
            # '47.243.172.201:17897',
            # '47.243.172.202:17897',
            # '47.243.172.203:17897'
        ])

    @property
    def APPLE_DEVELOPER_API_TIMEOUT(self):
        """
        访问苹果api超时时间，默认2分钟
        :return:
        """
        value = super().get_value('APPLE_DEVELOPER_API_TIMEOUT')
        return value if value is not None else 2 * 60


class WechatConfCache(ConfigCacheBase):
    def __init__(self):
        super(WechatConfCache, self).__init__()

    @property
    def THIRDLOGINCONF(self):
        return super().get_value('THIRDLOGINCONF', {
            'name': 'wx_official',
            'auth': {
                'app_id': 'we6',
                'app_secret': '5bfb678',
                'token': 'f0ae1b879b8',
                'encoding_aes_key': '7b9URovp83gG',
            },
            'active': True
        })


class AuthConfCache(WechatConfCache):
    def __init__(self):
        super(AuthConfCache, self).__init__()

    @property
    def REGISTER(self):
        """
        注册方式，如果启用sms或者email 需要配置 THIRD_PART_CONFIG_KEY_INFO.sender 信息
        :return:
        """
        return super().get_value('REGISTER', {
            "enable": True,
            "captcha": False,  # 是否开启注册字母验证码
            "geetest": True,  # 是否开启geetest验证，如要开启请先配置geetest
            "register_type": {
                'sms': True,  # 短信注册
                'email': True,  # 邮件注册
                'code': False,  # 邀请码注册,邀请码必填写，需要和短信，邮件一起使用
            }
        })

    @property
    def CHANGER(self):
        return super().get_value('CHANGER', {
            "enable": True,
            "captcha": False,  # 是否开启注册字母验证码
            "geetest": True,  # 是否开启geetest验证，如要开启请先配置geetest
            "change_type": {
                'sms': True,  # 短信注册
                'email': True,  # 邮件注册
                'code': False,  # 邀请码注册,邀请码必填写，需要和短信，邮件一起使用
            }
        })

    @property
    def LOGIN(self):
        return super().get_value('LOGIN', {
            "captcha": False,  # 是否开启登录字母验证码
            "geetest": True,  # 是否开启geetest验证
            "login_type": {
                'sms': True,  # 短信登录
                'email': True,  # 邮件登录
                'up': False,  # 密码登录
                'third': {
                    'wxp': self.THIRDLOGINCONF.get('active')  # 微信公众号登录，需要在 THIRDLOGINCONF 配置好微信公众号登录
                },
            }
        })

    @property
    def REPORT(self):
        return super().get_value('REPORT', {
            "enable": True,
            "captcha": True,  # 是否开启注册字母验证码
            "geetest": False,  # 是否开启geetest验证，如要开启请先配置geetest
            "report_type": {
                'sms': False,  # 短信举报
                'email': True,  # 邮件举报
            }
        })


class GeeTestConfCache(ConfigCacheBase):
    def __init__(self):
        super(GeeTestConfCache, self).__init__()

    @property
    def GEETEST_ID(self):
        value = super().get_value('GEETEST_ID')
        return value if value else BASECONF.GEETEST_ID

    @property
    def GEETEST_KEY(self):
        value = super().get_value('GEETEST_KEY')
        return value if value else BASECONF.GEETEST_KEY

    @property
    def GEETEST_CYCLE_TIME(self):
        """
        定时任务初始化，该数值无效，需要在配置中定义
        :return:
        """
        value = super().get_value('GEETEST_CYCLE_TIME')
        return value if value else BASECONF.GEETEST_CYCLE_TIME

    @property
    def GEETEST_BYPASS_STATUS_KEY(self):
        value = super().get_value('GEETEST_BYPASS_STATUS_KEY')
        return value if value else BASECONF.GEETEST_BYPASS_STATUS_KEY

    @property
    def GEETEST_BYPASS_URL(self):
        value = super().get_value('GEETEST_BYPASS_URL')
        return value if value else BASECONF.GEETEST_BYPASS_URL


class UserDownloadTimesCache(ConfigCacheBase):
    def __init__(self):
        super(UserDownloadTimesCache, self).__init__()

    @property
    def USER_FREE_DOWNLOAD_TIMES(self):
        value = super().get_value('USER_FREE_DOWNLOAD_TIMES')
        return value if value else 5

    @property
    def AUTH_USER_FREE_DOWNLOAD_TIMES(self):
        value = super().get_value('AUTH_USER_FREE_DOWNLOAD_TIMES')
        return value if value else 10

    @property
    def NEW_USER_GIVE_DOWNLOAD_TIMES(self):
        value = super().get_value('NEW_USER_GIVE_DOWNLOAD_TIMES')
        return value if value else 100

    @property
    def AUTH_USER_GIVE_DOWNLOAD_TIMES(self):
        value = super().get_value('AUTH_USER_GIVE_DOWNLOAD_TIMES')
        return value if value else 200


class EmailMsgCache(ConfigCacheBase):
    def __init__(self):
        super(EmailMsgCache, self).__init__()

    @property
    def MSG_NOT_EXIST_DEVELOPER(self):
        value = super().get_value('MSG_NOT_EXIST_DEVELOPER')
        tem = '用户 %s 你好，应用 %s 签名失败了，苹果开发者总设备量已经超限，请添加新的苹果开发者或者修改开发者设备数量。感谢有你!'
        return value if value else tem

    @property
    def MSG_ERROR_DEVELOPER(self):
        value = super().get_value('MSG_ERROR_DEVELOPER')
        tem = '用户 %s 你好，应用 %s 签名失败了，苹果开发者 %s 信息异常，请重新检查苹果开发者状态是否正常。感谢有你!'
        return value if value else tem

    @property
    def MSG_AUTO_CHECK_DEVELOPER(self):
        value = super().get_value('MSG_AUTO_CHECK_DEVELOPER')
        tem = '用户 %s 你好，苹果开发者 %s 信息异常，请重新检查苹果开发者状态是否正常。感谢有你!'
        return value if value else tem


class ConfigCache(BaseConfCache, IpaConfCache, AuthConfCache, EmailMsgCache, UserDownloadTimesCache, GeeTestConfCache):
    def __init__(self):
        super(ConfigCache, self).__init__()


Config = ConfigCache()
