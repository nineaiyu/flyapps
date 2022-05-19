#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 2月
# author: liuyu
# date: 2022/2/4

import json
import logging
import re

from django.template import Context, Template, TemplateSyntaxError
from django.template.base import VariableNode
from rest_framework import serializers

from api.models import SystemConfig, UserPersonalConfig
from common.cache.storage import UserSystemConfigCache
from config import BASECONF, THIRDLOGINCONF, AUTHCONF, IPACONF, DOWNLOADTIMESCONF, PAYCONF, STORAGEKEYCONF, SENDERCONF, \
    APPLEDEVELOPERCONF, DOMAINCONF, USERPERSONALCONFIGKEY, CONFIGDESCRIPTION, OSSSTORAGECONF

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


class ConfigCacheBase(object):
    def __init__(self, px='system', model=SystemConfig, cache=UserSystemConfigCache, serializer=SystemConfigSerializer,
                 timeout=60 * 60 * 24 * 30):
        self.px = px
        self.model = model
        self.cache = cache
        self.timeout = timeout
        self.serializer = serializer

    def invalid_config_cache(self, key='*'):
        UserSystemConfigCache(f'{self.px}_{key}').del_many()

    def get_render_value(self, value):
        if value:
            try:
                context_dict = {}
                for sys_obj_dict in self.model.objects.filter(enable=True).values().all():
                    if re.findall('{{.*%s.*}}' % sys_obj_dict['key'], sys_obj_dict['value']):
                        logger.warning(f"get same render key. so continue")
                        continue
                    context_dict[sys_obj_dict['key']] = sys_obj_dict['value']
                try:
                    value = get_render_context(value, context_dict)
                except TemplateSyntaxError as e:
                    res_list = re.findall("Could not parse the remainder: '{{(.*?)}}'", str(e))
                    for res in res_list:
                        r_value = self.get_render_value(f'{{{{{res}}}}}')
                        value = value.replace(f'{{{{{res}}}}}', f'{r_value}')
                    value = self.get_render_value(value)
                except Exception as e:
                    logger.warning(f"db config - render failed {e}")
            except Exception as e:
                logger.warning(f"db config - render failed {e}")
        try:
            value = json.loads(value)
        except Exception as e:
            logger.warning(f"db config - json loads failed {e}")
        if isinstance(value, str):
            if value.isdigit():
                return int(value)
            v_group = re.findall('"(.*?)"', value)
            if v_group and len(v_group) == 1 and v_group[0].isdigit():
                return int(v_group[0])
        return value

    def get_value_from_db(self, key):
        data = self.serializer(self.model.objects.filter(enable=True, key=key).first()).data
        if re.findall('{{.*%s.*}}' % data['key'], data['value']):
            logger.warning(f"get same render key:{key}. so get default value")
            data['key'] = ''
        return data

    def get_default_data(self, key, default_data):
        if default_data is None:
            default_data = {}
        return default_data

    def get_value(self, key, data=None):
        data = self.get_default_data(key, data)
        cache = self.cache(f'{self.px}_{key}')
        cache_data = cache.get_storage_cache()
        if cache_data is not None and cache_data.get('key', '') == key:
            return cache_data.get('value')
        db_data = self.get_value_from_db(key)
        d_key = db_data.get('key', '')
        if d_key != key and data is not None:
            db_data['value'] = json.dumps(data)
            db_data['key'] = key
        db_data['value'] = self.get_render_value(db_data['value'])
        cache.set_storage_cache(db_data, timeout=self.timeout)
        return db_data.get('value')

    def save_db(self, key, value, enable, description, **kwargs):
        defaults = {'value': value}
        if enable is not None:
            defaults['enable'] = enable
        if description is not None:
            defaults['description'] = description
        self.model.objects.update_or_create(key=key, defaults=defaults, **kwargs)

    def delete_db(self, key, **kwargs):
        self.model.objects.filter(key=key, **kwargs).delete()

    def set_value(self, key, value, enable=None, description=None, **kwargs):
        if not isinstance(value, str):
            value = json.dumps(value)
        self.save_db(key, value, enable, description, **kwargs)
        self.cache(f'{self.px}_{key}').del_storage_cache()

    def set_default_value(self, key, **kwargs):
        self.set_value(key, self.get_value(key, None), **kwargs)

    def del_value(self, key, **kwargs):
        self.delete_db(key, **kwargs)
        self.cache(f'{self.px}_{key}').del_storage_cache()

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except Exception as e:
            logger.error(f"__getattribute__ Error  {e}  {name}")
            return self.get_value(name)


class DomainConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(DomainConfCache, self).__init__(*args, **kwargs)

    @property
    def API_DOMAIN(self):
        return self.get_value('API_DOMAIN', DOMAINCONF.API_DOMAIN)

    @property
    def MOBILEPROVISION(self):
        return self.get_value('MOBILEPROVISION', DOMAINCONF.MOBILEPROVISION)

    @property
    def WEB_DOMAIN(self):
        return self.get_value('WEB_DOMAIN', DOMAINCONF.WEB_DOMAIN)


class BaseConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(BaseConfCache, self).__init__(*args, **kwargs)

    @property
    def POST_UDID_DOMAIN(self):
        return self.get_value('POST_UDID_DOMAIN', self.API_DOMAIN)

    @property
    def FILE_UPLOAD_DOMAIN(self):
        return self.get_value('FILE_UPLOAD_DOMAIN', self.API_DOMAIN)

    @property
    def WECHAT_WEB_SUCCESS_REDIRECT_URI(self):
        return self.get_value('WECHAT_WEB_SUCCESS_REDIRECT_URI', self.WEB_DOMAIN)

    @property
    def WECHAT_WEB_LOGIN_REDIRECT_DOMAIN(self):
        return self.get_value('WECHAT_WEB_LOGIN_REDIRECT_DOMAIN', self.API_DOMAIN)

    @property
    def IOS_PMFILE_DOWNLOAD_DOMAIN(self):
        # 验证码，ios 描述文件和plist文件下载域名，该域名用于后端，一般为api访问域名
        return {
            "domain_name": self.API_DOMAIN.split("://")[1],
            'is_https': True if self.API_DOMAIN.split("://")[0] == "https" else False,
        }


class IpaConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(IpaConfCache, self).__init__(*args, **kwargs)

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
        return super().get_value('APPLE_DEVELOPER_API_TIMEOUT', IPACONF.APPLE_DEVELOPER_API_TIMEOUT)


class WechatConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(WechatConfCache, self).__init__(*args, **kwargs)

    @property
    def WECHATAPPLET(self):
        return super().get_value('WECHATAPPLET', THIRDLOGINCONF.wx_applet)

    @property
    def WECHATOFFICIAL(self):
        return super().get_value('WECHATOFFICIAL', THIRDLOGINCONF.wx_official)


class AuthConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(AuthConfCache, self).__init__(*args, **kwargs)

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
        return super().get_value('NOTIFY', AUTHCONF.NOTIFY)

    @property
    def LOGIN(self):
        return super().get_value('LOGIN', AUTHCONF.LOGIN)

    @property
    def REPORT(self):
        return super().get_value('REPORT', AUTHCONF.REPORT)


class GeeTestConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(GeeTestConfCache, self).__init__(*args, **kwargs)

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
    def __init__(self, *args, **kwargs):
        super(UserDownloadTimesCache, self).__init__(*args, **kwargs)

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

    @property
    def SIGN_EXTRA_MULTIPLE(self):
        return super().get_value('SIGN_EXTRA_MULTIPLE', DOWNLOADTIMESCONF.SIGN_EXTRA_MULTIPLE)

    @property
    def APP_USE_BASE_DOWNLOAD_TIMES(self):
        return super().get_value('APP_USE_BASE_DOWNLOAD_TIMES', DOWNLOADTIMESCONF.APP_USE_BASE_DOWNLOAD_TIMES)

    @property
    def PRIVATE_OSS_DOWNLOAD_TIMES(self):
        return super().get_value('PRIVATE_OSS_DOWNLOAD_TIMES', DOWNLOADTIMESCONF.PRIVATE_OSS_DOWNLOAD_TIMES)

    @property
    def APP_FILE_CALCULATION_UNIT(self):
        return super().get_value('APP_FILE_CALCULATION_UNIT', DOWNLOADTIMESCONF.APP_FILE_CALCULATION_UNIT)

    @property
    def OSS_EXCHANGE_DOWNLOAD_TIMES(self):
        return super().get_value('OSS_EXCHANGE_DOWNLOAD_TIMES', DOWNLOADTIMESCONF.OSS_EXCHANGE_DOWNLOAD_TIMES)


class OssStorageConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(OssStorageConfCache, self).__init__(*args, **kwargs)

    @property
    def STORAGE_ALLOW_ENDPOINT(self):
        return super().get_value('STORAGE_ALLOW_ENDPOINT', OSSSTORAGECONF.STORAGE_ALLOW_ENDPOINT)

    @property
    def STORAGE_FREE_CAPACITY(self):
        return super().get_value('STORAGE_FREE_CAPACITY', OSSSTORAGECONF.STORAGE_FREE_CAPACITY)

    @property
    def STORAGE_OSS_CAPACITY(self):
        return super().get_value('STORAGE_OSS_CAPACITY', OSSSTORAGECONF.STORAGE_OSS_CAPACITY)


class PayConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(PayConfCache, self).__init__(*args, **kwargs)

    @property
    def PAY_SUCCESS_URL(self):
        return super().get_value('PAY_SUCCESS_URL', PAYCONF.PAY_SUCCESS_URL)

    @property
    def APP_NOTIFY_URL(self):
        return super().get_value('APP_NOTIFY_URL', PAYCONF.APP_NOTIFY_URL)

    @property
    def PAY_CONFIG_KEY_INFO(self):
        return super().get_value('PAY_CONFIG_KEY_INFO', PAYCONF.PAY_CONFIG_KEY_INFO)


class ThirdStorageConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(ThirdStorageConfCache, self).__init__(*args, **kwargs)

    @property
    def STORAGE(self):
        return super().get_value('STORAGE', STORAGEKEYCONF.STORAGE)


class ThirdPartConfCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(ThirdPartConfCache, self).__init__(*args, **kwargs)

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
    def __init__(self, *args, **kwargs):
        super(AppleDeveloperConfCache, self).__init__(*args, **kwargs)

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

    @property
    def DEVELOPER_WAIT_ABNORMAL_DEVICE(self):
        return super().get_value('DEVELOPER_WAIT_ABNORMAL_DEVICE', APPLEDEVELOPERCONF.DEVELOPER_WAIT_ABNORMAL_DEVICE)

    @property
    def DEVELOPER_ABNORMAL_DEVICE_WRITE(self):
        return super().get_value('DEVELOPER_ABNORMAL_DEVICE_WRITE', APPLEDEVELOPERCONF.DEVELOPER_ABNORMAL_DEVICE_WRITE)

    @property
    def DEVELOPER_WAIT_STATUS(self):
        return super().get_value('DEVELOPER_WAIT_STATUS', APPLEDEVELOPERCONF.DEVELOPER_WAIT_STATUS)

    @property
    def DEVELOPER_WAIT_ABNORMAL_STATE(self):
        return super().get_value('DEVELOPER_WAIT_ABNORMAL_STATE', APPLEDEVELOPERCONF.DEVELOPER_WAIT_ABNORMAL_STATE)

    @property
    def DEVELOPER_RESIGN_STATUS(self):
        return super().get_value('DEVELOPER_RESIGN_STATUS', APPLEDEVELOPERCONF.DEVELOPER_RESIGN_STATUS)


class UserPersonalConfKeyCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(UserPersonalConfKeyCache, self).__init__(*args, **kwargs)

    @property
    def DEVELOPER_STATUS_CONFIG(self):
        return super().get_value('DEVELOPER_STATUS_CONFIG', USERPERSONALCONFIGKEY.DEVELOPER_STATUS_CONFIG)


class ConfigDescriptionCache(ConfigCacheBase):
    def __init__(self, *args, **kwargs):
        super(ConfigDescriptionCache, self).__init__(*args, **kwargs)

    @property
    def DEVELOPER_WAIT_ABNORMAL_DEVICE_DES(self):
        return super().get_value('DEVELOPER_WAIT_ABNORMAL_DEVICE_DES',
                                 CONFIGDESCRIPTION.DEVELOPER_WAIT_ABNORMAL_DEVICE_DES)

    @property
    def DEVELOPER_ABNORMAL_DEVICE_WRITE_DES(self):
        return super().get_value('DEVELOPER_ABNORMAL_DEVICE_WRITE_DES',
                                 CONFIGDESCRIPTION.DEVELOPER_ABNORMAL_DEVICE_WRITE_DES)

    @property
    def DEVELOPER_WAIT_ABNORMAL_STATE_DES(self):
        return super().get_value('DEVELOPER_WAIT_ABNORMAL_STATE_DES',
                                 CONFIGDESCRIPTION.DEVELOPER_WAIT_ABNORMAL_STATE_DES)


class ConfigCache(BaseConfCache, DomainConfCache, IpaConfCache, AuthConfCache, UserDownloadTimesCache, GeeTestConfCache,
                  PayConfCache, ThirdStorageConfCache, ThirdPartConfCache, AppleDeveloperConfCache,
                  UserPersonalConfKeyCache, ConfigDescriptionCache, WechatConfCache, OssStorageConfCache):
    def __init__(self, *args, **kwargs):
        super(ConfigCache, self).__init__(*args, **kwargs)


Config = ConfigCache()


class UserConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPersonalConfig
        fields = "__all__"


class UserPersonalConfigCache(ConfigCache):
    def __init__(self, user_obj):
        self.user_obj = user_obj
        super().__init__(f'user_{user_obj.uid}', UserPersonalConfig, UserSystemConfigCache, UserConfigSerializer)

    def get_default_data(self, key, default_data):
        n_data = getattr(Config, key)
        if n_data is None:
            n_data = {}
        return n_data

    def delete_db(self, key, **kwargs):
        super(UserPersonalConfigCache, self).delete_db(key, user_id=self.user_obj)

    def save_db(self, key, value, enable=None, description=None, **kwargs):
        super(UserPersonalConfigCache, self).save_db(key, value, enable, description, user_id=self.user_obj)

    def set_default_value(self, key, **kwargs):
        super(UserPersonalConfigCache, self).set_default_value(key, user_id=self.user_obj)


UserConfig = UserPersonalConfigCache
