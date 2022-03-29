#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: notify
# author: liuyu
# data: 2022/3/26
import logging

from api.utils.modelutils import get_notify_wx_queryset
from common.base.baseutils import get_format_time
from common.core.sysconfig import Config
from common.libs.mp.wechat import WxTemplateMsg
from common.notify.utils import notify_by_email

logger = logging.getLogger(__name__)


def pay_success_notify(user_obj, order_obj):
    """
    4, '充值到账提醒'
    :param user_obj:
    :param order_obj:
    :return:
    """
    message_type = 4

    title = f'{order_obj.actual_download_times} 下载次数'
    if order_obj.actual_download_gift_times > 0:
        title = f'{title} 【赠送 {order_obj.actual_download_gift_times}】'
    msg = f"用户 {user_obj.first_name} 您好，{order_obj.description}。您购买了 {title}。感谢有你!"
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, wx_user_obj.nickname).pay_success_msg(
            title,
            f'{str(order_obj.actual_amount / 100)} 元',
            order_obj.get_payment_type_display(),
            order_obj.pay_time.strftime("%Y/%m/%d %H:%M:%S"),
            order_obj.order_number, order_obj.description)
        logger.info(f'user_obj {user_obj} weixin notify pay success result: {res}')

    notify_by_email(user_obj, message_type, msg)


def sign_failed_notify(user_obj, developer_obj, app_obj):
    """
    3, '应用签名失败'
    :return:
    """
    message_type = 3
    now_time = get_format_time().replace('_', ' ')

    msg = Config.MSG_ERROR_DEVELOPER % (
        user_obj.first_name, app_obj.name, now_time, developer_obj.issuer_id, developer_obj.description)

    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, wx_user_obj.nickname).operate_failed_msg(
            user_obj.first_name, f'应用 {app_obj.name} 签名失败了',
            f'开发者{developer_obj.issuer_id} 状态 {developer_obj.get_status_dispaly()}', now_time,
            f'开发者备注：{developer_obj.description}，请登录后台查看具体信息')
        logger.info(f'user_obj {user_obj} weixin notify pay success result: {res}')

    notify_by_email(user_obj, message_type, msg)


def sign_unavailable_developer(user_obj, app_obj):
    """
    3, '应用签名失败'
    :return:
    """
    message_type = 3
    now_time = get_format_time().replace('_', ' ')
    msg = Config.MSG_NOT_EXIST_DEVELOPER % (user_obj.first_name, app_obj.name, now_time)
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, wx_user_obj.nickname).operate_failed_msg(
            user_obj.first_name, f'应用 {app_obj.name} 签名失败了',
            f'苹果开发者总设备量已经超限', now_time, '添加新的苹果开发者或者修改开发者设备数量')
        logger.info(f'user_obj {user_obj} weixin notify pay success result: {res}')

    notify_by_email(user_obj, message_type, msg)


def sign_app_over_limit(user_obj, app_obj, used_num, limit_number):
    """
    0, '签名余额不足'
    :param limit_number:
    :param used_num:
    :param app_obj:
    :param user_obj:
    :return:
    """
    message_type = 2
    now_time = get_format_time().replace('_', ' ')
    msg = Config.MSG_SING_APP_OVER_LIMIT % (user_obj.first_name, app_obj.name, now_time, used_num, limit_number)
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, wx_user_obj.nickname).operate_failed_msg(
            user_obj.first_name, f'应用 {app_obj.name} 签名失败了', f'超过该应用的签名限额 {limit_number}', now_time,
            f'该应用已经使用设备数 {used_num}，已超过您设置该应用的签名限额 {limit_number}，当前已经无法安装新设备，为了避免业务使用，您可以修改该应用签名限额')
        logger.info(f'user_obj {user_obj} sign devices not enough result: {res}')
    notify_by_email(user_obj, message_type, msg)
