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
# from common.libs.apple.appleapiv3 import AppStoreConnectApi
# from xsign.models import AppIOSDeveloperInfo
#
# developer_obj = AppIOSDeveloperInfo.objects.filter(issuer_id='4257ad34-8fe8-4200-a827-5b09d9888371').first()
# apple_obj = AppStoreConnectApi(developer_obj.issuer_id, developer_obj.private_key_id, developer_obj.p8key)
# all_devices = apple_obj.get_all_devices()
# for device in all_devices:
#     print(device)

# res=apple_obj.disabled_device('ZZ4F3RM9H2','iPhone13,2','00008101-001560D00A60001E')
# print(res)
