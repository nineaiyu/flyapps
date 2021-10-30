#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6

import logging
import os
import time
import uuid
import zipfile

import xmltodict
from django.core.cache import cache
from django.db.models import Sum

from api.models import APPSuperSignUsedInfo, AppUDID, AppIOSDeveloperInfo, AppReleaseInfo, Apps, APPToDeveloper, \
    UDIDsyncDeveloper, DeveloperAppID, DeveloperDevicesID, IosDeveloperPublicPoolBill
from api.utils.app.iossignapi import ResignApp, AppDeveloperApiV2
from api.utils.baseutils import file_format_path, delete_app_profile_file, get_profile_full_path, format_apple_date, \
    get_format_time, make_app_uuid, make_from_user_uuid
from api.utils.response import BaseResponse
from api.utils.serializer import BillAppInfoSerializer, BillDeveloperInfoSerializer, BillUdidInfoSerializer
from api.utils.storage.caches import del_cache_response_by_short, send_msg_over_limit, check_app_permission, \
    consume_user_download_times_by_app_obj
from api.utils.storage.storage import Storage
from api.utils.utils import delete_app_to_dev_and_file, send_ios_developer_active_status, delete_local_files, \
    download_files_form_oss, get_developer_udided
from fir_ser.settings import SUPER_SIGN_ROOT, MEDIA_ROOT, MOBILE_CONFIG_SIGN_SSL, MSGTEMPLATE

logger = logging.getLogger(__name__)


def check_org_file(user_obj, org_file):
    if not os.path.isdir(os.path.dirname(org_file)):
        os.makedirs(os.path.dirname(org_file))

    if os.path.isfile(org_file):
        return

    storage_obj = Storage(user_obj)
    return download_files_form_oss(storage_obj, org_file)


def resign_by_app_id(app_obj, need_download_profile=True):
    user_obj = app_obj.user_id
    info_list = []
    if app_obj.issupersign and user_obj.supersign_active:
        for developer_app_id_obj in DeveloperAppID.objects.filter(app_id=app_obj).all():
            developer_obj = developer_app_id_obj.developerid
            developer_app_id = developer_app_id_obj.aid
            d_time = time.time()
            if need_download_profile:
                with cache.lock("%s_%s_%s" % ('download_profile', app_obj.app_id, developer_obj.issuer_id), timeout=60):
                    IosUtils.modify_capability(developer_obj, app_obj, developer_app_id)
                    download_flag, result = IosUtils.exec_download_profile(app_obj, developer_obj, None, 2)
            else:
                download_flag = True
            with cache.lock("%s_%s_%s" % ('run_sign', app_obj.app_id, developer_obj.issuer_id), timeout=60 * 10):
                status, result = IosUtils.run_sign(user_obj, app_obj, developer_obj, download_flag, None, d_time, {},
                                                   True)
                info_list.append({'developer_id': developer_obj.issuer_id, 'result': (status, result)})
    return info_list


def check_app_sign_limit(app_obj):
    used_num = APPSuperSignUsedInfo.objects.filter(app_id=app_obj).all().count()
    limit_num = app_obj.supersign_limit_number
    if limit_num <= 0:
        flag = True
    else:
        flag = used_num < limit_num
    return flag, used_num


def udid_bytes_to_dict(xml_stream):
    new_uuid_info = {}
    try:
        a = xml_stream.find('<plist')
        b = xml_stream.find('</plist>')
        xml_dict = xmltodict.parse(xml_stream[a:b + 8])  # 解析xml字符串
        for i in range(len(xml_dict['plist']['dict']['key'])):
            new_uuid_info[xml_dict['plist']['dict']['key'][i].lower()] = xml_dict['plist']['dict']['string'][i]
    except Exception as e:
        logger.error(f"udid_xml_stream:{xml_stream} Exception:{e}")
        return None
    return new_uuid_info


def make_sign_udid_mobile_config(udid_url, short, bundle_id, app_name):
    if MOBILE_CONFIG_SIGN_SSL.get("open"):
        ssl_key_path = MOBILE_CONFIG_SIGN_SSL.get("ssl_key_path", None)
        ssl_pem_path = MOBILE_CONFIG_SIGN_SSL.get("ssl_pem_path", None)

        if ssl_key_path and ssl_pem_path and os.path.isfile(ssl_key_path) and os.path.isfile(ssl_pem_path):
            mobile_config_tmp_dir = os.path.join(SUPER_SIGN_ROOT, 'tmp', 'mobile_config')
            if not os.path.exists(mobile_config_tmp_dir):
                os.makedirs(mobile_config_tmp_dir)

            sign_mobile_config_path = os.path.join(mobile_config_tmp_dir, 'sign_' + short)
            logger.info(f"make sing mobile config {sign_mobile_config_path}")
            if os.path.isfile(sign_mobile_config_path):
                return open(sign_mobile_config_path, 'rb')

            status, result = ResignApp.sign_mobile_config(
                make_udid_mobile_config(udid_url, bundle_id, app_name),
                ssl_pem_path,
                ssl_key_path)

            if status and result.get('data'):
                with open(sign_mobile_config_path, 'wb') as f:
                    f.write(result.get('data'))
                return open(sign_mobile_config_path, 'rb')
            else:
                logger.error(
                    f"{bundle_id} {app_name} sign_mobile_config failed ERROR:{result.get('err_info')}")
                return make_udid_mobile_config(udid_url, bundle_id, app_name)

        else:
            logger.error(f"sign_mobile_config {ssl_key_path} or {ssl_pem_path} is not exists")
            return make_udid_mobile_config(udid_url, bundle_id, app_name)

    else:
        return make_udid_mobile_config(udid_url, bundle_id, app_name)


def make_udid_mobile_config(udid_url, payload_organization, app_name, payload_uuid=uuid.uuid1(),
                            payload_description='该文件仅用来获取设备ID，帮助用户安装授权',
                            display_name='设备安装授权'):
    # <!--参考:https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/iPhoneOTAConfiguration/ConfigurationProfileExamples/ConfigurationProfileExamples.html-->
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>PayloadContent</key>
        <dict>
            <key>URL</key>
            <string>{udid_url}</string>
            <key>DeviceAttributes</key>
            <array>
                <string>SERIAL</string>
                <string>UDID</string>
                <string>IMEI</string>
                <string>ICCID</string>
                <string>VERSION</string>
                <string>PRODUCT</string>
            </array>
        </dict>
        <key>PayloadOrganization</key>
        <string>{payload_organization}</string>
        <key>PayloadDisplayName</key>
        <string>{app_name}--{display_name}</string>
        <key>PayloadVersion</key>
        <integer>1</integer>
        <key>PayloadUUID</key>
        <string>{payload_uuid}</string>
        <key>PayloadIdentifier</key>
        <string>{payload_organization}.profile-service</string>
        <key>PayloadDescription</key>
        <string>{payload_description}</string>
        <key>PayloadType</key>
        <string>Profile Service</string>
    </dict>
</plist>'''


def get_auth_form_developer(developer_obj):
    if developer_obj.issuer_id:
        auth = {
            "issuer_id": developer_obj.issuer_id,
            "private_key_id": developer_obj.private_key_id,
            "p8key": developer_obj.p8key,
            "cert_id": developer_obj.certid
        }
    else:
        auth = {}
    return auth


def get_api_obj(auth):
    if auth.get("issuer_id"):
        app_api_obj = AppDeveloperApiV2(**auth)
    else:
        app_api_obj = None
    return app_api_obj


def get_apple_udid_key(auth):
    m_key = ''
    if auth.get("issuer_id"):
        m_key = auth.get("issuer_id")
    return m_key


def err_callback(func, *args, **kwargs):
    def wrapper():
        return func(*args, **kwargs)

    return wrapper


def get_ios_developer_public_num(user_obj):
    add_number = IosDeveloperPublicPoolBill.objects.filter(to_user_id=user_obj, action__in=[1, 2]).aggregate(
        number=Sum('number'))
    used_number = IosDeveloperPublicPoolBill.objects.filter(user_id=user_obj, action=0,
                                                            udid_sync_info__isnull=False).aggregate(
        number=Sum('number'))
    if add_number:
        add_number = add_number.get("number", 0)
        if not add_number:
            return False
        used_number = used_number.get("number", 0)
        if not used_number:
            used_number = 0
        if add_number - used_number > 0:
            return True
    return False


def get_developer_user_by_app_udid(user_obj, udid):
    use_device_obj = APPSuperSignUsedInfo.objects.filter(udid__udid__udid=udid,
                                                         user_id=user_obj, developerid__is_actived=True,
                                                         developerid__certid__isnull=False).first()
    # 只要账户下面存在udid,就可以使用该苹果开发者账户，避免多个开发者账户下面出现同一个udid
    if use_device_obj:
        developer_obj = use_device_obj.developerid
    else:
        developer_udid_obj = UDIDsyncDeveloper.objects.filter(udid=udid,
                                                              developerid__is_actived=True,
                                                              developerid__certid__isnull=False).first()
        if developer_udid_obj and developer_udid_obj.developerid.user_id.pk == user_obj.pk:
            developer_obj = developer_udid_obj.developerid
        else:
            for developer_obj in AppIOSDeveloperInfo.objects.filter(user_id=user_obj, is_actived=True,
                                                                    certid__isnull=False).order_by("created_time"):
                if get_developer_udided(developer_obj)[1] < developer_obj.usable_number:
                    return developer_obj
            return None
    return developer_obj


def get_developer_obj_by_others(user_obj, udid):
    result = get_developer_user_by_app_udid(user_obj, udid)
    if result:
        return result
    if not get_ios_developer_public_num(user_obj):
        return None
    receive_user_obj_list = IosDeveloperPublicPoolBill.objects.filter(to_user_id=user_obj).all()
    for receive_user_obj in receive_user_obj_list:
        result = get_developer_user_by_app_udid(receive_user_obj.user_id, udid)
        if result is None:
            continue
        else:
            logger.warning(f"user receive_user_obj {receive_user_obj.user_id} developer to sign")
            return result
    return None


class IosUtils(object):
    def __init__(self, udid_info, user_obj, app_obj=None):
        self.developer_obj = None
        self.auth = None
        self.udid_info = udid_info
        self.udid = udid_info.get('udid')
        self.app_obj = app_obj
        self.user_obj = user_obj
        self.get_developer_auth()

    def get_developer_auth(self):
        self.developer_obj = get_developer_obj_by_others(self.user_obj, self.udid)
        if self.developer_obj:
            self.auth = get_auth_form_developer(self.developer_obj)
        else:
            logger.error(f"user {self.user_obj} has no active apple developer")
            if self.user_obj.email:
                if send_msg_over_limit("get", self.user_obj.email):
                    send_msg_over_limit("set", self.user_obj.email)
                    send_ios_developer_active_status(self.user_obj, MSGTEMPLATE.get('NOT_EXIST_DEVELOPER', '')
                                                     % (
                                                         self.user_obj.first_name, self.app_obj.name))
                else:
                    logger.error(f"user {self.user_obj} send msg failed. over limit")

    # def download_profile(self, developer_app_id, device_id_list):
    #     return get_api_obj(self.auth).get_profile(self.app_obj, self.udid_info,
    #                                               self.get_profile_full_path(),
    #                                               self.auth, developer_app_id, device_id_list, )

    # 开启超级签直接在开发者账户创建
    # def create_app(self, app_obj):
    #     bundleId = self.app_obj.bundle_id
    #     app_id = self.app_obj.app_id
    #     s_type = self.app_obj.supersign_type
    #     return get_api_obj(self.auth).create_app(bundleId, app_id, s_type)

    @staticmethod
    def modify_capability(developer_obj, app_obj, developer_app_id):
        auth = get_auth_form_developer(developer_obj)
        return get_api_obj(auth).modify_capability(app_obj, developer_app_id)

    def get_profile_full_path(self):
        cert_dir_name = make_app_uuid(self.user_obj, get_apple_udid_key(self.auth))
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name, "profile")
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        provision_name = os.path.join(cert_dir_path, self.app_obj.app_id)
        return provision_name + '.mobileprovision'

    @staticmethod
    def exec_download_profile(app_obj, developer_obj, udid_info, sign_try_attempts=3):
        result = {}
        developer_app_id = None
        auth = get_auth_form_developer(developer_obj)
        while sign_try_attempts > 0:
            logger.info(
                f"exec_download_profile app_id:{app_obj} developer:{developer_obj} sign_try_attempts:{sign_try_attempts}")
            device_id_list = DeveloperDevicesID.objects.filter(app_id=app_obj,
                                                               developerid=developer_obj).values_list('did')
            device_id_lists = [did[0] for did in device_id_list]
            developer_app_id = None
            add_did_flag = False
            sync_device_obj = None
            developer_app_id_obj = DeveloperAppID.objects.filter(developerid=developer_obj,
                                                                 app_id=app_obj).first()
            if developer_app_id_obj:
                developer_app_id = developer_app_id_obj.aid
            if udid_info:
                sync_device_obj = UDIDsyncDeveloper.objects.filter(udid=udid_info.get('udid'),
                                                                   developerid=developer_obj, status=True).first()
                if sync_device_obj:
                    DeveloperDevicesID.objects.update_or_create(did=sync_device_obj.serial, udid=sync_device_obj,
                                                                developerid=developer_obj,
                                                                app_id=app_obj)

                    device_id_lists.append(sync_device_obj.serial)
                    udid_info = None
                    add_did_flag = True
                    logger.info(f"app {app_obj} device {sync_device_obj.serial} already in developer {developer_obj}")

            status, result = get_api_obj(auth).get_profile(app_obj, udid_info,
                                                           get_profile_full_path(developer_obj, app_obj),
                                                           auth, developer_app_id, device_id_lists,
                                                           err_callback(IosUtils.get_device_from_developer,
                                                                        developer_obj))
            if add_did_flag and sync_device_obj:
                result['did'] = sync_device_obj.serial
                result['did_exists'] = True
            if not status:
                sign_try_attempts -= 1
                logger.warning(f"app {app_obj}  developer {developer_obj} sign failed {result} .try again ")
                time.sleep(3)
            else:
                sign_try_attempts = -1
        if sign_try_attempts != -1:
            logger.error(f"app {app_obj} developer {developer_obj} sign failed {result}")
            developer_obj.is_actived = False
            developer_obj.save(update_fields=['is_actived'])
            send_ios_developer_active_status(developer_obj.user_id,
                                             MSGTEMPLATE.get('ERROR_DEVELOPER') % (
                                                 developer_obj.user_id.first_name, app_obj.name,
                                                 developer_obj.issuer_id))
            return False, result

        if not developer_app_id and result.get("aid", None):
            DeveloperAppID.objects.create(aid=result["aid"], developerid=developer_obj, app_id=app_obj)

        return True, result

    @staticmethod
    def zip_cert(user_obj, developer_obj):
        auth = get_auth_form_developer(developer_obj)
        file_format_path_name = file_format_path(user_obj, auth)
        os.chdir(os.path.dirname(file_format_path_name))
        zip_file_path = file_format_path_name + '.zip'
        zipf = zipfile.ZipFile(zip_file_path, mode='w', compression=zipfile.ZIP_DEFLATED)
        for file in os.listdir(os.path.dirname(file_format_path_name)):
            if os.path.isfile(file) and file.startswith(os.path.basename(file_format_path_name)) and \
                    file.split('.')[-1] not in ['zip', 'bak']:
                zipf.write(file)
        zipf.close()
        return zip_file_path

    @staticmethod
    def get_resign_obj(user_obj, developer_obj):
        auth = get_auth_form_developer(developer_obj)
        file_format_path_name = file_format_path(user_obj, auth)
        my_local_key = file_format_path_name + ".key"
        app_dev_pem = file_format_path_name + ".pem"
        app_dev_p12 = file_format_path_name + ".p12"
        return ResignApp(my_local_key, app_dev_pem, app_dev_p12)

    @staticmethod
    def exec_sign(user_obj, app_obj, developer_obj, random_file_name, release_obj):
        resign_app_obj = IosUtils.get_resign_obj(user_obj, developer_obj)
        org_file = os.path.join(MEDIA_ROOT, release_obj.release_id + ".ipa")
        check_org_file(user_obj, org_file)
        new_file = os.path.join(MEDIA_ROOT, random_file_name + ".ipa")
        properties_info = {}
        if app_obj.new_bundle_id:
            properties_info = {'-b': app_obj.new_bundle_id}
        if app_obj.new_bundle_name:
            properties_info = {'-n': app_obj.new_bundle_name}
        status, result = resign_app_obj.sign(get_profile_full_path(developer_obj, app_obj), org_file, new_file,
                                             properties_info)
        if status:
            logger.info(f"{user_obj} {developer_obj} {app_obj} sign_ipa success")
            return True, result
        else:
            logger.error(f"{user_obj} {developer_obj} {app_obj} sign_ipa failed ERROR:{result.get('err_info')}")
            return False, result

    @staticmethod
    def update_sign_file_name(user_obj, app_obj, developer_obj, release_obj, random_file_name):
        apptodev_obj = APPToDeveloper.objects.filter(developerid=developer_obj, app_id=app_obj).first()
        storage_obj = Storage(user_obj)
        if apptodev_obj:
            delete_local_files(apptodev_obj.binary_file + ".ipa")
            storage_obj.delete_file(apptodev_obj.binary_file + ".ipa")
            apptodev_obj.binary_file = random_file_name
            old_release_file = apptodev_obj.release_file
            apptodev_obj.release_file = release_obj.release_id
            apptodev_obj.save(update_fields=['binary_file', 'release_file'])
            if storage_obj.get_storage_type() in [1, 2] and old_release_file != release_obj.release_id:
                logger.warning(f"update sign file , now clean ole {old_release_file}.ipa file")
                delete_local_files(old_release_file + ".ipa")
        else:
            APPToDeveloper.objects.create(developerid=developer_obj, app_id=app_obj,
                                          binary_file=random_file_name, release_file=release_obj.release_id)

        logger.info(f"update sign file end, now upload {storage_obj.storage} {random_file_name}.ipa file")
        return storage_obj.upload_file(os.path.join(MEDIA_ROOT, random_file_name + ".ipa"))

    def update_developer_used_data(self, client_ip):
        udid_obj = AppUDID.objects.filter(app_id=self.app_obj, udid__udid=self.udid,
                                          udid__developerid=self.developer_obj).first()
        udid_obj.is_download = True
        udid_obj.save(update_fields=['is_download'])
        APPSuperSignUsedInfo.objects.update_or_create(app_id=self.app_obj,
                                                      user_id=self.user_obj,
                                                      developerid=self.developer_obj,
                                                      udid=udid_obj)
        udid_sync_info = UDIDsyncDeveloper.objects.filter(developerid=self.developer_obj,
                                                          udid=self.udid).first()
        IosDeveloperPublicPoolBill.objects.update_or_create(user_id=self.user_obj,
                                                            app_info=BillAppInfoSerializer(self.app_obj).data,
                                                            developer_info=BillDeveloperInfoSerializer(
                                                                self.developer_obj).data,
                                                            udid_info=BillUdidInfoSerializer(udid_obj).data, action=0,
                                                            number=1, udid_sync_info=udid_sync_info
                                                            )

    @staticmethod
    def update_sign_data(user_obj, app_obj, developer_obj, random_file_name, release_obj, udid):
        # 更新新签名的ipa包
        if IosUtils.update_sign_file_name(user_obj, app_obj, developer_obj, release_obj,
                                          random_file_name):
            newdata = {
                "is_signed": True,
                "binary_file": random_file_name
            }
            # 更新已经完成签名状态，设备消耗记录，和开发者已消耗数量
            udid_obj = UDIDsyncDeveloper.objects.filter(developerid=developer_obj, udid=udid).first()
            AppUDID.objects.filter(app_id=app_obj, udid=udid_obj).update(**newdata)
            del_cache_response_by_short(app_obj.app_id, udid=udid)
            return True

    @staticmethod
    def run_sign(user_obj, app_obj, developer_obj, download_flag, udid, d_time, result, resign=False):
        d_result = {'code': 0, 'msg': 'success'}
        start_time = time.time()
        if download_flag:
            logger.info(f"app_id {app_obj} download profile success. time:{start_time - d_time}")
            random_file_name = make_from_user_uuid(developer_obj.user_id)
            release_obj = AppReleaseInfo.objects.filter(app_id=app_obj, is_master=True).first()
            status, e_result = IosUtils.exec_sign(developer_obj.user_id, app_obj, developer_obj, random_file_name,
                                                  release_obj)
            if status:
                s_time1 = time.time()
                logger.info(f"app_id {app_obj} exec sign ipa success. time:{s_time1 - start_time}")
                if resign:
                    if not IosUtils.update_sign_file_name(user_obj, app_obj, developer_obj, release_obj,
                                                          random_file_name):
                        d_result['code'] = 1004
                        d_result['msg'] = '数据更新失败，请稍后重试'
                        return status, d_result
                else:
                    if not IosUtils.update_sign_data(user_obj, app_obj, developer_obj, random_file_name, release_obj,
                                                     udid):
                        d_result['code'] = 1004
                        d_result['msg'] = '数据更新失败，请稍后重试'
                        return status, d_result
            else:
                d_result['code'] = 1004
                d_result['msg'] = '签名失败，请检查包是否正常'
                return status, d_result
        else:
            msg = f"app_id {app_obj} download profile failed. {result} time:{time.time() - start_time}"
            d_result['code'] = 1002
            d_result['msg'] = msg
            logger.error(d_result)
            return False, d_result
        msg = f"app_id {app_obj} developer {developer_obj} sign end... time:{time.time() - start_time}"
        logger.info(msg)
        d_result['msg'] = msg
        return True, d_result

    def sign(self, client_ip, sign_try_attempts=3):
        """
        :param client_ip:
        :param sign_try_attempts:
        :return:  status, result
        :des:  仅用于苹果设备发送设备udid签名使用
        """
        d_result = {'code': 0, 'msg': 'success'}
        state, used_num = check_app_sign_limit(self.app_obj)
        if not state:
            d_result['code'] = 1003
            d_result['msg'] = "app_id %s used over limit.now %s limit: %s" % (
                self.app_obj, used_num, self.app_obj.supersign_limit_number)
            logger.error(d_result)
            return False, d_result

        res = check_app_permission(self.app_obj, BaseResponse())
        if res.code != 1000:
            return False, {'code': res.code, 'msg': res.msg}

        if not self.developer_obj:
            msg = "udid %s app %s not exists apple developer" % (self.udid, self.app_obj)
            d_result['code'] = 1005
            d_result['msg'] = msg
            logger.error(d_result)
            return False, d_result

        app_udid_obj = AppUDID.objects.filter(app_id=self.app_obj, udid__udid=self.udid,
                                              udid__developerid=self.developer_obj).first()
        if app_udid_obj and app_udid_obj.is_download:
            if app_udid_obj.is_signed:
                release_obj = AppReleaseInfo.objects.filter(app_id=self.app_obj, is_master=True).first()
                for apptodev_obj in APPToDeveloper.objects.filter(app_id=self.app_obj).all():
                    if release_obj.release_id == apptodev_obj.release_file:
                        msg = "udid %s exists app_id %s" % (self.udid, self.app_obj)
                        d_result['msg'] = msg
                        logger.info(d_result)
                        return True, d_result
            else:
                with cache.lock("%s_%s_%s" % ('run_sign', self.app_obj.app_id, self.developer_obj.issuer_id),
                                timeout=60 * 10):
                    logger.info("start run_sign ...")
                    return IosUtils.run_sign(self.user_obj, self.app_obj, self.developer_obj, 1,
                                             self.udid, time.time(),
                                             None)

        logger.info("udid %s not exists app_id %s ,need sign" % (self.udid, self.app_obj))

        if consume_user_download_times_by_app_obj(self.app_obj):
            d_result['code'] = 1009
            d_result['msg'] = '可用下载额度不足，请联系开发者'
            logger.error(d_result)
            return False, d_result

        call_flag = True
        download_flag = False
        count = 1
        result = {}
        start_time = time.time()
        while call_flag:
            logger.info(
                "call_loop download_profile appid:%s developer:%s count:%s" % (self.app_obj, self.developer_obj, count))
            if self.developer_obj:
                with cache.lock("%s_%s_%s" % ('download_profile', self.app_obj.app_id, self.developer_obj.issuer_id),
                                timeout=180):
                    download_flag, result = IosUtils.exec_download_profile(self.app_obj, self.developer_obj,
                                                                           self.udid_info, sign_try_attempts)
                if download_flag:
                    call_flag = False
                else:
                    self.get_developer_auth()
            else:
                call_flag = False
            count += 1
        if download_flag:
            app_udid_obj = UDIDsyncDeveloper.objects.filter(developerid=self.developer_obj,
                                                            udid=self.udid)
            udid_info = self.udid_info
            del udid_info['udid']
            AppUDID.objects.update_or_create(app_id=self.app_obj, udid=app_udid_obj.first(),
                                             defaults=udid_info)
            if not result.get("did_exists", None):
                app_udid_obj = app_udid_obj.filter(status=True).first()
                if not app_udid_obj:
                    appudid_obj = AppUDID.objects.filter(app_id=self.app_obj, udid__udid=self.udid,
                                                         udid__developerid=self.developer_obj)
                    device = appudid_obj.values("serial",
                                                'product',
                                                'udid__udid',
                                                'version').first()
                    if result.get("did", None):
                        device['serial'] = result["did"]
                        device['status'] = True
                        app_udid_obj, _ = UDIDsyncDeveloper.objects.update_or_create(developerid=self.developer_obj,
                                                                                     udid=device['udid__udid'],
                                                                                     defaults=device)
                        DeveloperDevicesID.objects.create(did=result["did"], udid=app_udid_obj,
                                                          developerid=self.developer_obj,
                                                          app_id=self.app_obj)
                else:
                    if result.get("did", None):
                        DeveloperDevicesID.objects.create(did=result["did"], udid=app_udid_obj,
                                                          developerid=self.developer_obj,
                                                          app_id=self.app_obj)

            self.update_developer_used_data(client_ip)

        if not self.developer_obj:
            d_result['code'] = 1005
            d_result['msg'] = '未找到可用苹果开发者'
            logger.error(d_result)
            return False, d_result
        with cache.lock("%s_%s_%s" % ('run_sign', self.app_obj.app_id, self.developer_obj.issuer_id), timeout=60 * 10):
            logger.info("start run_sign ...")
            return IosUtils.run_sign(self.user_obj, self.app_obj, self.developer_obj, download_flag,
                                     self.udid, start_time,
                                     result)

    @staticmethod
    def disable_udid(udid_obj, app_id):

        usedeviceobj = APPSuperSignUsedInfo.objects.filter(udid=udid_obj, app_id_id=app_id)
        if usedeviceobj:
            developer_obj = usedeviceobj.first().developerid
            auth = get_auth_form_developer(developer_obj)

            # 需要判断该设备在同一个账户下 的多个应用，若存在，则不操作
            udid_lists = list(
                APPSuperSignUsedInfo.objects.values_list("udid__udid__udid").filter(developerid=developer_obj))
            IosUtils.do_disable_device(developer_obj, udid_lists, udid_obj, auth)
            DeveloperDevicesID.objects.filter(udid__appudid=udid_obj, developerid=developer_obj,
                                              app_id_id=app_id).delete()
            udid_obj.delete()
            # 通过开发者id判断 app_id 是否多个，否则删除profile 文件
            if APPSuperSignUsedInfo.objects.filter(developerid=developer_obj, app_id_id=app_id).count() == 0:
                app_api_obj = get_api_obj(auth)
                app_obj = Apps.objects.filter(pk=app_id).first()
                app_api_obj.del_profile(app_obj.app_id)
                app_api_obj2 = get_api_obj(auth)
                app_api_obj2.del_app(app_obj.bundle_id, app_obj.app_id)
                DeveloperAppID.objects.filter(developerid=developer_obj, app_id=app_obj).delete()
                delete_app_to_dev_and_file(developer_obj, app_id)
                delete_app_profile_file(developer_obj, app_obj)

    @staticmethod
    def do_disable_device(developer_obj, udid_lists, udid_obj, auth):
        if udid_lists.count((udid_obj.udid.udid,)) == 1:
            app_api_obj = get_api_obj(auth)
            app_api_obj.set_device_status("disable", udid_obj.udid.udid)
            UDIDsyncDeveloper.objects.filter(udid=udid_obj.udid.udid, developerid=developer_obj).update(status=False)

    @staticmethod
    def clean_udid_by_app_obj(app_obj, developer_obj):

        auth = get_auth_form_developer(developer_obj)

        # 需要判断该设备在同一个账户下 的多个应用，若存在，则不操作
        udid_lists = list(
            APPSuperSignUsedInfo.objects.values_list("udid__udid__udid").filter(developerid=developer_obj))

        for SuperSignUsed_obj in APPSuperSignUsedInfo.objects.filter(app_id=app_obj, developerid=developer_obj):
            udid_obj = SuperSignUsed_obj.udid
            IosUtils.do_disable_device(developer_obj, udid_lists, udid_obj, auth)
            SuperSignUsed_obj.delete()
            DeveloperDevicesID.objects.filter(udid__appudid=udid_obj, developerid=developer_obj,
                                              app_id=app_obj).delete()
            udid_obj.delete()

    @staticmethod
    def clean_app_by_user_obj(app_obj):
        """
        该APP为超级签，删除app的时候，需要清理一下开发者账户里面的profile 和 bundleid
        :param app_obj:
        :return:
        """

        developer_id_lists = list(set(DeveloperAppID.objects.values_list("developerid").filter(app_id=app_obj)))

        for developer_id in developer_id_lists:
            developer_obj = AppIOSDeveloperInfo.objects.filter(pk=developer_id[0]).first()
            if developer_obj and developer_obj.user_id == app_obj.user_id:
                IosUtils.clean_app_by_developer_obj(app_obj, developer_obj)
                delete_app_to_dev_and_file(developer_obj, app_obj.id)
                IosUtils.clean_udid_by_app_obj(app_obj, developer_obj)
                delete_app_profile_file(developer_obj, app_obj)

    @staticmethod
    def clean_app_by_developer_obj(app_obj, developer_obj, cert_id=None):
        auth = get_auth_form_developer(developer_obj)
        DeveloperAppID.objects.filter(developerid=developer_obj, app_id=app_obj).delete()
        app_api_obj = get_api_obj(auth)
        app_api_obj.del_profile(app_obj.app_id)
        if not cert_id:
            app_api_obj2 = get_api_obj(auth)
            app_api_obj2.del_app(app_obj.bundle_id, app_obj.app_id)

    @staticmethod
    def clean_developer(developer_obj, user_obj, cert_id=None):
        """
        根据消耗记录 删除该苹果账户下所有信息
        :param user_obj:
        :param cert_id:
        :param developer_obj:
        :return:
        """
        for APPToDeveloper_obj in APPToDeveloper.objects.filter(developerid=developer_obj):
            app_obj = APPToDeveloper_obj.app_id
            IosUtils.clean_app_by_developer_obj(app_obj, developer_obj, cert_id)
            delete_app_to_dev_and_file(developer_obj, app_obj.id)
            if not cert_id:
                IosUtils.clean_udid_by_app_obj(app_obj, developer_obj)
        full_path = file_format_path(user_obj, get_auth_form_developer(developer_obj))
        try:
            # move dirs replace delete
            new_full_path_dir = os.path.dirname(full_path)
            new_full_path_name = os.path.basename(full_path)
            new_full_path = os.path.join(os.path.dirname(new_full_path_dir),
                                         '%s_%s_%s' % ('remove', new_full_path_name, get_format_time()))
            os.rename(new_full_path_dir, new_full_path)
        except Exception as e:
            logger.error("clean_developer developer_obj:%s user_obj:%s delete file failed Exception:%s" % (
                developer_obj, user_obj, e))

    @staticmethod
    def active_developer(developer_obj):
        """
        激活开发者账户
        :param developer_obj:
        :return:
        """
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        status, result = app_api_obj.active()
        if status:
            cert_is_exists = True
            for cert_obj in result.get('data', []):
                if cert_obj.id == developer_obj.certid:
                    developer_obj.cert_expire_time = format_apple_date(cert_obj.expirationDate)
                    cert_is_exists = False
                    break
            if developer_obj.certid and len(developer_obj.certid) > 3 and cert_is_exists and len(
                    result.get('data', [])) > 0:
                # 数据库证书id和苹果开发id不一致，可认为被用户删掉，需要执行清理开发者操作
                IosUtils.clean_developer(developer_obj, developer_obj.user_id)
                developer_obj.certid = None
                developer_obj.cert_expire_time = None
            developer_obj.is_actived = True
        else:
            developer_obj.is_actived = False
        developer_obj.save(update_fields=['certid', 'cert_expire_time', 'is_actived'])
        return status, result

    @staticmethod
    def create_developer_space(developer_obj, user_obj):
        auth = get_auth_form_developer(developer_obj)
        file_format_path_name = file_format_path(user_obj, auth)
        if not os.path.isdir(os.path.dirname(file_format_path_name)):
            os.makedirs(os.path.dirname(file_format_path_name))

    @staticmethod
    def create_developer_cert(developer_obj, user_obj):
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        status, result = app_api_obj.create_cert(user_obj)
        if status:
            if auth.get("issuer_id"):
                cert_id = result.id
                AppIOSDeveloperInfo.objects.filter(user_id=user_obj, issuer_id=auth.get("issuer_id")).update(
                    is_actived=True,
                    certid=cert_id, cert_expire_time=format_apple_date(result.expirationDate))
                resign_app_obj = IosUtils.get_resign_obj(user_obj, developer_obj)
                resign_app_obj.make_p12_from_cert(cert_id)
        return status, result

    @staticmethod
    def revoke_developer_cert(developer_obj, user_obj):
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        status, result = app_api_obj.revoke_cert()
        if not status:
            logger.warning('%s revoke cert failed,but i need clean cert_id %s' % (developer_obj.issuer_id, result))
        AppIOSDeveloperInfo.objects.filter(user_id=user_obj, issuer_id=auth.get("issuer_id")).update(
            is_actived=True,
            certid=None, cert_expire_time=None)
        return status, result

    @staticmethod
    def check_developer_cert(developer_obj, user_obj):
        # 暂时无用
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        status, result = app_api_obj.get_cert_obj_by_cid()
        if not status:
            AppIOSDeveloperInfo.objects.filter(user_id=user_obj, issuer_id=auth.get("issuer_id")).update(
                certid=None, cert_expire_time=None)
        return status, result

    @staticmethod
    def auto_get_cert_id_by_p12(developer_obj, user_obj):
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        file_format_path_name = file_format_path(user_obj, auth)
        app_dev_pem = file_format_path_name + ".pem.bak"
        status, result = app_api_obj.auto_set_certid_by_p12(app_dev_pem)
        if status:
            AppIOSDeveloperInfo.objects.filter(user_id=user_obj, issuer_id=auth.get("issuer_id")).update(
                is_actived=True,
                certid=result.id, cert_expire_time=format_apple_date(result.expirationDate))
        return status, result

    @staticmethod
    def get_device_from_developer(developer_obj):
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        status, result = app_api_obj.get_device()
        if status and auth.get("issuer_id"):

            udid_developer_obj_list = UDIDsyncDeveloper.objects.filter(developerid=developer_obj).values_list('udid')
            udid_developer_list = [x[0] for x in udid_developer_obj_list if len(x) > 0]
            udid_result_list = [device.udid for device in result]

            will_del_udid_list = list(set(udid_developer_list) - set(udid_result_list))

            udid_enabled_result_list = [device.udid for device in result if device.status == 'ENABLED']
            will_del_disabled_udid_list = list(set(udid_developer_list) - set(udid_enabled_result_list))

            for device_obj in result:
                device = {
                    "serial": device_obj.id,
                    "product": device_obj.name,
                    "udid": device_obj.udid,
                    "version": device_obj.model,
                    "status": True if device_obj.status == 'ENABLED' else False
                }
                obj, create = UDIDsyncDeveloper.objects.update_or_create(developerid=developer_obj,
                                                                         udid=device_obj.udid, defaults=device)
                if not create:
                    DeveloperDevicesID.objects.filter(udid=obj, developerid=developer_obj).update(
                        **{'did': device_obj.id})
            AppUDID.objects.filter(udid__udid__in=will_del_disabled_udid_list,
                                   app_id__developerdevicesid__udid__in=UDIDsyncDeveloper.objects.filter(
                                       udid__in=will_del_disabled_udid_list)).delete()
            developer_device_list = DeveloperDevicesID.objects.filter(udid__udid__in=will_del_disabled_udid_list,
                                                                      developerid=developer_obj).all()
            for developer_device_obj in developer_device_list:
                app_obj = developer_device_obj.app_id
                if APPSuperSignUsedInfo.objects.filter(developerid=developer_obj, app_id=app_obj).count() == 0:
                    app_api_obj = get_api_obj(auth)
                    app_api_obj.del_profile(app_obj.app_id)
                    app_api_obj2 = get_api_obj(auth)
                    app_api_obj2.del_app(app_obj.bundle_id, app_obj.app_id)
                    DeveloperAppID.objects.filter(developerid=developer_obj, app_id=app_obj).delete()
                    delete_app_to_dev_and_file(developer_obj, app_obj.pk)
                    delete_app_profile_file(developer_obj, app_obj)
                developer_device_obj.delete()

            UDIDsyncDeveloper.objects.filter(udid__in=will_del_udid_list, developerid=developer_obj).delete()

        return status, result
