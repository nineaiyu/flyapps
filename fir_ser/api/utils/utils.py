#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月
# author: liuyu
# date: 2020/5/7
import os
from fir_ser.settings import SUPER_SIGN_ROOT, SERVER_DOMAIN, CAPTCHA_LENGTH
from api.models import APPSuperSignUsedInfo, APPToDeveloper, \
    UDIDsyncDeveloper
from api.utils.app.randomstrings import make_app_uuid
from api.utils.storage.localApi import LocalStorage
from django.db.models import Sum
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
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
    try:
        os.remove(get_profile_full_path(developer_obj, app_obj))
    except Exception as e:
        print(e)


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
