#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月
# author: liuyu
# date: 2020/5/7
import binascii
import datetime
import logging
import os

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.core.cache import cache

from api.models import APPSuperSignUsedInfo, APPToDeveloper, \
    UDIDsyncDeveloper, UserInfo, AppReleaseInfo, AppScreenShot, Token, DeveloperDevicesID, UserAdDisplayInfo
from api.utils.TokenManager import generate_numeric_token_of_length, generate_alphanumeric_token_of_length, make_token, \
    verify_token
from api.utils.baseutils import get_real_ip_address
from api.utils.modelutils import get_app_d_count_by_app_id
from api.utils.sendmsg.sendmsg import SendMessage
from api.utils.storage.caches import consume_user_download_times
from api.utils.storage.localApi import LocalStorage
from api.utils.storage.storage import Storage
from api.utils.tempcaches import TmpCache
from fir_ser.settings import SERVER_DOMAIN, CAPTCHA_LENGTH, MEDIA_ROOT, CACHE_KEY_TEMPLATE

logger = logging.getLogger(__name__)


def delete_app_to_dev_and_file(developer_obj, app_id):
    app_to_developer_obj = APPToDeveloper.objects.filter(developerid=developer_obj, app_id_id=app_id)
    if app_to_developer_obj:
        binary_file = app_to_developer_obj.first().binary_file + ".ipa"
        delete_local_files(binary_file)
        storage = Storage(developer_obj.user_id)
        storage.delete_file(binary_file)
        app_to_developer_obj.delete()


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


def usable_number(developer_obj):
    d_count = UDIDsyncDeveloper.objects.filter(developerid=developer_obj).count()
    u_count = developer_obj.usable_number
    return d_count if d_count > u_count else u_count


def get_developer_devices(developer_obj_lists):
    other_used_sum = 0
    flyapp_used_sum = 0
    max_total = 0
    for dev_obj in developer_obj_lists.filter(is_actived=True):
        other_used, flyapp_used, _ = get_developer_udided(dev_obj)
        other_used_sum += other_used
        flyapp_used_sum += flyapp_used
        max_total += 100

    use_number_obj_list = developer_obj_lists.filter(is_actived=True)
    all_use_number = 0
    all_usable_number = 0
    for use_number_obj in use_number_obj_list:
        all_usable_number += usable_number(use_number_obj)
        all_use_number += DeveloperDevicesID.objects.filter(developerid=use_number_obj).values(
            'udid').distinct().count()
    use_num = {
        "all_usable_number": all_usable_number,
        "all_use_number": all_use_number,
        "other_used_sum": other_used_sum,
        "flyapp_used_sum": flyapp_used_sum,
        "max_total": max_total
    }
    return use_num


def get_captcha():
    captcha_key = CaptchaStore.generate_key()
    captcha_image = captcha_image_url(captcha_key)
    CaptchaStore.remove_expired()
    local_storage = LocalStorage(**SERVER_DOMAIN.get("IOS_PMFILE_DOWNLOAD_DOMAIN"))
    return {"captcha_image": "/".join([local_storage.get_base_url(), captcha_image.strip("/"), '']),
            "captcha_key": captcha_key,
            "length": CAPTCHA_LENGTH}


def valid_captcha(captcha_key, code, username):
    if username:
        challenge = CaptchaStore.objects.filter(hashkey=captcha_key).values("challenge").first()
        logger.info(f"captcha_key:{captcha_key} code:{code}  challenge:{challenge}")
        if challenge:
            if captcha_key and code and code.strip(" ").lower() == challenge.get("challenge").lower():
                return True
    return False


def upload_oss_default_head_img(user_obj, storage_obj):
    head_img_full_path = os.path.join(MEDIA_ROOT, "head_img.jpeg")
    if storage_obj:
        storage_obj = Storage(user_obj, storage_obj)
        return storage_obj.upload_file(head_img_full_path)


def get_sender_token(sender, user_id, target, action, msg=None):
    code = generate_numeric_token_of_length(6)
    if msg:
        code = msg
    token = make_token(code, time_limit=300, key=user_id)
    TmpCache.set_tmp_cache(user_id, token, target)
    if action in ('change', 'password', 'register', 'login', 'common'):
        sender.send_msg_by_act(target, code, action)
    elif action == 'msg':
        sender.send_email_msg(target, msg)
    else:
        logger.error(f"get_sender_token failed. action is {action}")
        return None, None
    return token, code


def get_sender_sms_token(key, phone, action, msg=None):
    sender = SendMessage('sms')
    if sender.sender:
        return get_sender_token(sender, key, phone, action, msg)
    return False, False


def is_valid_sender_code(key, token, code, success_once=False):
    return verify_token(token, code, success_once), TmpCache.get_tmp_cache(key, token)


def get_sender_email_token(key, email, action, msg=None):
    sender = SendMessage('email')
    if sender.sender:
        return get_sender_token(sender, key, email, action, msg)
    return False, False


def check_username_exists(username):
    user_obj = UserInfo.objects.filter(username=username).values("username").first()
    if user_obj and user_obj['username'] == username:
        return True
    return False


def get_random_username(length=16):
    username = generate_alphanumeric_token_of_length(length)
    if check_username_exists(username):
        return get_random_username(length)
    return username


def send_ios_developer_active_status(user_info, msg):
    act = 'email'
    email = user_info.email
    if email:
        get_sender_email_token(act, email, 'msg', msg)
    else:
        logger.warning(f"user {user_info} has no email. so {msg} can't send!")


def get_filename_from_apptype(filename, apptype):
    if apptype == 0:
        filename = filename + '.apk'
    else:
        filename = filename + '.ipa'
    return filename


def delete_local_files(filename, apptype=None):
    storage = LocalStorage("localhost", False)
    if apptype is not None:
        filename = get_filename_from_apptype(filename, apptype)
    try:
        return storage.del_file(filename)
    except Exception as e:
        logger.error(f"delete file {filename} failed  Exception  {e}")


def delete_app_screenshots_files(storage_obj, app_obj):
    for screenshot_obj in AppScreenShot.objects.filter(app_id=app_obj).all():
        storage_obj.delete_file(screenshot_obj.screenshot_url)
        screenshot_obj.delete()


def change_storage_and_change_head_img(user_obj, new_storage_obj, clean_old_data=True):
    if user_obj.head_img == 'head_img.jpeg':
        clean_old_data = False
    migrating_storage_file_data(user_obj, user_obj.head_img, new_storage_obj, clean_old_data)
    change_storage_and_change_advert_img(user_obj, new_storage_obj, clean_old_data)


def change_storage_and_change_advert_img(user_obj, new_storage_obj, clean_old_data=True):
    for user_advert_obj in UserAdDisplayInfo.objects.filter(user_id=user_obj):
        migrating_storage_file_data(user_obj, user_advert_obj.ad_pic, new_storage_obj, clean_old_data)


def download_files_form_oss(storage_obj, org_file):
    if storage_obj.download_file(os.path.basename(org_file), org_file + ".check.tmp"):
        if os.path.isfile(org_file) and os.path.exists(org_file + ".check.tmp"):
            os.remove(org_file)
        if os.path.exists(org_file + ".check.tmp"):
            os.rename(os.path.join(org_file + ".check.tmp"), org_file)
            return True
    return False


def check_storage_is_new_storage(user_obj, new_storage_obj):
    old_storage_obj = Storage(user_obj)
    if not new_storage_obj:
        new_storage_obj = Storage(user_obj, None, True)
    else:
        new_storage_obj = Storage(user_obj, new_storage_obj)
    if old_storage_obj.get_storage_uuid() == new_storage_obj.get_storage_uuid():
        return False
    return True


def migrating_storage_file_data(user_obj, filename, new_storage_obj, clean_old_data=True):
    local_file_full_path = os.path.join(MEDIA_ROOT, filename)
    old_storage_obj = Storage(user_obj)
    if not new_storage_obj:
        new_storage_obj = Storage(user_obj, None, True)
    else:
        new_storage_obj = Storage(user_obj, new_storage_obj)

    if old_storage_obj.get_storage_uuid() == new_storage_obj.get_storage_uuid():
        # 同一个存储，无需迁移数据
        return True

    if old_storage_obj.get_storage_type() == 3:
        if new_storage_obj.get_storage_type() == 3:
            # 都是本地存储，无需操作
            pass
        else:
            # 本地向云存储上传,并删除本地数据
            new_storage_obj.upload_file(local_file_full_path)
            if clean_old_data:
                delete_local_files(filename)
    else:
        if new_storage_obj.get_storage_type() == 3:
            # 云存储下载 本地，并删除云存储
            if download_files_form_oss(old_storage_obj, local_file_full_path):
                if clean_old_data:
                    old_storage_obj.delete_file(filename)
        else:
            # 云存储互传，先下载本地，然后上传新云存储，删除本地和老云存储
            if download_files_form_oss(old_storage_obj, local_file_full_path):
                new_storage_obj.upload_file(local_file_full_path)
                delete_local_files(filename)
                if clean_old_data:
                    old_storage_obj.delete_file(filename)


def migrating_storage_data(user_obj, new_storage_obj, clean_old_data):
    with cache.lock("%s_%s" % ('migrating_storage_data', user_obj.uid), timeout=60 * 60 * 24):

        auth_status = False
        certification = getattr(user_obj, 'certification', None)
        if certification and certification.status == 1:
            auth_status = True
        for app_release_obj in AppReleaseInfo.objects.filter(app_id__user_id=user_obj).all():
            # 迁移APP数据
            filename = get_filename_from_apptype(app_release_obj.release_id, app_release_obj.release_type)
            migrating_storage_file_data(user_obj, filename, new_storage_obj, clean_old_data)
            migrating_storage_file_data(user_obj, app_release_obj.icon_url, new_storage_obj, clean_old_data)
            # 迁移APP 截图
            for screenshot_obj in AppScreenShot.objects.filter(app_id=app_release_obj.app_id).all():
                migrating_storage_file_data(user_obj, screenshot_obj.screenshot_url, new_storage_obj, clean_old_data)
            # 迁移超级签数据
            for apptodev_obj in APPToDeveloper.objects.filter(app_id=app_release_obj.app_id).all():
                filename = get_filename_from_apptype(apptodev_obj.binary_file, app_release_obj.release_type)
                migrating_storage_file_data(user_obj, filename, new_storage_obj, clean_old_data)
            # 消费下载次数
            amount = get_app_d_count_by_app_id(app_release_obj.app_id.app_id)
            consume_user_download_times(user_obj.pk, app_release_obj.app_id, amount, auth_status)
        return True


def clean_storage_data(user_obj, storage_obj=None):
    storage_obj = Storage(user_obj, storage_obj)
    logger.info(f"{user_obj} clean_storage_data {storage_obj}")
    for app_release_obj in AppReleaseInfo.objects.filter(app_id__user_id=user_obj).all():
        storage_obj.delete_file(app_release_obj.release_id, app_release_obj.release_type)
        storage_obj.delete_file(app_release_obj.icon_url)
        for screenshot_obj in AppScreenShot.objects.filter(app_id=app_release_obj.app_id).all():
            storage_obj.delete_file(screenshot_obj.screenshot_url)
        for apptodev_obj in APPToDeveloper.objects.filter(app_id=app_release_obj.app_id).all():
            storage_obj.delete_file(apptodev_obj.binary_file, app_release_obj.release_type)
    return True


def get_choices_dict(choices):
    result = []
    choices_org_list = list(choices)
    for choice in choices_org_list:
        result.append({'id': choice[0], 'name': choice[1]})
    return result


def get_choices_name_from_key(choices, key):
    choices_org_list = list(choices)
    for choice in choices_org_list:
        if choice[0] == key:
            return choice[1]
    return ''


def set_user_token(user_obj, request):
    key = binascii.hexlify(os.urandom(32)).decode()
    now = datetime.datetime.now()
    user_info = UserInfo.objects.get(pk=user_obj.pk)
    auth_key = "_".join([CACHE_KEY_TEMPLATE.get('user_auth_token_key'), key])
    cache.set(auth_key, {'uid': user_info.uid, 'username': user_info.username}, 3600 * 24 * 7)
    Token.objects.create(user=user_obj,
                         **{"access_token": key, "created": now, "remote_addr": get_real_ip_address(request)})
    return key, user_info


def clean_user_token_and_cache(user_obj, white_token_list=None):
    if white_token_list is None:
        white_token_list = []
    for token_obj in Token.objects.filter(user=user_obj):
        if token_obj.access_token in white_token_list:
            continue
        auth_key = "_".join([CACHE_KEY_TEMPLATE.get('user_auth_token_key'), token_obj.access_token])
        cache.delete(auth_key)
        token_obj.delete()
