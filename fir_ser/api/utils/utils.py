#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月
# author: liuyu
# date: 2020/5/7
import os, json, requests, datetime, random
from fir_ser.settings import SERVER_DOMAIN, CAPTCHA_LENGTH, MEDIA_ROOT
from api.models import APPSuperSignUsedInfo, APPToDeveloper, \
    UDIDsyncDeveloper, UserInfo, AppReleaseInfo, AppScreenShot
from api.utils.storage.caches import get_app_d_count_by_app_id
from api.utils.storage.localApi import LocalStorage
from api.utils.storage.storage import Storage
from api.utils.tempcaches import tmpCache
from api.utils.TokenManager import DownloadToken, generateNumericTokenOfLength, generateAlphanumericTokenOfLength
from api.utils.sendmsg.sendmsg import SendMessage
from django.db.models import Sum
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from api.utils.storage.caches import consume_user_download_times
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def delete_app_to_dev_and_file(developer_obj, app_id):
    APPToDeveloper_obj = APPToDeveloper.objects.filter(developerid=developer_obj, app_id_id=app_id)
    if APPToDeveloper_obj:
        binary_file = APPToDeveloper_obj.first().binary_file + ".ipa"
        delete_local_files(binary_file)
        storage = Storage(developer_obj.user_id)
        storage.delete_file(binary_file)
        APPToDeveloper_obj.delete()


def get_developer_udided(developer_obj):
    SuperSignUsed_obj = APPSuperSignUsedInfo.objects.filter(developerid=developer_obj)
    UDIDsyncDeveloper_obj = UDIDsyncDeveloper.objects.filter(developerid=developer_obj)
    develoer_udid_lists = []
    supersign_udid_lists = []
    if UDIDsyncDeveloper_obj:
        develoer_udid_lists = list(UDIDsyncDeveloper_obj.values_list("udid"))
    if SuperSignUsed_obj:
        supersign_udid_lists = list(SuperSignUsed_obj.values_list("udid__udid"))
    return len(set(develoer_udid_lists) - set(supersign_udid_lists)), len(develoer_udid_lists)


def get_developer_devices(developer_obj_lists):
    other_used_sum = 0
    flyapp_used_sum = 0
    for dev_obj in developer_obj_lists:
        other_used, flyapp_used = get_developer_udided(dev_obj)
        other_used_sum += other_used
        flyapp_used_sum += flyapp_used

    use_number_obj = developer_obj_lists.filter(is_actived=True)
    if use_number_obj:
        use_number_dict = use_number_obj.aggregate(usable_number=Sum('usable_number'), use_number=Sum('use_number'))
        use_num = {
            "all_usable_number": use_number_dict.get("usable_number", 0),
            "all_use_number": use_number_dict.get("use_number", 0),
            "other_used_sum": other_used_sum,
            "flyapp_used_sum": flyapp_used_sum,
        }
        return use_num


def get_captcha():
    cptch_key = CaptchaStore.generate_key()
    cptch_image = captcha_image_url(cptch_key)
    CaptchaStore.remove_expired()
    local_storage = LocalStorage(**SERVER_DOMAIN.get("IOS_PMFILE_DOWNLOAD_DOMAIN"))
    return {"cptch_image": "/".join([local_storage.get_base_url(), cptch_image.strip("/")]), "cptch_key": cptch_key,
            "length": CAPTCHA_LENGTH}


def valid_captcha(cptch_key, code, username):
    if username:
        challenge = CaptchaStore.objects.filter(hashkey=cptch_key).values("challenge").first()
        logger.info("cptch_key:%s code:%s  challenge:%s" % ((cptch_key, code, challenge)))
        if challenge:
            if cptch_key and code and code.strip(" ").lower() == challenge.get("challenge").lower():
                return True
    return False


def upload_oss_default_head_img(user_obj, storage_obj):
    head_img_full_path = os.path.join(MEDIA_ROOT, "head_img.jpeg")
    if storage_obj:
        storage_obj = Storage(user_obj, storage_obj)
        return storage_obj.upload_file(head_img_full_path)


def get_sender_token(sender, user_id, target, action, msg=None):
    sms_token_obj = DownloadToken()
    code = generateNumericTokenOfLength(6)
    token = sms_token_obj.make_token(code, time_limit=300, key=user_id)
    tmpCache.set_tmp_cache(user_id, token, target)
    if action == 'change':
        sender.send_change_msg(target, code)
    elif action == 'register':
        sender.send_register_msg(target, code)
    elif action == 'login':
        sender.send_login_msg(target, code)
    elif action == 'msg':
        sender.send_email_msg(target, msg)
    else:
        logger.error("get_sender_token failed. action is %s" % (action))
        return None, None
    return token, code


def get_sender_sms_token(key, phone, action):
    sender = SendMessage('sms')
    return get_sender_token(sender, key, phone, action)


def is_valid_sender_code(key, token, code):
    sms_token_obj = DownloadToken()
    return sms_token_obj.verify_token(token, code), tmpCache.get_tmp_cache(key, token)


def get_sender_email_token(key, email, action, msg=None):
    sender = SendMessage('email')
    return get_sender_token(sender, key, email, action, msg)


def check_username_exists(username):
    user_obj = UserInfo.objects.filter(username=username).values("username").first()
    if user_obj and user_obj['username'] == username:
        return True
    return False


def get_random_username(length=16):
    username = generateAlphanumericTokenOfLength(length)
    if check_username_exists(username):
        return get_random_username(length)
    return username


def send_ios_developer_active_status(user_info, msg):
    act = 'email'
    email = user_info.email
    if email:
        get_sender_email_token(act, email, 'msg', msg)
    else:
        logger.warning("user %s has no email. so %s can't send!" % (user_info, msg))


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
        logger.error("delete file  %s  failed  Exception %s" % (filename, e))


def delete_app_screenshots_files(storage_obj, app_obj):
    for screenshot_obj in AppScreenShot.objects.filter(app_id=app_obj).all():
        storage_obj.delete_file(screenshot_obj.screenshot_url)
        screenshot_obj.delete()


def change_storage_and_change_head_img(user_obj, new_storage_obj):
    migrating_storage_file_data(user_obj, user_obj.head_img, new_storage_obj)


def download_files_form_oss(storage_obj, org_file):
    download_url = storage_obj.get_download_url(os.path.basename(org_file), 600, key='check_org_file', force_new=True)
    req = requests.get(download_url)
    if req.status_code == 200:
        logger.info("download  file %s success" % org_file)
    else:
        logger.error("download  file %s failed %s" % (org_file, req.content))
        return False
    try:
        with open(org_file + ".check.tmp", "wb") as f:
            for chunk in req.iter_content(chunk_size=5120):
                if chunk:
                    f.write(chunk)
        logger.info("save download  file %s success" % org_file)
        if os.path.isfile(org_file):
            os.remove(org_file)
        os.rename(os.path.join(org_file + ".check.tmp"), org_file)
        return True
    except Exception as e:
        logger.error("check download file and move file %s failed Exception %s" % (org_file, e))
        return False


def migrating_storage_file_data(user_obj, filename, new_storage_obj, clean_old_data=True):
    local_file_full_path = os.path.join(MEDIA_ROOT, filename)
    old_storage_obj = Storage(user_obj)
    if not new_storage_obj:
        new_storage_obj = Storage(user_obj, None, True)
    else:
        new_storage_obj = Storage(user_obj, new_storage_obj)

    if old_storage_obj.get_storage_type() == new_storage_obj.get_storage_type():
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
    with cache.lock("%s_%s" % ('migrating_storage_data', user_obj.uid)):

        status = user_obj.certification.status
        auth_status = False
        if status and status == 1:
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
    for app_release_obj in AppReleaseInfo.objects.filter(app_id__user_id=user_obj).all():
        storage_obj.delete_file(app_release_obj.release_id, app_release_obj.release_type)
        storage_obj.delete_file(app_release_obj.icon_url)
        for apptodev_obj in APPToDeveloper.objects.filter(app_id=app_release_obj.app_id).all():
            storage_obj.delete_file(apptodev_obj.binary_file, app_release_obj.release_type)
    return True


def get_order_num(order_type=1):
    now = datetime.datetime.now()
    date_str = "{0}{1}{2}{3}{4}{5}{6}".format(order_type, now.year, now.month, now.day, now.hour, now.minute,
                                              now.second)
    return date_str + str(random.randint(1000, 9999)) + str(random.randint(1000, 9999)) + str(
        random.randint(1000, 9999))


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
