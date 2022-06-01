#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: notify
# author: liuyu
# date: 2022/3/26
import logging

from api.utils.modelutils import get_notify_wx_queryset, get_wx_nickname
from common.base.baseutils import get_format_time
from common.base.magic import magic_call_in_times
from common.libs.mp.wechat import WxTemplateMsg
from common.libs.sendmsg.template_content import get_pay_success_html_content, get_sign_failed_html_content, \
    get_sign_unavailable_developer_html_content, get_sign_app_over_limit_html_content, \
    get_check_developer_report_html_content, get_user_download_times_not_enough_html_content
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
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, get_wx_nickname(wx_user_obj.openid)).pay_success_msg(
            title,
            f'{str(order_obj.actual_amount / 100)} 元',
            order_obj.get_payment_type_display(),
            order_obj.pay_time.strftime("%Y/%m/%d %H:%M:%S"),
            order_obj.order_number, order_obj.description)
        logger.info(f'user_obj {user_obj} weixin notify pay success result: {res}')

    notify_by_email(user_obj, message_type, get_pay_success_html_content(user_obj, order_obj))


@magic_call_in_times(key=lambda *x: x[0].uid)
def sign_failed_notify(user_obj, developer_obj, app_obj):
    """
    3, '应用签名失败'
    :return:
    """
    message_type = 3
    now_time = get_format_time().replace('_', ' ')

    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, get_wx_nickname(wx_user_obj.openid)).operate_failed_msg(
            user_obj.first_name, f'应用 {app_obj.name} 签名失败了',
            f'开发者{developer_obj.issuer_id} 状态 {developer_obj.get_status_display()}', now_time,
            f'开发者备注：{developer_obj.description}，请登录后台查看具体信息')
        logger.info(f'user_obj {user_obj} sign_failed_notify result: {res}')

    notify_by_email(user_obj, message_type, get_sign_failed_html_content(user_obj, app_obj, developer_obj, now_time))


@magic_call_in_times(key=lambda *x: x[0].uid)
def sign_unavailable_developer_notify(user_obj, app_obj):
    """
    3, '应用签名失败'
    :return:
    """
    message_type = 3
    now_time = get_format_time().replace('_', ' ')
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, get_wx_nickname(wx_user_obj.openid)).operate_failed_msg(
            user_obj.first_name, f'应用 {app_obj.name} 签名失败了',
            f'苹果开发者总设备量已经超限', now_time, '添加新的苹果开发者或者修改开发者设备数量')
        logger.info(f'user_obj {user_obj} sign_unavailable_developer result: {res}')

    notify_by_email(user_obj, message_type, get_sign_unavailable_developer_html_content(user_obj, app_obj, now_time))


@magic_call_in_times(key=lambda *x: x[0].uid)
def sign_app_over_limit_notify(user_obj, app_obj, used_num, limit_number):
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
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        res = WxTemplateMsg(wx_user_obj.openid, get_wx_nickname(wx_user_obj.openid)).operate_failed_msg(
            user_obj.first_name, f'应用 {app_obj.name} 签名失败了', f'超过该应用的签名限额 {limit_number}', now_time,
            f'该应用已经使用设备数 {used_num}，已超过您设置该应用的签名限额 {limit_number}，当前已经无法安装新设备，为了避免业务使用，您可以修改该应用签名限额')
        logger.info(f'user_obj {user_obj} sign devices not enough result: {res}')
    notify_by_email(user_obj, message_type,
                    get_sign_app_over_limit_html_content(user_obj, app_obj, now_time, used_num, limit_number))


def check_developer_status_notify(user_obj, developer_obj_list, developer_used_info, yesterday_used_number):
    """
    7, '系统提醒'

    :return:
    """
    message_type = 7
    now_time = get_format_time().replace('_', ' ')
    status_msg = {}
    for developer_obj in developer_obj_list:
        status = developer_obj.get_status_display()
        status_msg[status] = status_msg.get(status, 0) + 1

    msg = []
    for key, value in status_msg.items():
        msg.append(f'{value}个{key}状态')
    description = f'开发者状态 {",".join(msg)}。详细信息请查看邮件通知或者登录后台查看'
    for wx_user_obj in get_notify_wx_queryset(user_obj, message_type):
        nick_name = get_wx_nickname(wx_user_obj.openid)
        title = f'你好，“{nick_name}“，苹果开发者状态检测结果'
        res = WxTemplateMsg(wx_user_obj.openid, nick_name).task_finished_msg(title, '苹果开发者状态检测', '完成',
                                                                             now_time, description)
        logger.info(f'user_obj {user_obj} sign devices not enough result: {res}')
    notify_by_email(user_obj, message_type,
                    get_check_developer_report_html_content(user_obj, developer_obj_list, developer_used_info,
                                                            yesterday_used_number))


@magic_call_in_times(key=lambda *x: x[0].uid)
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
    notify_by_email(user_obj, message_type, get_user_download_times_not_enough_html_content(user_obj))
