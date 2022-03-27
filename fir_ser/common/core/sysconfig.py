#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 2月
# author: liuyu
# date: 2022/2/4

import json
import logging
import re

from django.template import Context, Template
from django.template.base import VariableNode
from rest_framework import serializers

from api.models import SystemConfig
from common.cache.storage import SystemConfigCache
from config import BASECONF, API_DOMAIN, MOBILEPROVISION, WEB_DOMAIN, THIRDLOGINCONF, AUTHCONF, IPACONF, MSGCONF, \
    DOWNLOADTIMESCONF, PAYCONF, STORAGEKEYCONF, SENDERCONF, APPLEDEVELOPERCONF

logger = logging.getLogger(__name__)


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = "__all__"


def get_render_context(tmp: str, context: dict) -> str:
    template = Template(tmp)
    for node in template.nodelist:
        if isinstance(node, VariableNode):
            v_key = re.findall(r'<Variable Node: (.*)>', str(node))
            if v_key and v_key[0].isupper():
                context[v_key[0]] = getattr(Config, v_key[0])
    context = Context(context)
    return template.render(context)


def invalid_config_cache(key='*'):
    SystemConfigCache(key).del_many()


def get_render_value(value):
    if value:
        try:
            context_dict = {}
            for sys_obj_dict in SystemConfig.objects.filter(enable=True).values().all():
                if re.findall('{{.*%s.*}}' % sys_obj_dict['key'], sys_obj_dict['value']):
                    logger.warning(f"get same render key. so continue")
                    continue
                context_dict[sys_obj_dict['key']] = sys_obj_dict['value']

            value = get_render_context(value, context_dict)
        except Exception as e:
            logger.warning(f"db config - render failed {e}")
    return value


class ConfigCacheBase(object):
    def __init__(self, px=''):
        self.px = px

    def get_value_from_db(self, key):
        data = SystemConfigSerializer(SystemConfig.objects.filter(enable=True, key=key).first()).data
        if re.findall('{{.*%s.*}}' % data['key'], data['value']):
            logger.warning(f"get same render key. so get default value")
            data['key'] = ''
        return data

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
            db_data['value'] = json.dumps(data)
            db_data['key'] = key
        db_data['value'] = get_render_value(db_data['value'])
        try:
            db_data['value'] = json.loads(db_data['value'])
        except Exception as e:
            logger.warning(f"db config - json loads failed {e}")
        cache.set_storage_cache(db_data, timeout=60 * 60 * 24 * 30)
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
        return self.get_value('MOBILEPROVISION', MOBILEPROVISION)

    @property
    def API_DOMAIN(self):
        return self.get_value('API_DOMAIN', API_DOMAIN)

    @property
    def WEB_DOMAIN(self):
        return self.get_value('WEB_DOMAIN', WEB_DOMAIN)

    @property
    def POST_UDID_DOMAIN(self):
        return self.get_value('POST_UDID_DOMAIN', self.API_DOMAIN)

    @property
    def FILE_UPLOAD_DOMAIN(self):
        return self.get_value('FILE_UPLOAD_DOMAIN', self.API_DOMAIN)


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
        return super().get_value('MOBILE_CONFIG_SIGN_SSL', IPACONF.MOBILE_CONFIG_SIGN_SSL)

    @property
    def DEFAULT_MOBILEPROVISION(self):
        return super().get_value('DEFAULT_MOBILEPROVISION', IPACONF.DEFAULT_MOBILEPROVISION)

    @property
    def APPLE_DEVELOPER_API_PROXY(self):
        return super().get_value('APPLE_DEVELOPER_API_PROXY', IPACONF.APPLE_DEVELOPER_API_PROXY)

    @property
    def APPLE_DEVELOPER_API_PROXY_LIST(self):
        return super().get_value('APPLE_DEVELOPER_API_PROXY_LIST', IPACONF.APPLE_DEVELOPER_API_PROXY_LIST)

    @property
    def APPLE_DEVELOPER_API_TIMEOUT(self):
        """
        访问苹果api超时时间，默认2分钟
        :return:
        """
        return super().get_value('APPLE_DEVELOPER_API_TIMEOUT', 2 * 60)


class WechatConfCache(ConfigCacheBase):
    def __init__(self):
        super(WechatConfCache, self).__init__()

    @property
    def THIRDLOGINCONF(self):
        return super().get_value('THIRDLOGINCONF', THIRDLOGINCONF.wx_official)


class AuthConfCache(WechatConfCache):
    def __init__(self):
        super(AuthConfCache, self).__init__()

    @property
    def REGISTER(self):
        """
        注册方式，如果启用sms或者email 需要配置 THIRD_PART_CONFIG_KEY_INFO.sender 信息
        :return:
        """
        return super().get_value('REGISTER', AUTHCONF.REGISTER)

    @property
    def CHANGER(self):
        return super().get_value('CHANGER', AUTHCONF.CHANGER)

    @property
    def NOTIFY(self):
        # return super().get_value('NOTIFY', AUTHCONF.NOTIFY)
        return AUTHCONF.NOTIFY

    @property
    def LOGIN(self):
        return super().get_value('LOGIN', AUTHCONF.LOGIN)

    @property
    def REPORT(self):
        return super().get_value('REPORT', AUTHCONF.REPORT)


class GeeTestConfCache(ConfigCacheBase):
    def __init__(self):
        super(GeeTestConfCache, self).__init__()

    @property
    def GEETEST_ID(self):
        return super().get_value('GEETEST_ID', BASECONF.GEETEST_ID)

    @property
    def GEETEST_KEY(self):
        return super().get_value('GEETEST_KEY', BASECONF.GEETEST_KEY)

    @property
    def GEETEST_CYCLE_TIME(self):
        """
        定时任务初始化，该数值无效，需要在配置中定义
        :return:
        """
        return super().get_value('GEETEST_CYCLE_TIME', BASECONF.GEETEST_CYCLE_TIME)

    @property
    def GEETEST_BYPASS_STATUS_KEY(self):
        return super().get_value('GEETEST_BYPASS_STATUS_KEY', BASECONF.GEETEST_BYPASS_STATUS_KEY)

    @property
    def GEETEST_BYPASS_URL(self):
        return super().get_value('GEETEST_BYPASS_URL', BASECONF.GEETEST_BYPASS_URL)


class UserDownloadTimesCache(ConfigCacheBase):
    def __init__(self):
        super(UserDownloadTimesCache, self).__init__()

    @property
    def USER_FREE_DOWNLOAD_TIMES(self):
        return super().get_value('USER_FREE_DOWNLOAD_TIMES', DOWNLOADTIMESCONF.USER_FREE_DOWNLOAD_TIMES)

    @property
    def AUTH_USER_FREE_DOWNLOAD_TIMES(self):
        return super().get_value('AUTH_USER_FREE_DOWNLOAD_TIMES', DOWNLOADTIMESCONF.AUTH_USER_FREE_DOWNLOAD_TIMES)

    @property
    def NEW_USER_GIVE_DOWNLOAD_TIMES(self):
        return super().get_value('NEW_USER_GIVE_DOWNLOAD_TIMES', DOWNLOADTIMESCONF.NEW_USER_GIVE_DOWNLOAD_TIMES)

    @property
    def AUTH_USER_GIVE_DOWNLOAD_TIMES(self):
        return super().get_value('AUTH_USER_GIVE_DOWNLOAD_TIMES', DOWNLOADTIMESCONF.AUTH_USER_GIVE_DOWNLOAD_TIMES)


class EmailMsgCache(ConfigCacheBase):
    def __init__(self):
        super(EmailMsgCache, self).__init__()

    @property
    def MSG_NOT_EXIST_DEVELOPER(self):
        return super().get_value('MSG_NOT_EXIST_DEVELOPER', MSGCONF.MSG_NOT_EXIST_DEVELOPER)

    @property
    def MSG_SING_APP_OVER_LIMIT(self):
        return super().get_value('MSG_SING_APP_OVER_LIMIT', MSGCONF.MSG_SING_APP_OVER_LIMIT)

    @property
    def MSG_ERROR_DEVELOPER(self):
        return super().get_value('MSG_ERROR_DEVELOPER', MSGCONF.MSG_ERROR_DEVELOPER)

    @property
    def MSG_AUTO_CHECK_DEVELOPER(self):
        return super().get_value('MSG_AUTO_CHECK_DEVELOPER', MSGCONF.MSG_AUTO_CHECK_DEVELOPER)


class PayConfCache(ConfigCacheBase):
    def __init__(self):
        super(PayConfCache, self).__init__()

    @property
    def PAY_SUCCESS_URL(self):
        return super().get_value('PAY_SUCCESS_URL', PAYCONF.PAY_SUCCESS_URL)

    @property
    def APP_NOTIFY_URL(self):
        return super().get_value('APP_NOTIFY_URL', PAYCONF.APP_NOTIFY_URL)

    @property
    def PAY_CONFIG_KEY_INFO(self):
        return super().get_value('PAY_CONFIG_KEY_INFO', PAYCONF.PAY_CONFIG_KEY_INFO)


class ThirdPartConfCache(ConfigCacheBase):
    def __init__(self):
        super(ThirdPartConfCache, self).__init__()

    @property
    def STORAGE(self):
        return super().get_value('STORAGE', STORAGEKEYCONF.STORAGE)

    @property
    def SENDER(self):
        return super().get_value('SENDER', SENDERCONF.SENDER)

    @property
    def WHITE_SENDER_CODE(self):
        return super().get_value('WHITE_SENDER_CODE', SENDERCONF.WHITE_SENDER_CODE)

    @property
    def WHITE_SENDER_LIST(self):
        return super().get_value('WHITE_SENDER_LIST', SENDERCONF.WHITE_SENDER_LIST)


class AppleDeveloperConfCache(ConfigCacheBase):
    def __init__(self):
        super(AppleDeveloperConfCache, self).__init__()

    @property
    def DEVELOPER_USE_STATUS(self):
        return super().get_value('DEVELOPER_USE_STATUS', APPLEDEVELOPERCONF.DEVELOPER_USE_STATUS)

    @property
    def DEVELOPER_SIGN_STATUS(self):
        return super().get_value('DEVELOPER_SIGN_STATUS', APPLEDEVELOPERCONF.DEVELOPER_SIGN_STATUS)

    @property
    def DEVELOPER_AUTO_CHECK_STATUS(self):
        return super().get_value('DEVELOPER_AUTO_CHECK_STATUS', APPLEDEVELOPERCONF.DEVELOPER_AUTO_CHECK_STATUS)

    @property
    def DEVELOPER_WRITE_STATUS(self):
        return super().get_value('DEVELOPER_WRITE_STATUS', APPLEDEVELOPERCONF.DEVELOPER_WRITE_STATUS)

    @property
    def DEVELOPER_DISABLED_STATUS(self):
        return super().get_value('DEVELOPER_DISABLED_STATUS', APPLEDEVELOPERCONF.DEVELOPER_DISABLED_STATUS)

    @property
    def DEVELOPER_UID_KEY(self):
        return super().get_value('DEVELOPER_UID_KEY', APPLEDEVELOPERCONF.DEVELOPER_UID_KEY)


class ConfigCache(BaseConfCache, IpaConfCache, AuthConfCache, EmailMsgCache, UserDownloadTimesCache, GeeTestConfCache,
                  PayConfCache, ThirdPartConfCache, AppleDeveloperConfCache):
    def __init__(self):
        super(ConfigCache, self).__init__()


Config = ConfigCache()
