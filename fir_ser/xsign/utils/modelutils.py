#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: NinEveN
# date: 2021/4/16


import logging

from django.db.models import Count, Sum, Q

from api.models import AppReleaseInfo, UserInfo
from common.base.baseutils import is_valid_phone
from common.constants import SignStatus, AppleDeveloperStatus
from common.core.sysconfig import Config, UserConfig
from xsign.models import APPSuperSignUsedInfo, UDIDsyncDeveloper, AppUDID, APPToDeveloper, AppIOSDeveloperInfo, \
    IosDeveloperPublicPoolBill, IosDeveloperBill, DeveloperDevicesID, AppleDeveloperToAppUse, DeveloperAppID, \
    AppleSignMessage, DeviceAbnormalUDID

logger = logging.getLogger(__name__)


def get_ios_developer_public_num(user_obj):
    add_number = get_user_public_sign_num(user_obj)
    if not add_number:
        add_number = -99
    used_number = get_user_public_used_sign_num(user_obj)
    return add_number - used_number


def get_user_public_sign_num(user_obj):
    add_number = IosDeveloperBill.objects.filter(to_user_id=user_obj, status=2).aggregate(
        number=Sum('number'))
    number = add_number.get("number", 0)
    return number if number else 0


def get_user_public_used_sign_num(user_obj):
    used_number = IosDeveloperPublicPoolBill.objects.filter(user_id=user_obj, udid_sync_info__isnull=False).exclude(
        udid_sync_info__developerid__user_id=user_obj).values('number',
                                                              'udid_sync_info_id').annotate(
        counts=Count('udid_sync_info_id')).aggregate(number=Sum('number'))
    number = used_number.get("number", 0)
    return number if number else 0


# def get_developer_can_used_from_public_sign(user_obj):
#     o_number_info = IosDeveloperBill.objects.filter(to_user_id__isnull=False, user_id=user_obj).values(
#         'number').aggregate(number=Sum('number'))
#     o_number = o_number_info.get("number", 0)
#     if o_number is None:
#         o_number = 0
#     u_number_info = IosDeveloperPublicPoolBill.objects.filter(
#         user_id_id__in=IosDeveloperBill.objects.filter(user_id=user_obj).values('to_user_id_id')).values(
#         'number',
#         'udid_sync_info_id').annotate(
#         counts=Count('udid_sync_info_id')).aggregate(number=Sum('number'))
#     u_number = u_number_info.get("number", 0)
#     if u_number is None:
#         u_number = 0
#     return o_number - u_number


def check_super_sign_permission(user_obj):
    if not user_obj.supersign_active:
        return False
    developer_count = AppIOSDeveloperInfo.objects.filter(user_id=user_obj).count()
    if developer_count == 0 and get_ios_developer_public_num(user_obj) < 0:
        return False
    return True


def check_ipa_is_latest_sign(app_obj, developer_obj=None):
    if AppUDID.objects.filter(app_id=app_obj, udid__developerid=developer_obj,
                              sign_status__lt=SignStatus.SIGNATURE_PACKAGE_COMPLETE).first():
        return
    release_obj = AppReleaseInfo.objects.filter(app_id=app_obj, is_master=True).first()
    all_app_to_dev = APPToDeveloper.objects.filter(app_id=app_obj)
    if developer_obj:
        all_app_to_dev = all_app_to_dev.filter(developerid=developer_obj)
    all_app_to_dev = all_app_to_dev.all()
    t_count = 0
    for apptodev_obj in all_app_to_dev:
        if release_obj.release_id == apptodev_obj.release_file:
            t_count += 1
    if t_count == all_app_to_dev.count():
        return True


def get_developer_udided(developer_obj):
    super_sing_used_obj = APPSuperSignUsedInfo.objects.filter(developerid=developer_obj).all()
    udid_sync_developer_obj = UDIDsyncDeveloper.objects.filter(developerid=developer_obj).all()
    developer_udid_lists = []
    super_sign_udid_lists = []
    if udid_sync_developer_obj:
        developer_udid_lists = list(udid_sync_developer_obj.values_list("udid"))
    if super_sing_used_obj:
        super_sign_udid_lists = list(super_sing_used_obj.values_list("udid__udid__udid"))
    return len(set(developer_udid_lists) - set(super_sign_udid_lists)), len(set(super_sign_udid_lists)), len(
        set(developer_udid_lists))


def update_or_create_developer_udid_info(device_obj, developer_obj):
    device = {
        "serial": device_obj.id,
        "product": device_obj.name,
        "udid": device_obj.udid,
        "version": device_obj.model,
        "status": device_obj.status
    }
    return UDIDsyncDeveloper.objects.update_or_create(developerid=developer_obj, udid=device_obj.udid, defaults=device)


def check_uid_has_relevant(user_uid, to_user_uid):
    if user_uid and to_user_uid:
        return IosDeveloperBill.objects.filter(user_id__uid=user_uid, to_user_id__uid=to_user_uid, status=2).first()


def usable_number(developer_obj):
    d_count = UDIDsyncDeveloper.objects.filter(developerid=developer_obj).count()
    u_count = developer_obj.usable_number
    return d_count if d_count > u_count else u_count


def get_use_number(developer_obj):
    return DeveloperDevicesID.objects.filter(developerid=developer_obj).values('udid').distinct().count()


def get_developer_devices(developer_obj_lists, user_obj):
    developer_obj_lists = developer_obj_lists.filter(status__in=Config.DEVELOPER_USE_STATUS).all()
    result_info = []
    for dev_obj in developer_obj_lists:
        other_used, flyapp_used, _ = get_developer_udided(dev_obj)
        result_info.append({
            'other_used': other_used,
            'flyapp_used': flyapp_used,
            'usable_number': usable_number(dev_obj),
            'use_number': get_use_number(dev_obj),
            'status': dev_obj.status,
            'abnormal_register': dev_obj.abnormal_register
        })

    use_num = {
        "all_usable_number": 0,  # 可用的设备数
        "all_use_number": 0,  # 已经使用的设备数 【通过设备ID】
        "other_used_sum": 0,  # 开发者已经使用，但是平台未使用设备数
        "flyapp_used_sum": 0,  # 平台已经使用的设备数【通过设备安装详情】
        "can_sign_number": 0,  # 可以被用来签名数【状态为1】
        "used_sign_number": 0,  # 已被用来签名数【状态为1】
        "may_sign_number": 0,  # 可以被用来签名数
        "can_other_used": 0,  # 开发者已经使用，但是平台未使用设备数【状态为1】
        "used_number": 0,  # 可用的设备数【状态为1】
        "max_total": 100 * len(result_info)
    }

    developer_status = Config.DEVELOPER_SIGN_STATUS
    if UserConfig(user_obj).DEVELOPER_WAIT_ABNORMAL_DEVICE and UserConfig(user_obj).DEVELOPER_ABNORMAL_DEVICE_WRITE:
        developer_status.append(AppleDeveloperStatus.DEVICE_ABNORMAL)

    for info in result_info:
        use_num['other_used_sum'] += info['other_used']
        use_num['flyapp_used_sum'] += info['flyapp_used']
        use_num['all_usable_number'] += info['usable_number']
        use_num['all_use_number'] += info['use_number']
        if info['status'] in developer_status and info['abnormal_register']:
            use_num['can_sign_number'] += (info['usable_number'] - info['flyapp_used'] - info['other_used'])
            use_num['used_sign_number'] += info['usable_number']
            use_num['can_other_used'] += info['other_used']
            use_num['used_number'] += info['use_number']
        use_num['may_sign_number'] += (info['usable_number'] - info['flyapp_used'] - info['other_used'])

    return use_num


def get_user_obj_from_epu(user_id):
    if is_valid_phone(user_id):
        user_obj = UserInfo.objects.filter(mobile=user_id).first()
    else:
        user_obj = UserInfo.objects.filter(Q(email=user_id) | Q(uid=user_id)).first()
    return user_obj


def get_app_sign_info(app_obj):
    return {
        'count': APPToDeveloper.objects.filter(app_id=app_obj).count(),
        'private_developer_number': AppleDeveloperToAppUse.objects.filter(app_id=app_obj).count(),
        'supersign_used_number': APPSuperSignUsedInfo.objects.filter(app_id=app_obj).all().count(),
        'developer_used_count': DeveloperAppID.objects.filter(app_id=app_obj).all().count(),
        'private_developer_used_number': DeveloperDevicesID.objects.filter(app_id=app_obj,
                                                                           developerid__appledevelopertoappuse__app_id=app_obj).distinct().count()
    }


def get_filename_form_file(filename):
    file_id_list = filename.split('.')
    check = False
    if file_id_list[-1] in ['ipa']:
        app_to_obj = APPToDeveloper.objects.filter(binary_file='.'.join(file_id_list[0:-1])).first()
        if app_to_obj:
            app_obj = app_to_obj.app_id
            if app_obj.type == 0:
                f_type = '.apk'
            else:
                f_type = '.ipa'
            filename = f"{app_obj.name}-sign-{app_obj.short}{f_type}"
            check = True
    return check, filename


def add_sign_message(user_obj, developer_obj, app_obj, title, message, is_success):
    if app_obj:
        title = f'应用【{app_obj.name}】 {title}'
    AppleSignMessage.objects.create(user_id=user_obj, developerid=developer_obj, app_id=app_obj,
                                    title=title, message=message, operate_status=is_success)


def sync_abnormal_device(developer_obj, udid):
    DeviceAbnormalUDID.objects.filter(auto_remove=True, udid__udid=udid, udid__developerid=developer_obj).delete()


def update_or_create_abnormal_device(sync_device_obj, user_obj, app_obj, client_ip):
    defaults = {
        "description": f"签名应用【{app_obj.name}】 客户端IP地址:【{client_ip}】",
    }
    return DeviceAbnormalUDID.objects.update_or_create(user_id=user_obj, udid=sync_device_obj, defaults=defaults)
