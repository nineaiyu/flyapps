#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2022/3/9
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fir_ser.settings')
django.setup()

# from xsign.utils.ctasks import auto_check_ios_developer_active

# userinfo = UserInfo.objects.first()
# developer_obj_list = AppIOSDeveloperInfo.objects.all()
# aa = []
# for i in range(22):
#     aa.append(developer_obj_list.first())
# content = loader.render_to_string('check_developer.html',
#                                   {'username': userinfo.first_name, 'developer_obj_list': aa})
#
# send_ios_developer_active_status(userinfo, content)
# auto_check_ios_developer_active()
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

# to_user = 'opTae6mrV-MY1UOLahIVXaCDJhUU'
# wx_user_obj = ThirdWeChatUserInfo.objects.filter(openid=to_user).first()

# res = WxTemplateMsg().download_times_not_enough_msg(to_user, wx_user_obj.nickname, wx_user_obj.user_id.first_name,
#                                                     wx_user_obj.user_id.download_times)
# print(res)
# developer_obj = AppIOSDeveloperInfo.objects.filter(issuer_id='4257ad34-8fe8-4200-a827-5b09d9888371').first()
# otherStyleTime = developer_obj.cert_expire_time.strftime("%Y年%m月%d")
#
# res = WxTemplateMsg().cert_expired_msg(to_user, wx_user_obj.nickname, developer_obj.issuer_id, developer_obj.certid, otherStyleTime)
# print(res)
#
# user_obj = UserInfo.objects.filter(uid='47ed855a8e6411ec83f100163e1bfc45').first()
# order_obj = Order.objects.filter(order_number='12022323155915437216374686').first()
# for wx_user_obj in ThirdWeChatUserInfo.objects.filter(subscribe=True, user_id=user_obj).all():
#     res = WxTemplateMsg().pay_success_msg(wx_user_obj.openid, wx_user_obj.nickname,
#                                           f'{order_obj.actual_download_times} 下载次数',
#                                           f'{str(order_obj.actual_amount / 100)} 元',
#                                           order_obj.get_payment_type_display(),
#                                           order_obj.pay_time.strftime("%Y/%m/%d %H:%M:%S"),
#                                           order_obj.order_number, order_obj.description)
#
# a = WeChatInfo.objects.filter(openid='11').values('nickname')
# print(a)
#
from api.models import *
app_obj = Apps.objects.first()
print(app_obj.updated_time)
app_obj.description='111'
app_obj.save(update_fields=["description","updated_time"])
app_obj = Apps.objects.first()
print(app_obj.updated_time)
# from common.notify.wx import check_apple_developer_devices
#
# user_obj = UserInfo.objects.filter(uid='47ed855a8e6411ec83f100163e1bfc45').first()
# wx_user_obj_queryset = ThirdWeChatUserInfo.objects.filter(enable_login=True).all()
# print(wx_user_obj_queryset.values('user_id__id'))
# wx_user_obj_queryset = ThirdWeChatUserInfo.objects.filter(openid='opTae6mrV-MY1UOLahIVXaCDJhUU').filter(
#     Q(enable_login=True) | Q(enable_notify=True)).all()
# for wx_obj in wx_user_obj_queryset:
#     print(wx_obj.__dict__)
# ThirdWeChatUserInfo.objects.filter().delete()
# class AesBaseCrypt(object):
#
#     def __init__(self):
#         print(self.__class__.__name__)
#         self.cipher = AESCipher(self.__class__.__name__)
#
#     def get_encrypt_uid(self, raw):
#         return self.cipher.encrypt(raw.encode('utf-8')).decode('utf-8')
#
#     def get_decrypt_uid(self, enc):
#         return self.cipher.decrypt(enc)
#
#
# class AppleDeveloperUid(AesBaseCrypt):
#     pass
# class aaaa():
#     def __init__(self):
#         self.a=11
#
# obj = aaaa()
# def cc(obj):
#     obj.a = 222
#
# cc(obj)
# print(obj.a)
# print(AppleDeveloperUid().cipher)
# check_apple_developer_devices(user_obj)
# notify_config_obj = NotifyConfig.objects.create(user_id=user_obj, message_type=0,
#                                                 config_name='下载次数不足3323',
#                                                 enable_email=True, enable_weixin=True, description='次数不足')
# notify_config_obj.sender.set(NotifyReceiver.objects.filter(user_id=user_obj).all())
#
# developer_obj = AppIOSDeveloperInfo.objects.filter(issuer_id='69a6de96-c16e-47e3-e053-5b8c7c11a4d1').first()
#
# res = IosUtils.get_developer_cert_info(developer_obj)
# print(res)
# app_dev_pem = '/data/flyapps/fir_ser/supersign/459a0d8a2b80539f80613db0de775518/459a0d8a2b80539f80613db0de775518.pem'
# cer = load_certificate(FILETYPE_PEM, open(app_dev_pem, 'rb').read())
#
# not_after = datetime.datetime.strptime(cer.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ")
# print(not_after, hex(cer.get_serial_number()), cer.get_serial_number())
# x = '4257FF461CEEBC5CCC83225192AC5518'
# print(int(x, 16))
#
# udid_result_list = [1, 2, 3, 4, 5, 6, 7, 8]
# udid_developer_list = [2, 3, 4, 5, 6]
# udid_same = set(udid_result_list) & set(udid_developer_list)
# same_p = (len(udid_same) / len(udid_result_list) + len(udid_same) / len(udid_developer_list)) / 2
# print(same_p, same_p < 0.8)
