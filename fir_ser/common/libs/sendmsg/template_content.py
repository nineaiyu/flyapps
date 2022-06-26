#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: send_template_msg
# author: liuyu
# date: 2022/4/8

from django.template import loader

from common.base.baseutils import get_format_time


def get_pay_success_html_content(user_obj, order_obj, base_download_times=1):
    return loader.render_to_string('pay_success.html',
                                   {
                                       'username': user_obj.first_name,
                                       'order_obj': order_obj,
                                       'base_download_times': base_download_times
                                   })


def get_sign_failed_html_content(user_obj, app_obj, developer_obj, now_time):
    return loader.render_to_string('xsign/app_sign_failed.html',
                                   {
                                       'username': user_obj.first_name,
                                       'app_obj': app_obj,
                                       'developer_obj': developer_obj,
                                       'now_time': now_time
                                   })


def get_sign_unavailable_developer_html_content(user_obj, app_obj, now_time):
    return loader.render_to_string('xsign/apple_developer_unavailable.html',
                                   {
                                       'username': user_obj.first_name,
                                       'app_obj': app_obj,
                                       'now_time': now_time
                                   })


def get_sign_app_over_limit_html_content(user_obj, app_obj, now_time, used_num, limit_number):
    return loader.render_to_string('xsign/app_sign_over_limit.html',
                                   {
                                       'username': user_obj.first_name,
                                       'app_obj': app_obj,
                                       'now_time': now_time,
                                       'used_num': used_num,
                                       'limit_number': limit_number,
                                   })


def get_check_developer_report_html_content(user_obj, developer_obj_list, developer_used_info, yesterday_used_number):
    return loader.render_to_string('xsign/timing_task_notify.html',
                                   {
                                       'username': user_obj.first_name,
                                       'developer_obj_list': developer_obj_list,
                                       'developer_used_info': developer_used_info,
                                       'yesterday_used_number': yesterday_used_number,
                                   })


def get_user_download_times_over_limit_html_content(user_obj, base_download_times=1):
    return loader.render_to_string('download_times_over_limit.html',
                                   {
                                       'username': user_obj.first_name,
                                       'user_obj': user_obj,
                                       'base_download_times': base_download_times,
                                   })


def get_developer_devices_over_limit_html_content(user_obj, device_count):
    return loader.render_to_string('xsign/apple_developer_devices_over_limit.html',
                                   {
                                       'username': user_obj.first_name,
                                       'user_obj': user_obj,
                                       'device_count': device_count,
                                   })


def get_developer_cert_expired_html_content(user_obj, developer_obj_list):
    return loader.render_to_string('xsign/apple_developer_cert_expired.html',
                                   {
                                       'username': user_obj.first_name,
                                       'developer_obj_list': developer_obj_list,
                                   })


def get_user_download_times_not_enough_html_content(user_obj, base_download_times=1):
    return loader.render_to_string('download_times_not_enough.html',
                                   {
                                       'username': user_obj.first_name,
                                       'user_obj': user_obj,
                                       'base_download_times': base_download_times,
                                   })


def get_userinfo_change_html_content(code):
    return loader.render_to_string('userinfo/change_userinfo.html',
                                   {
                                       'now_time': get_format_time().replace('_', ' '),
                                       'code': code,
                                   })


def get_userinfo_change_code_html_content(code):
    return loader.render_to_string('userinfo/change_userinfo.html',
                                   {
                                       'now_time': get_format_time().replace('_', ' '),
                                       'code': code,
                                   })


def get_code_notify_html_content(code):
    return loader.render_to_string('userinfo/code_notify.html',
                                   {
                                       'now_time': get_format_time().replace('_', ' '),
                                       'code': code,
                                   })


def get_userinfo_login_code_html_content(code):
    return loader.render_to_string('userinfo/login_code.html',
                                   {
                                       'now_time': get_format_time().replace('_', ' '),
                                       'code': code,
                                   })


def get_userinfo_register_code_html_content(code):
    return loader.render_to_string('userinfo/register_code.html',
                                   {
                                       'now_time': get_format_time().replace('_', ' '),
                                       'code': code,
                                   })


def get_userinfo_reset_pwd_html_content(code):
    return loader.render_to_string('userinfo/reset_password.html',
                                   {
                                       'now_time': get_format_time().replace('_', ' '),
                                       'code': code,
                                   })
