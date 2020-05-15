#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6

import uuid, xmltodict, os, re, logging
from fir_ser.settings import SUPER_SIGN_ROOT, MEDIA_ROOT, SERVER_DOMAIN
from api.utils.app.iossignapi import AppDeveloperApi, ResignApp
from api.models import APPSuperSignUsedInfo, AppUDID, AppIOSDeveloperInfo, AppReleaseInfo, Apps, APPToDeveloper, \
    UDIDsyncDeveloper
from api.utils.app.randomstrings import make_app_uuid, make_from_user_uuid
from api.utils.serializer import get_developer_udided
from api.utils.storage.localApi import LocalStorage
from api.utils.storage.caches import del_cache_response_by_short
from api.utils.utils import file_format_path, delete_app_to_dev_and_file, delete_app_profile_file

logger = logging.getLogger(__file__)


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


def make_udid_mobileconfig(udid_url, PayloadOrganization, PayloadUUID=uuid.uuid1(), PayloadDescription='本文件仅用来获取设备ID',
                           PayloadDisplayName='查询设备UDID'):
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
</plist>''' % (udid_url, PayloadOrganization, PayloadDisplayName, PayloadUUID, PayloadOrganization, PayloadDescription)
    return mobileconfig


def get_post_udid_url(request, short):
    server_domain = get_http_server_doamin(request)
    # PATH_INFO = request.META.get('PATH_INFO')
    # PATH_INFO_lists = PATH_INFO.strip('/').split('/')
    # PATH_INFO_lists[-1] = 'udid'
    # PATH_INFO_lists.pop(-2)
    # PATH_INFO_lists.append(short)
    # PATH_INFO_lists.insert(0, server_domain)
    PATH_INFO_lists = [server_domain, "udid", short]
    udid_url = "/".join(PATH_INFO_lists)
    return udid_url


def get_http_server_doamin(request):
    server_domain = SERVER_DOMAIN.get('POST_UDID_DOMAIN', None)
    if not server_domain or not server_domain.startswith("http"):
        HTTP_HOST = request.META.get('HTTP_HOST')
        SERVER_PROTOCOL = request.META.get('SERVER_PROTOCOL')
        protocol = 'https'
        if SERVER_PROTOCOL == 'HTTP/1.1':
            protocol = 'http'
        server_domain = "%s://%s" % (protocol, HTTP_HOST)
    return server_domain


def get_redirect_server_domain(request):
    server_domain = SERVER_DOMAIN.get('REDIRECT_UDID_DOMAIN', None)
    if not server_domain or not server_domain.startswith("http"):
        HTTP_HOST = request.META.get('HTTP_HOST')
        SERVER_PROTOCOL = request.META.get('SERVER_PROTOCOL')
        protocol = 'https'
        if SERVER_PROTOCOL == 'HTTP/1.1':
            protocol = 'http'
        server_domain = "%s://%s" % (protocol, HTTP_HOST)
    return server_domain


class IosUtils(object):
    def __init__(self, udid_info, user_obj, app_obj=None):
        self.udid_info = udid_info
        self.app_obj = app_obj
        self.user_obj = user_obj
        self.get_developer_auth()

    def get_developer_auth(self):
        developer_obj = self.get_developer_user_by_app_udid()
        auth = {
            "username": developer_obj.email,
            "password": developer_obj.password,
            "certid": developer_obj.certid
        }
        self.developer_obj = developer_obj
        self.auth = auth

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
                for developer_obj in AppIOSDeveloperInfo.objects.filter(user_id=self.user_obj,
                                                                        is_actived=True, certid__isnull=False).order_by(
                    "created_time"):
                    usable_number = developer_obj.usable_number
                    flyapp_used = get_developer_udided(developer_obj)[1]
                    if flyapp_used < usable_number:
                        return developer_obj
                return None
        return developer_obj

    def download_profile(self):
        app_api_obj = AppDeveloperApi(**self.auth)
        bundleId = self.app_obj.bundle_id
        app_id = self.app_obj.app_id
        device_udid = self.udid_info.get('udid')
        device_name = self.udid_info.get('product')
        app_api_obj.get_profile(bundleId, app_id, device_udid, device_name, self.get_profile_full_path())

    def get_profile_full_path(self):
        cert_dir_name = make_app_uuid(self.user_obj, self.auth.get("username"))
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT, cert_dir_name, "profile")
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        provisionName = os.path.join(cert_dir_path, self.app_obj.app_id)
        return provisionName + '.mobileprovision'

    def resign(self):
        if AppUDID.objects.filter(app_id=self.app_obj, udid=self.udid_info.get('udid')).first().is_signed:
            apptodev_obj = APPToDeveloper.objects.filter(app_id=self.app_obj).first()
            if apptodev_obj:
                release_obj = AppReleaseInfo.objects.filter(app_id=self.app_obj, is_master=True).first()
                if release_obj.release_id == apptodev_obj.release_file:
                    logger.info("udid %s exists app_id %s" % (self.udid_info.get('udid'), self.app_obj))
                    return
        logger.info("udid %s not exists app_id %s ,need sign" % (self.udid_info.get('udid'), self.app_obj))
        self.download_profile()

        file_format_path_name = file_format_path(self.user_obj, self.auth)
        my_local_key = file_format_path_name + ".key"
        app_dev_pem = file_format_path_name + ".pem"
        ResignAppObj = ResignApp(my_local_key, app_dev_pem)

        random_file_name = make_from_user_uuid(self.user_obj)

        release_obj = AppReleaseInfo.objects.filter(app_id=self.app_obj, is_master=True).first()

        org_file = os.path.join(MEDIA_ROOT, release_obj.release_id + ".ipa")
        new_file = os.path.join(MEDIA_ROOT, random_file_name + ".ipa")
        ResignAppObj.sign(self.get_profile_full_path(), org_file, new_file)

        newdata = {
            "is_signed": True,
            "binary_file": random_file_name
        }
        # 更新已经完成签名状态，设备消耗记录，和开发者已消耗数量
        AppUDID.objects.filter(app_id=self.app_obj, udid=self.udid_info.get('udid')).update(**newdata)

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

        del_cache_response_by_short(self.app_obj.app_id, udid=self.udid_info.get('udid'))

        app_udid_obj = UDIDsyncDeveloper.objects.filter(developerid=self.developer_obj, udid=self.udid_info.get('udid'))
        if not app_udid_obj:
            device = AppUDID.objects.filter(app_id=self.app_obj, udid=self.udid_info.get('udid')).values("serial",
                                                                                                         'product',
                                                                                                         'udid',
                                                                                                         'version').first()
            UDIDsyncDeveloper.objects.create(developerid=self.developer_obj, **device)

        # 创建
        apptodev_obj = APPToDeveloper.objects.filter(developerid=self.developer_obj, app_id=self.app_obj).first()
        if apptodev_obj:
            storage = LocalStorage("localhost", False)
            storage.del_file(apptodev_obj.binary_file + ".ipa")
            apptodev_obj.binary_file = random_file_name
            apptodev_obj.release_file = release_obj.release_id
            apptodev_obj.save()

        else:
            APPToDeveloper.objects.create(developerid=self.developer_obj, app_id=self.app_obj,
                                          binary_file=random_file_name, release_file=release_obj.release_id)

    @staticmethod
    def disable_udid(udid_obj, app_id):

        usedeviceobj = APPSuperSignUsedInfo.objects.filter(udid=udid_obj, app_id_id=app_id)
        if usedeviceobj:
            developer_obj = usedeviceobj.first().developerid
            auth = {
                "username": developer_obj.email,
                "password": developer_obj.password,
                "certid": developer_obj.certid
            }

            # 需要判断该设备在同一个账户下 的多个应用，若存在，则不操作
            udid_lists = list(APPSuperSignUsedInfo.objects.values_list("udid__udid").filter(developerid=developer_obj))
            if udid_lists.count((udid_obj.udid,)) == 1:
                app_api_obj = AppDeveloperApi(**auth)
                app_api_obj.set_device_status("disable", udid_obj.udid)

                if developer_obj.use_number > 0:
                    developer_obj.use_number = developer_obj.use_number - 1
                    developer_obj.save()

            usedeviceobj.delete()

            # 通过开发者id判断 app_id 是否多个，否则删除profile 文件
            if APPSuperSignUsedInfo.objects.filter(developerid=developer_obj, app_id_id=app_id).count() == 0:
                app_api_obj = AppDeveloperApi(**auth)
                app_obj = Apps.objects.filter(pk=app_id).first()
                app_api_obj.del_profile(app_obj.bundle_id, app_obj.app_id)
                app_api_obj2 = AppDeveloperApi(**auth)
                app_api_obj2.del_app(app_obj.bundle_id, app_obj.app_id)
                delete_app_to_dev_and_file(developer_obj, app_id)
                delete_app_profile_file(developer_obj, app_obj)

    @staticmethod
    def clean_udid_by_app_obj(app_obj, developer_obj):

        auth = {
            "username": developer_obj.email,
            "password": developer_obj.password,
            "certid": developer_obj.certid
        }

        # 需要判断该设备在同一个账户下 的多个应用，若存在，则不操作
        udid_lists = list(APPSuperSignUsedInfo.objects.values_list("udid__udid").filter(developerid=developer_obj))

        for SuperSignUsed_obj in APPSuperSignUsedInfo.objects.filter(app_id=app_obj, developerid=developer_obj):
            udid_obj = SuperSignUsed_obj.udid

            if udid_lists.count((udid_obj.udid,)) == 1:
                app_api_obj = AppDeveloperApi(**auth)
                app_api_obj.set_device_status("disable", udid_obj.udid)

                if developer_obj.use_number > 0:
                    developer_obj.use_number = developer_obj.use_number - 1
                    developer_obj.save()

            udid_obj.delete()

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
    def clean_app_by_developer_obj(app_obj, developer_obj):
        auth = {
            "username": developer_obj.email,
            "password": developer_obj.password,
            "certid": developer_obj.certid
        }
        app_api_obj = AppDeveloperApi(**auth)
        app_api_obj.del_profile(app_obj.bundle_id, app_obj.app_id)
        app_api_obj2 = AppDeveloperApi(**auth)
        app_api_obj2.del_app(app_obj.bundle_id, app_obj.app_id)

    @staticmethod
    def clean_developer(developer_obj, user_obj):
        '''
        根据消耗记录 删除该苹果账户下所有信息
        :param developer_obj:
        :return:
        '''
        for APPToDeveloper_obj in APPToDeveloper.objects.filter(developerid=developer_obj):
            app_obj = APPToDeveloper_obj.app_id
            IosUtils.clean_app_by_developer_obj(app_obj, developer_obj)
            delete_app_to_dev_and_file(developer_obj, app_obj.id)
            IosUtils.clean_udid_by_app_obj(app_obj, developer_obj)
        full_path = file_format_path(user_obj, email=developer_obj.email)
        try:
            for root, dirs, files in os.walk(full_path, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(full_path)
        except Exception as e:
            logger.error("clean_developer developer_obj:%s user_obj:%s delete file failed Exception:%s" % (
                developer_obj, user_obj, e))

    @staticmethod
    def active_developer(developer_obj, user_obj):
        '''
        激活开发者账户
        :param developer_obj:
        :param code:
        :return:
        '''
        auth = {
            "username": developer_obj.email,
            "password": developer_obj.password,
            "certid": developer_obj.certid
        }
        app_api_obj = AppDeveloperApi(**auth)
        status, result = app_api_obj.active(user_obj)
        if status:
            developer_obj.is_actived = True
            developer_obj.save()
        return status, result

    @staticmethod
    def create_developer_cert(developer_obj, user_obj):
        auth = {
            "username": developer_obj.email,
            "password": developer_obj.password,
            "certid": developer_obj.certid
        }
        app_api_obj = AppDeveloperApi(**auth)
        status, result = app_api_obj.create_cert(user_obj)
        if status:
            file_format_path_name = file_format_path(user_obj, auth)
            cert_info = None
            try:
                with open(file_format_path_name + '.info', "r") as f:
                    cert_info = f.read()
            except Exception as e:
                logger.error("create_developer_cert developer_obj:%s user_obj:%s delete file failed Exception:%s" % (
                    developer_obj, user_obj, e))
            if cert_info:
                cert_id = re.findall(r'.*\n\tid=(.*),.*', cert_info)[0].replace('"', '')
                AppIOSDeveloperInfo.objects.filter(user_id=user_obj, email=auth.get("username")).update(is_actived=True,
                                                                                                        certid=cert_id)
        return status, result

    @staticmethod
    def get_device_from_developer(developer_obj, user_obj):
        auth = {
            "username": developer_obj.email,
            "password": developer_obj.password,
            "certid": developer_obj.certid
        }
        app_api_obj = AppDeveloperApi(**auth)
        status, result = app_api_obj.get_device(user_obj)
        if status:
            file_format_path_name = file_format_path(user_obj, auth)
            devices_info = ""
            try:
                with open(file_format_path_name + ".devices.info", "r") as f:
                    devices_info = f.read().replace("\n\t", "").replace("[", "").replace("]", "")
            except Exception as e:
                logger.error(
                    "get_device_from_developer developer_obj:%s user_obj:%s delete file failed Exception:%s" % (
                        developer_obj, user_obj, e))

            for devicestr in devices_info.split(">"):
                formatdevice = re.findall(r'.*Device id="(.*)",.*name="(.*)",.*udid="(.*?)",.*model=(.*),.*', devicestr)
                if formatdevice:
                    device = {
                        "serial": formatdevice[0][0],
                        "product": formatdevice[0][1],
                        "udid": formatdevice[0][2],
                        "version": formatdevice[0][3],
                    }
                    app_udid_obj = UDIDsyncDeveloper.objects.filter(developerid=developer_obj, udid=device.get("udid"))
                    if app_udid_obj:
                        pass
                    else:
                        UDIDsyncDeveloper.objects.create(developerid=developer_obj, **device)
        return status, result
