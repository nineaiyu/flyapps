#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6

import uuid, xmltodict, os, re, logging, time

from django.utils import timezone
import zipfile
from api.utils.response import BaseResponse
from fir_ser.settings import SUPER_SIGN_ROOT, MEDIA_ROOT, SERVER_DOMAIN, MOBILECONFIG_SIGN_SSL, MSGTEMPLATE
from api.utils.app.iossignapi import ResignApp, AppDeveloperApiV2
from api.models import APPSuperSignUsedInfo, AppUDID, AppIOSDeveloperInfo, AppReleaseInfo, Apps, APPToDeveloper, \
    UDIDsyncDeveloper, DeveloperAppID, DeveloperDevicesID
from api.utils.app.randomstrings import make_app_uuid, make_from_user_uuid
from api.utils.storage.caches import del_cache_response_by_short, send_msg_over_limit, check_app_permission, \
    consume_user_download_times_by_app_obj
from api.utils.utils import delete_app_to_dev_and_file, send_ios_developer_active_status, delete_local_files, \
    download_files_form_oss, get_developer_udided
from api.utils.baseutils import file_format_path, delete_app_profile_file, get_profile_full_path, get_user_domain_name, \
    get_user_default_domain_name, get_min_default_domain_cname_obj, format_apple_date, get_format_time
from api.utils.storage.storage import Storage
from django.core.cache import cache

logger = logging.getLogger(__file__)


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
        for dappid_obj in DeveloperAppID.objects.filter(app_id=app_obj).all():
            developer_obj = dappid_obj.developerid
            developer_app_id = dappid_obj.aid
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
        logger.error("udid_xml_stream:%s Exception:%s" % (xml_stream, e))
        return None
    return new_uuid_info


def make_sign_udid_mobileconfig(udid_url, PayloadOrganization, appname):
    if MOBILECONFIG_SIGN_SSL.get("open"):
        ssl_key_path = MOBILECONFIG_SIGN_SSL.get("ssl_key_path", None)
        ssl_pem_path = MOBILECONFIG_SIGN_SSL.get("ssl_pem_path", None)

        if ssl_key_path and ssl_pem_path and os.path.isfile(ssl_key_path) and os.path.isfile(ssl_pem_path):
            mobileconfig_tmp_dir = os.path.join(SUPER_SIGN_ROOT, 'tmp', 'mobileconfig')
            if not os.path.exists(mobileconfig_tmp_dir):
                os.makedirs(mobileconfig_tmp_dir)

            mobileconfig_filename = PayloadOrganization + str(uuid.uuid1())
            mobilconfig_path = os.path.join(mobileconfig_tmp_dir, mobileconfig_filename)

            sign_mobilconfig_path = os.path.join(mobileconfig_tmp_dir, 'sign_' + mobileconfig_filename)
            with open(mobilconfig_path, "w") as f:
                f.write(make_udid_mobileconfig(udid_url, PayloadOrganization, appname))

            status, result = ResignApp.sign_mobileconfig(mobilconfig_path, sign_mobilconfig_path, ssl_pem_path,
                                                         ssl_key_path)
            if status:
                mobileconfig_body = open(sign_mobilconfig_path, 'rb')
            else:
                logger.error(
                    "%s %s sign_mobileconfig failed ERROR:%s" % (PayloadOrganization, appname, result.get("err_info")))
                return make_udid_mobileconfig(udid_url, PayloadOrganization, appname)

            return mobileconfig_body

        else:
            logger.error("sign_mobileconfig %s or %s is not exists" % (ssl_key_path, ssl_pem_path))
            return make_udid_mobileconfig(udid_url, PayloadOrganization, appname)

    else:
        return make_udid_mobileconfig(udid_url, PayloadOrganization, appname)


def make_udid_mobileconfig(udid_url, PayloadOrganization, appname, PayloadUUID=uuid.uuid1(),
                           PayloadDescription='该文件仅用来获取设备ID，帮助用户安装授权',
                           PayloadDisplayName='设备安装授权'):
    # <!--参考:https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/iPhoneOTAConfiguration/ConfigurationProfileExamples/ConfigurationProfileExamples.html-->
    mobileconfig = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>PayloadContent</key>
        <dict>
            <key>URL</key>
            <string>%s</string>
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
        <string>%s</string>
        <key>PayloadDisplayName</key>
        <string>%s</string>
        <key>PayloadVersion</key>
        <integer>1</integer>
        <key>PayloadUUID</key>
        <string>%s</string>
        <key>PayloadIdentifier</key>
        <string>%s.profile-service</string>
        <key>PayloadDescription</key>
        <string>%s</string>
        <key>PayloadType</key>
        <string>Profile Service</string>
    </dict>
</plist>''' % (udid_url, PayloadOrganization, appname + " -- " + PayloadDisplayName, PayloadUUID, PayloadOrganization,
               PayloadDescription)
    return mobileconfig


def get_post_udid_url(request, short):
    server_domain = get_http_server_doamin(request)
    PATH_INFO_lists = [server_domain, "udid", short]
    udid_url = "/".join(PATH_INFO_lists)
    return udid_url


def get_auth_form_developer(developer_obj):
    if developer_obj.issuer_id:
        auth = {
            "issuer_id": developer_obj.issuer_id,
            "private_key_id": developer_obj.private_key_id,
            "p8key": developer_obj.p8key,
            "certid": developer_obj.certid
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
    mpkey = ''
    if auth.get("issuer_id"):
        mpkey = auth.get("issuer_id")
    return mpkey


def get_server_domain_from_request(request, server_domain):
    if not server_domain or not server_domain.startswith("http"):
        HTTP_HOST = request.META.get('HTTP_HOST')
        SERVER_PROTOCOL = request.META.get('SERVER_PROTOCOL')
        protocol = 'https'
        if SERVER_PROTOCOL == 'HTTP/1.1':
            protocol = 'http'
        server_domain = "%s://%s" % (protocol, HTTP_HOST)
    return server_domain


def get_http_server_doamin(request):
    server_domain = SERVER_DOMAIN.get('POST_UDID_DOMAIN', None)
    return get_server_domain_from_request(request, server_domain)


def get_redirect_server_domain(request, user_obj=None, app_domain_name=None):
    is_https = False
    if user_obj:
        if app_domain_name and len(app_domain_name) > 3:
            domain_name = app_domain_name
        else:
            domain_name = get_user_domain_name(user_obj)
            if not domain_name:
                is_https, domain_name = get_user_default_domain_name(user_obj.default_domain_name)
    elif app_domain_name and len(app_domain_name) > 3:
        domain_name = app_domain_name
    else:
        is_https, domain_name = get_user_default_domain_name(get_min_default_domain_cname_obj(True))
    protocol = 'http'
    if is_https:
        protocol = 'https'
    server_domain = "%s://%s" % (protocol, domain_name)
    return get_server_domain_from_request(request, server_domain)


class IosUtils(object):
    def __init__(self, udid_info, user_obj, app_obj=None):
        self.developer_obj = None
        self.auth = None
        self.udid_info = udid_info
        self.app_obj = app_obj
        self.user_obj = user_obj
        self.get_developer_auth()

    def get_developer_auth(self):
        self.developer_obj = self.get_developer_user_by_app_udid()
        if self.developer_obj:
            self.auth = get_auth_form_developer(self.developer_obj)
        else:
            logger.error("user %s has no actived apple developer" % self.user_obj)
            if self.user_obj.email:
                if send_msg_over_limit("get", self.user_obj.email):
                    send_msg_over_limit("set", self.user_obj.email)
                    send_ios_developer_active_status(self.user_obj, MSGTEMPLATE.get('NOT_EXIST_DEVELOPER', '')
                                                     % (
                                                         self.user_obj.first_name, self.app_obj.name))
                else:
                    logger.error("user %s send msg failed. over limit" % self.user_obj)

    def get_developer_user_by_app_udid(self):
        usedeviceobj = APPSuperSignUsedInfo.objects.filter(udid__udid=self.udid_info.get('udid'),
                                                           user_id=self.user_obj, developerid__is_actived=True,
                                                           developerid__certid__isnull=False).first()
        # 只要账户下面存在udid,就可以使用该苹果开发者账户，避免多个开发者账户下面出现同一个udid
        if usedeviceobj:
            developer_obj = usedeviceobj.developerid
        else:
            developer_udid_obj = UDIDsyncDeveloper.objects.filter(udid=self.udid_info.get('udid'),
                                                                  developerid__is_actived=True,
                                                                  developerid__certid__isnull=False).first()
            if developer_udid_obj:
                developer_obj = developer_udid_obj.developerid
            else:
                for developer_obj in AppIOSDeveloperInfo.objects.filter(user_id=self.user_obj, is_actived=True,
                                                                        certid__isnull=False).order_by("created_time"):
                    usable_number = developer_obj.usable_number
                    flyapp_used = get_developer_udided(developer_obj)[1]
                    if flyapp_used < usable_number:
                        return developer_obj
                return None
        return developer_obj

    def download_profile(self, developer_app_id, device_id_list):
        return get_api_obj(self.auth).get_profile(self.app_obj, self.udid_info,
                                                  self.get_profile_full_path(),
                                                  self.auth, developer_app_id, device_id_list)

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
        add_did_flag = False
        auth = get_auth_form_developer(developer_obj)
        while sign_try_attempts > 0:
            logger.info("exec_download_profile appid:%s developer:%s sign_try_attempts:%s" % (
                app_obj, developer_obj, sign_try_attempts))
            device_id_list = DeveloperDevicesID.objects.filter(app_id=app_obj,
                                                               developerid=developer_obj).values_list('did')
            device_id_lists = [did[0] for did in device_id_list]
            developer_app_id = None
            developer_appid_obj = DeveloperAppID.objects.filter(developerid=developer_obj,
                                                                app_id=app_obj).first()
            if developer_appid_obj:
                developer_app_id = developer_appid_obj.aid
            if udid_info:
                sync_device_obj = UDIDsyncDeveloper.objects.filter(udid=udid_info.get('udid'),
                                                                   developerid=developer_obj).first()
                if sync_device_obj:
                    device_id_lists.append(sync_device_obj.serial)
                    udid_info = None
                    add_did_flag = True
                    logger.info(
                        "app %s device %s already in developer %s" % (app_obj, sync_device_obj.serial, developer_obj))

            status, result = get_api_obj(auth).get_profile(app_obj, udid_info,
                                                           get_profile_full_path(developer_obj, app_obj),
                                                           auth, developer_app_id, device_id_lists)
            if add_did_flag:
                result['did'] = sync_device_obj.serial
                result['did_exists'] = True
            if not status:
                sign_try_attempts -= 1
                logger.warning("app %s  developer %s sign failed %s .try again " % (app_obj, developer_obj, result))
                time.sleep(3)
            else:
                sign_try_attempts = -1
        if sign_try_attempts != -1:
            logger.error("app %s  developer %s sign failed %s" % (app_obj, developer_obj, result))
            developer_obj.is_actived = False
            developer_obj.save()
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
            logger.info("%s %s %s sign_ipa success" % (user_obj, developer_obj, app_obj))
            return True, result
        else:
            logger.error(
                "%s %s %s sign_ipa failed ERROR:%s" % (user_obj, developer_obj, app_obj, result.get("err_info")))
            return False, result

    @staticmethod
    def update_sign_file_name(user_obj, app_obj, developer_obj, release_obj, random_file_name):
        apptodev_obj = APPToDeveloper.objects.filter(developerid=developer_obj, app_id=app_obj).first()
        storage_obj = Storage(user_obj)
        if apptodev_obj:
            delete_local_files(apptodev_obj.binary_file + ".ipa")
            storage_obj.delete_file(apptodev_obj.binary_file + ".ipa")
            apptodev_obj.binary_file = random_file_name
            apptodev_obj.release_file = release_obj.release_id
            apptodev_obj.save()
        else:
            APPToDeveloper.objects.create(developerid=developer_obj, app_id=app_obj,
                                          binary_file=random_file_name, release_file=release_obj.release_id)

        storage_obj.upload_file(os.path.join(MEDIA_ROOT, random_file_name + ".ipa"))

    def update_developer_used_data(self):
        appsupersign_obj = APPSuperSignUsedInfo.objects.filter(udid__udid=self.udid_info.get('udid'),
                                                               developerid=self.developer_obj)
        if appsupersign_obj.count() == 0:
            developer_obj = self.developer_obj
            developer_obj.use_number = developer_obj.use_number + 1
            logger.info("developer %s use_number+1 now %s udid %s app_id %s" % (
                developer_obj, developer_obj.use_number, self.udid_info.get('udid'), self.app_obj))
            developer_obj.save()

        if not appsupersign_obj.filter(app_id=self.app_obj, user_id=self.user_obj).first():
            APPSuperSignUsedInfo.objects.create(app_id=self.app_obj, user_id=self.user_obj,
                                                developerid=self.developer_obj,
                                                udid=AppUDID.objects.filter(app_id=self.app_obj,
                                                                            udid=self.udid_info.get('udid')).first())

    def update_sign_data(self, random_file_name, release_obj):
        newdata = {
            "is_signed": True,
            "binary_file": random_file_name
        }
        # 更新已经完成签名状态，设备消耗记录，和开发者已消耗数量
        AppUDID.objects.filter(app_id=self.app_obj, udid=self.udid_info.get('udid')).update(**newdata)

        # 更新新签名的ipa包
        IosUtils.update_sign_file_name(self.user_obj, self.app_obj, self.developer_obj, release_obj, random_file_name)

        del_cache_response_by_short(self.app_obj.app_id, udid=self.udid_info.get('udid'))

    @staticmethod
    def run_sign(user_obj, app_obj, developer_obj, download_flag, obj, d_time, result, resign=False):
        d_result = {'code': 0, 'msg': 'success'}
        start_time = time.time()
        if download_flag:
            logger.info("app_id %s download profile success. time:%s" % (app_obj, start_time - d_time))
            random_file_name = make_from_user_uuid(user_obj)
            release_obj = AppReleaseInfo.objects.filter(app_id=app_obj, is_master=True).first()
            status, e_result = IosUtils.exec_sign(user_obj, app_obj, developer_obj, random_file_name, release_obj)
            if status:
                s_time1 = time.time()
                logger.info("app_id %s exec sign ipa success. time:%s" % (app_obj, s_time1 - start_time))
                if resign:
                    IosUtils.update_sign_file_name(user_obj, app_obj, developer_obj, release_obj, random_file_name)
                else:
                    obj.update_sign_data(random_file_name, release_obj)
            else:
                return status, e_result
        else:
            msg = "app_id %s download profile failed. %s time:%s" % (app_obj, result, time.time() - start_time)
            d_result['code'] = 1002
            d_result['msg'] = msg
            logger.error(d_result)
            return False, d_result
        msg = "app_id %s developer %s sign end... time:%s" % (app_obj, developer_obj, time.time() - start_time)
        logger.info(msg)
        d_result['msg'] = msg
        return True, d_result

    def sign(self, sign_try_attempts=3):
        """
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
            msg = "udid %s app %s not exists apple developer" % (self.udid_info.get('udid'), self.app_obj)
            d_result['code'] = 1005
            d_result['msg'] = msg
            logger.error(d_result)
            return False, d_result
        app_udid_obj = AppUDID.objects.filter(app_id=self.app_obj, udid=self.udid_info.get('udid')).first()
        if app_udid_obj and app_udid_obj.is_signed:
            release_obj = AppReleaseInfo.objects.filter(app_id=self.app_obj, is_master=True).first()
            for apptodev_obj in APPToDeveloper.objects.filter(app_id=self.app_obj).all():
                if release_obj.release_id == apptodev_obj.release_file:
                    msg = "udid %s exists app_id %s" % (self.udid_info.get('udid'), self.app_obj)
                    d_result['msg'] = msg
                    logger.info(d_result)
                    return True, d_result
        logger.info("udid %s not exists app_id %s ,need sign" % (self.udid_info.get('udid'), self.app_obj))

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
                                timeout=60):
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
            AppUDID.objects.update_or_create(app_id=self.app_obj, udid=self.udid_info.get('udid'),
                                             defaults=self.udid_info)
            if not result.get("did_exists", None):
                app_udid_obj = UDIDsyncDeveloper.objects.filter(developerid=self.developer_obj,
                                                                udid=self.udid_info.get('udid')).first()
                if not app_udid_obj:
                    appudid_obj = AppUDID.objects.filter(app_id=self.app_obj, udid=self.udid_info.get('udid'))
                    device = appudid_obj.values("serial",
                                                'product',
                                                'udid',
                                                'version').first()
                    if result.get("did", None):
                        device['serial'] = result["did"]
                        app_udid_obj = UDIDsyncDeveloper.objects.create(developerid=self.developer_obj, **device)
                        DeveloperDevicesID.objects.create(did=result["did"], udid=app_udid_obj,
                                                          developerid=self.developer_obj,
                                                          app_id=self.app_obj)
                else:
                    if result.get("did", None):
                        DeveloperDevicesID.objects.create(did=result["did"], udid=app_udid_obj,
                                                          developerid=self.developer_obj,
                                                          app_id=self.app_obj)

            self.update_developer_used_data()

        with cache.lock("%s_%s_%s" % ('run_sign', self.app_obj.app_id, self.developer_obj.issuer_id), timeout=60 * 10):
            logger.info("start run_sign ...")
            return IosUtils.run_sign(self.user_obj, self.app_obj, self.developer_obj, download_flag, self, start_time,
                                     result)

    @staticmethod
    def disable_udid(udid_obj, app_id):

        usedeviceobj = APPSuperSignUsedInfo.objects.filter(udid=udid_obj, app_id_id=app_id)
        if usedeviceobj:
            developer_obj = usedeviceobj.first().developerid
            auth = get_auth_form_developer(developer_obj)

            # 需要判断该设备在同一个账户下 的多个应用，若存在，则不操作
            udid_lists = list(APPSuperSignUsedInfo.objects.values_list("udid__udid").filter(developerid=developer_obj))
            IosUtils.do_disable_device(developer_obj, udid_lists, udid_obj, auth)
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

            app_udid_obj = UDIDsyncDeveloper.objects.filter(developerid=developer_obj,
                                                            udid=udid_obj.udid).first()
            DeveloperDevicesID.objects.filter(udid=app_udid_obj, developerid=developer_obj, app_id_id=app_id).delete()

    @staticmethod
    def do_disable_device(developer_obj, udid_lists, udid_obj, auth):
        if udid_lists.count((udid_obj.udid,)) == 1:
            app_api_obj = get_api_obj(auth)
            app_api_obj.set_device_status("disable", udid_obj.udid)
            UDIDsyncDeveloper.objects.filter(udid=udid_obj.udid, developerid=developer_obj).delete()

            if developer_obj.use_number > 0:
                developer_obj.use_number = developer_obj.use_number - 1
                developer_obj.save()

        udid_obj.delete()

    @staticmethod
    def clean_udid_by_app_obj(app_obj, developer_obj):

        auth = get_auth_form_developer(developer_obj)

        # 需要判断该设备在同一个账户下 的多个应用，若存在，则不操作
        udid_lists = list(APPSuperSignUsedInfo.objects.values_list("udid__udid").filter(developerid=developer_obj))

        for SuperSignUsed_obj in APPSuperSignUsedInfo.objects.filter(app_id=app_obj, developerid=developer_obj):
            udid_obj = SuperSignUsed_obj.udid
            IosUtils.do_disable_device(developer_obj, udid_lists, udid_obj, auth)
            SuperSignUsed_obj.delete()

    @staticmethod
    def clean_app_by_user_obj(app_obj, user_obj):
        '''
        该APP为超级签，删除app的时候，需要清理一下开发者账户里面的profile 和 bundleid
        :param app_obj:
        :param user_obj:
        :return:
        '''
        SuperSign_obj_lists = list(
            set(APPSuperSignUsedInfo.objects.values_list("developerid").filter(user_id=user_obj, app_id=app_obj)))
        for SuperSign_obj in SuperSign_obj_lists:
            developer_obj = AppIOSDeveloperInfo.objects.filter(pk=SuperSign_obj[0]).first()
            if developer_obj:
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
        '''
        根据消耗记录 删除该苹果账户下所有信息
        :param user_obj:
        :param cert_id:
        :param developer_obj:
        :return:
        '''
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
            new_full_path = os.path.join(new_full_path_dir,
                                         '%s_%s_%s' % ('remove', new_full_path_name, get_format_time()))
            os.rename(full_path, new_full_path)
            # for root, dirs, files in os.walk(full_path, topdown=False):
            #     for name in files:
            #         os.remove(os.path.join(root, name))
            #     for name in dirs:
            #         os.rmdir(os.path.join(root, name))
            # os.rmdir(full_path)
        except Exception as e:
            logger.error("clean_developer developer_obj:%s user_obj:%s delete file failed Exception:%s" % (
                developer_obj, user_obj, e))

    @staticmethod
    def active_developer(developer_obj):
        '''
        激活开发者账户
        :param developer_obj:
        :param code:
        :return:
        '''
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        status, result = app_api_obj.active()
        if status:
            for cert_obj in result.get('data', []):
                if cert_obj.id == developer_obj.certid:
                    developer_obj.cert_expire_time = format_apple_date(cert_obj.expirationDate)
                    break
            developer_obj.is_actived = True
        else:
            developer_obj.is_actived = False
        developer_obj.save()
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
        status, result = app_api_obj.revoke_cert(developer_obj.certid)
        if not status:
            logger.warning('%s revoke cert failed,but i need clean cert_id %s' % (developer_obj.issuer_id, result))
            AppIOSDeveloperInfo.objects.filter(user_id=user_obj, issuer_id=auth.get("issuer_id")).update(
                is_actived=True,
                certid=None, cert_expire_time=None)
        return status, result

    @staticmethod
    def check_developer_cert(developer_obj,user_obj):
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        status, result = app_api_obj.get_cert_obj_by_cid(developer_obj.certid)
        if not status:
            AppIOSDeveloperInfo.objects.filter(user_id=user_obj, issuer_id=auth.get("issuer_id")).update(
                certid=None, cert_expire_time=None)
        return status, result


    @staticmethod
    def auto_get_certid_by_p12(developer_obj, user_obj):
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
    def get_device_from_developer(developer_obj, user_obj):
        auth = get_auth_form_developer(developer_obj)
        app_api_obj = get_api_obj(auth)
        status, result = app_api_obj.get_device()
        if status:
            if auth.get("issuer_id"):
                UDIDsyncDeveloper.objects.filter(developerid=developer_obj, platform=1).delete()
                for device_obj in result:
                    device = {
                        "serial": device_obj.id,
                        "product": device_obj.name,
                        "udid": device_obj.udid,
                        "version": device_obj.model,
                        "platform": 1
                    }
                    app_udid_obj = UDIDsyncDeveloper.objects.filter(developerid=developer_obj, udid=device.get("udid"))
                    if app_udid_obj:
                        pass
                    else:
                        UDIDsyncDeveloper.objects.create(developerid=developer_obj, **device)
            else:

                file_format_path_name = file_format_path(user_obj, auth)
                devices_info = ""
                try:
                    with open(file_format_path_name + ".devices.info", "r") as f:
                        devices_info = f.read().replace("\n\t", "").replace("[", "").replace("]", "")
                except Exception as e:
                    logger.error(
                        "get_device_from_developer developer_obj:%s user_obj:%s delete file failed Exception:%s" % (
                            developer_obj, user_obj, e))

                UDIDsyncDeveloper.objects.filter(developerid=developer_obj, platform=1).delete()
                for devicestr in devices_info.split(">"):
                    formatdevice = re.findall(r'.*Device id="(.*)",.*name="(.*)",.*udid="(.*?)",.*model=(.*),.*',
                                              devicestr)
                    if formatdevice:
                        device = {
                            "serial": formatdevice[0][0],
                            "product": formatdevice[0][1],
                            "udid": formatdevice[0][2],
                            "version": formatdevice[0][3],
                            "platform": 1
                        }
                        app_udid_obj = UDIDsyncDeveloper.objects.filter(developerid=developer_obj,
                                                                        udid=device.get("udid"))
                        if app_udid_obj:
                            pass
                        else:
                            UDIDsyncDeveloper.objects.create(developerid=developer_obj, **device)
        return status, result
