#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月
# author: liuyu
# date: 2020/5/7
import os, re, json, requests
from fir_ser.settings import SUPER_SIGN_ROOT, SERVER_DOMAIN, CAPTCHA_LENGTH, MEDIA_ROOT
from api.models import APPSuperSignUsedInfo, APPToDeveloper, \
    UDIDsyncDeveloper, UserInfo, AppReleaseInfo
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
        pkey = auth.get("username")
        if auth.get("issuer_id"):
            pkey = auth.get("issuer_id")
        cert_dir_name = make_app_uuid(user_obj, pkey)
    cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name)
    if not os.path.isdir(cert_dir_path):
        os.makedirs(cert_dir_path)
    file_format_path_name = os.path.join(cert_dir_path, cert_dir_name)
    return file_format_path_name


def get_profile_full_path(developer_obj, app_obj):
    pkey = developer_obj.email
    if developer_obj.issuer_id:
        pkey = developer_obj.issuer_id
    cert_dir_name = make_app_uuid(developer_obj.user_id, pkey)
    cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name, "profile")
    provision_name = os.path.join(cert_dir_path, app_obj.app_id)
    return provision_name + '.mobileprovision'


def delete_app_to_dev_and_file(developer_obj, app_id):
    APPToDeveloper_obj = APPToDeveloper.objects.filter(developerid=developer_obj, app_id_id=app_id)
    if APPToDeveloper_obj:
        binary_file = APPToDeveloper_obj.first().binary_file + ".ipa"
        delete_local_files(binary_file)
        storage = Storage(developer_obj.user_id)
        storage.delete_file(binary_file)
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


def check_storage_additionalparameter(request, res):
    data = request.data
    try:
        extra_parameters = data.get('additionalparameter', '')
        if extra_parameters:
            if not extra_parameters.get("download_auth_type", None):
                extra_parameters['download_auth_type'] = 1
            if extra_parameters.get("download_auth_type", None) == 2:
                if not extra_parameters.get("cnd_auth_key", None):
                    logger.error("user %s add new storage failed" % (request.user))
                    res.msg = "cdn 鉴权KEY 缺失"
                    res.code = 1006
                    return False, res
        data['additionalparameters'] = json.dumps(extra_parameters)
    except Exception as e:
        logger.error("user:%s additionalparameters %s dumps failed Exception:%s" % (
            request.user, data.get('additionalparameter', ''), e))
    return True, res


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

    with open(org_file + ".check.tmp", "wb") as f:
        f.write(req.content)
    try:
        if os.path.isfile(org_file):
            os.remove(org_file)
        os.rename(os.path.join(org_file + ".check.tmp"), org_file)
        return True
    except Exception as e:
        logger.error("check org file and mv file %s failed Exception %s" % (org_file, e))
        return False


def migrating_storage_file_data(user_obj, filename, new_storage_obj):
    local_file_full_path = os.path.join(MEDIA_ROOT, filename)
    old_storage_obj = Storage(user_obj)
    if not new_storage_obj:
        new_storage_obj = Storage(user_obj, None, True)
    else:
        new_storage_obj = Storage(user_obj, new_storage_obj)

    if old_storage_obj.get_storage_type() == 3:
        if new_storage_obj.get_storage_type() == 3:
            pass
        else:
            # 本地向云存储上传,并删除本地数据
            new_storage_obj.upload_file(local_file_full_path)
            delete_local_files(filename)
    else:
        if new_storage_obj.get_storage_type() == 3:
            # 云存储下载 本地，并删除云存储
            if download_files_form_oss(old_storage_obj, local_file_full_path):
                old_storage_obj.delete_file(filename)
        else:
            # 云存储互传，先下载本地，然后上传新云存储，删除本地和老云存储
            if download_files_form_oss(old_storage_obj, local_file_full_path):
                new_storage_obj.upload_file(local_file_full_path)
                delete_local_files(filename)
                old_storage_obj.delete_file(filename)


def migrating_storage_data(user_obj, new_storage_obj):
    for app_release_obj in AppReleaseInfo.objects.filter(app_id__user_id=user_obj).all():
        filename = get_filename_from_apptype(app_release_obj.release_id, app_release_obj.release_type)
        migrating_storage_file_data(user_obj, filename, new_storage_obj)
