#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: constants
# author: liuyu
# date: 2022/4/5

class DeviceStatus(object):
    """
    设备状态: 当开发者设备里面存在 PROCESSING 或 INELIGIBLE 状态时，再次注册的设备状态全部都为 PROCESSING
    """
    DISABLED = 'DISABLED'
    ENABLED = 'ENABLED'
    PROCESSING = 'PROCESSING'
    INELIGIBLE = 'INELIGIBLE'


class AppleDeveloperStatus(object):
    """
        status_choices = ((-1, '疑似被封'), (0, '未激活'), (1, '已激活'), (2, '协议待同意'),
        (3, '维护中'), (4, '证书过期'), (5, '证书丢失'), (6, '设备状态异常'), (99, '状态异常'))

    """
    BAN = -1
    INACTIVATED = 0
    ACTIVATED = 1
    AGREEMENT_NOT_AGREED = 2
    MAINTENANCE = 3
    CERTIFICATE_EXPIRED = 4
    CERTIFICATE_MISSING = 5
    DEVICE_ABNORMAL = 6
    ABNORMAL_STATUS = 99


class SignStatus(object):
    """
        sign_status_choices = ((0, '新设备入库准备'), (1, '设备ID已经注册'), (2, 'bundelid已经注册'),
         (3, '描述文件已经下载'), (4, '已经完成签名打包'))

    """
    SIGNATURE_PREPARE = 0
    DEVICE_REGISTRATION_COMPLETE = 1
    APP_REGISTRATION_COMPLETE = 2
    PROFILE_DOWNLOAD_COMPLETE = 3
    SIGNATURE_PACKAGE_COMPLETE = 4
