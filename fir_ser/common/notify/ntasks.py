#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: ntasks
# author: liuyu
# data: 2022/3/26
import datetime
import logging

from api.utils.modelutils import get_notify_wx_queryset, get_wx_nickname
from common.base.magic import magic_wrapper, magic_notify
from common.cache.storage import NotifyLoopCache
from common.core.sysconfig import Config
from common.libs.mp.wechat import WxTemplateMsg
from common.notify.utils import notify_by_email
from xsign.models import AppIOSDeveloperInfo
from xsign.utils.modelutils import get_developer_devices

logger = logging.getLogger(__name__)


def download_times_not_enough(user_obj, msg):
    """
    1, '下载次数不足'
    :param msg:
    :param user_obj:
    :return:
    """
    message_type = 1
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, get_wx_nickname(wx_user_obj.openid)).download_times_not_enough_msg(
            user_obj.first_name, user_obj.download_times, msg)
        logger.info(f'user_obj {user_obj} download times not enough result: {res}')
    notify_by_email(user_obj, message_type, msg)


def apple_developer_devices_not_enough(user_obj, device_count):
    """
    0, '签名余额不足'
    :param user_obj:
    :return:
    """
    message_type = 0
    msg = f"您当前账户超级签名可用设备仅剩 {device_count}，已超过您设置的阈值 {user_obj.notify_available_signs}，为了避免业务使用，望您尽快添加苹果开发者!"
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid,
                            get_wx_nickname(wx_user_obj.openid)).apple_developer_devices_not_enough_msg(
            user_obj.first_name, device_count, msg)
        logger.info(f'user_obj {user_obj} sign devices not enough result: {res}')
    notify_by_email(user_obj, message_type, msg)


def apple_developer_cert_expired(user_obj, developer_queryset):
    """
    6, '证书到期消息'
    :param developer_queryset:
    :param user_obj:
    :return:
    """
    message_type = 6
    developer_count = developer_queryset.count()
    developer_obj = developer_queryset.first()
    expired_time = developer_obj.cert_expire_time.strftime("%Y年%m月%d")
    if developer_count == 1:
        issuer_id = developer_obj.issuer_id
        cert_id = developer_obj.certid
        msg = f"用户 {user_obj.first_name} 您好，您苹果开发者 {issuer_id} ，证书 {cert_id} 即将到期，到期时间 {expired_time}，为了保证您开发者可用，请您尽快更新开发者证书，感谢您的关注"
    else:
        issuer_id = f'{developer_obj.issuer_id} 等 {developer_count} 个开发者ID'
        cert_id = f'{developer_obj.certid} 等 {developer_count} 个证书ID'
        msg = f"用户 {user_obj.first_name} 您好，您苹果开发者 {issuer_id} ，证书 {cert_id} 即将到期，到期时间 {expired_time}，为了保证您开发者可用，请您尽快更新开发者证书，感谢您的关注 "

    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, get_wx_nickname(wx_user_obj.openid)).cert_expired_msg(issuer_id,
                                                                                                      cert_id,
                                                                                                      expired_time)
        logger.info(f'user_obj {user_obj} apple developer cert expired result: {res}')

    notify_by_email(user_obj, message_type, msg)


def check_user_download_times(user_obj, days=None):
    if days is None:
        days = [0, 3, 7]
    if user_obj.notify_available_downloads == 0 or user_obj.notify_available_downloads < user_obj.download_times:
        return
    msg = f"您当前账户下载次数仅剩 {user_obj.download_times}，已超过您设置的阈值 {user_obj.notify_available_downloads}，为了避免业务使用，望您尽快充值!"
    notify_rules = [
        {
            'func': magic_wrapper(lambda obj: obj.download_times < obj.notify_available_downloads, user_obj),
            'notify': days,
            'cache': NotifyLoopCache(user_obj.uid, 'download_times'),
            'notify_func': [magic_wrapper(download_times_not_enough, user_obj, msg)]
        }
    ]
    magic_notify(notify_rules)


def check_apple_developer_devices(user_obj, days=None):
    if days is None:
        days = [0, 3, 7]
    developer_queryset = AppIOSDeveloperInfo.objects.filter(user_id=user_obj)
    if developer_queryset.count() == 0:
        return
    developer_used_info = get_developer_devices(developer_queryset)
    device_count = developer_used_info.get('can_sign_number', 0)
    if user_obj.notify_available_signs == 0 or device_count > user_obj.notify_available_signs:
        return
    notify_rules = [
        {
            'func': magic_wrapper(lambda obj: device_count < obj.notify_available_signs, user_obj),
            'notify': days,
            'cache': NotifyLoopCache(user_obj.uid, 'sign_device_times'),
            'notify_func': [magic_wrapper(apple_developer_devices_not_enough, user_obj, device_count)]
        }
    ]
    magic_notify(notify_rules)


def check_apple_developer_cert(user_obj, expire_day=7):
    expire_time = datetime.datetime.now() + datetime.timedelta(days=expire_day)
    developer_queryset = AppIOSDeveloperInfo.objects.filter(user_id=user_obj, status__in=Config.DEVELOPER_USE_STATUS,
                                                            cert_expire_time__lte=expire_time).order_by(
        'cert_expire_time')
    if developer_queryset.count() == 0:
        return

    notify_rules = [
        {
            'func': magic_wrapper(lambda: True),
            'notify': [0, 3, 7],
            'cache': NotifyLoopCache(user_obj.uid, 'developer_cert'),
            'notify_func': [magic_wrapper(apple_developer_cert_expired, user_obj, developer_queryset)]
        }
    ]
    magic_notify(notify_rules)
