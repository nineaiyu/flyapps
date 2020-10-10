#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月
# author: liuyu
# date: 2020/5/7
import os, re
from fir_ser.settings import SUPER_SIGN_ROOT, SERVER_DOMAIN, CAPTCHA_LENGTH, MEDIA_ROOT
from api.models import APPSuperSignUsedInfo, APPToDeveloper, \
    UDIDsyncDeveloper, UserInfo
from api.utils.app.randomstrings import make_app_uuid
from api.utils.storage.localApi import LocalStorage
from api.utils.storage.storage import Storage
from api.utils.tempcaches import tmpCache
from api.utils.TokenManager import DownloadToken, generateNumericTokenOfLength, generateAlphanumericTokenOfLength
from api.utils.sendmsg.sendmsg import SendMessage
from django.db.models import Sum
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


def file_format_path(user_obj, auth=None, email=None):
    if email:
        cert_dir_name = make_app_uuid(user_obj, email)
    else:
        cert_dir_name = make_app_uuid(user_obj, auth.get("username"))
    cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name)
    if not os.path.isdir(cert_dir_path):
        os.makedirs(cert_dir_path)
    file_format_path_name = os.path.join(cert_dir_path, cert_dir_name)
    return file_format_path_name


def get_profile_full_path(developer_obj, app_obj):
    cert_dir_name = make_app_uuid(developer_obj.user_id, developer_obj.email)
    cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name, "profile")
    provisionName = os.path.join(cert_dir_path, app_obj.app_id)
    return provisionName + '.mobileprovision'


def delete_app_to_dev_and_file(developer_obj, app_id):
    APPToDeveloper_obj = APPToDeveloper.objects.filter(developerid=developer_obj, app_id_id=app_id)
    if APPToDeveloper_obj:
        binary_file = APPToDeveloper_obj.first().binary_file + ".ipa"
        lsobj = LocalStorage("localhost", False)
        lsobj.del_file(binary_file)
        APPToDeveloper_obj.delete()


def delete_app_profile_file(developer_obj, app_obj):
    file = get_profile_full_path(developer_obj, app_obj)
    try:
        if os.path.isfile(file):
            os.remove(file)
    except Exception as e:
        logger.error("delete_app_profile_file developer_obj:%s  app_obj:%s file:%s Exception:%s" % (
            developer_obj, app_obj, file, e))


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


def is_valid_domain(value):
    pattern = re.compile(
        r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
        r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
        r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
    )
    return True if pattern.match(value) else False


def is_valid_phone(value):
    phone_pat = re.compile('^(13\d|14[5|7]|15\d|166|17[3|6|7]|18\d)\d{8}$')
    return True if value and re.search(phone_pat, value) else False


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


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


def send_ios_developer_active_status(developer, msg):
    user_info = developer.user_id
    act = 'email'
    email = user_info.email
    if email:
        get_sender_email_token(act, email, 'msg', msg)
    else:
        logger.info("user %s has no email. so %s can't send!" % (user_info, msg))
