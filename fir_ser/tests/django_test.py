#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2022/3/9

import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fir_ser.settings')
django.setup()

from xsign.utils.ctasks import auto_check_ios_developer_active

# userinfo = UserInfo.objects.first()
# developer_obj_list = AppIOSDeveloperInfo.objects.all()
# aa = []
# for i in range(22):
#     aa.append(developer_obj_list.first())
# content = loader.render_to_string('check_developer.html',
#                                   {'username': userinfo.first_name, 'developer_obj_list': aa})
#
# send_ios_developer_active_status(userinfo, content)
auto_check_ios_developer_active()
