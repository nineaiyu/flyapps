#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6

import uuid, xmltodict,os
from fir_ser.settings import SUPER_SIGN_ROOT,MEDIA_ROOT,SERVER_DOMAIN
from api.utils.app.iossignapi import AppDeveloperApi,ResignApp
from api.models import  APPSuperSignUsedInfo,AppUDID,AppIOSDeveloperInfo,AppReleaseInfo
from api.utils.app.randomstrings import make_app_uuid,make_from_user_uuid
from django.db.models import F

def udid_bytes_to_dict(xml_stream):
    new_uuid_info = {}
    try:
        a = xml_stream.find('<plist')
        b = xml_stream.find('</plist>')
        xml_dict = xmltodict.parse(xml_stream[a:b + 8])  # 解析xml字符串
        for i in range(len(xml_dict['plist']['dict']['key'])):
            new_uuid_info[xml_dict['plist']['dict']['key'][i].lower()] = xml_dict['plist']['dict']['string'][i]
    except Exception as e:
        print(e)
    return new_uuid_info


def make_udid_mobileconfig(udid_url, PayloadOrganization, PayloadUUID=uuid.uuid1(), PayloadDescription='本文件仅用来获取设备ID',
                           PayloadDisplayName='查询设备UDID'):
    # <!--参考:https://developer.apple.com/library/ios/documentation/NetworkingInternet/Conceptual/iPhoneOTAConfiguration/ConfigurationProfileExamples/ConfigurationProfileExamples.html-->
    mobileconfig = '''
<?xml version="1.0" encoding="UTF-8"?>
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

    PATH_INFO = request.META.get('PATH_INFO')
    PATH_INFO_lists = PATH_INFO.strip('/').split('/')
    PATH_INFO_lists[-1] = 'udid'
    PATH_INFO_lists.pop(-2)
    PATH_INFO_lists.append(short)
    PATH_INFO_lists.insert(0, server_domain)
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
    def __init__(self,udid_info,app_obj):
        self.udid_info=udid_info
        self.app_obj = app_obj
        self.user_obj = app_obj.user_id
        self.get_developer_auth()


    def get_developer_auth(self):
        developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=self.user_obj,is_actived=True,use_number__lte=F("usable_number")).first()
        auth = {
            "username":developer_obj.email,
            "password": developer_obj.password,
            "certid":developer_obj.certid
        }
        self.auth = auth


    def download_profile(self):
        app_api_obj = AppDeveloperApi(** self.auth)
        bundleId = self.app_obj.bundle_id
        app_id=self.app_obj.app_id
        device_udid= self.udid_info.get('udid')
        device_name=self.udid_info.get('product')
        app_api_obj.get_profile(bundleId,app_id,device_udid,device_name,self.get_profile_full_path())

    def get_profile_full_path(self):
        cert_dir_name = make_app_uuid(self.user_obj,self.auth.get("username"))
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT,cert_dir_name)
        file_format_path_name = os.path.join(cert_dir_path,cert_dir_name,"profile")
        if not os.path.isdir(file_format_path_name):
            os.makedirs(file_format_path_name)
        provisionName = os.path.join(file_format_path_name,self.app_obj.app_id)
        return provisionName+ '.mobileprovision'

    def resign(self):
        self.download_profile()
        cert_dir_name = make_app_uuid(self.app_obj.user_id,self.auth.get("username"))
        cert_dir_path = os.path.join(SUPER_SIGN_ROOT,cert_dir_name)
        if not os.path.isdir(cert_dir_path):
            os.makedirs(cert_dir_path)
        file_format_path_name = os.path.join(cert_dir_path,cert_dir_name)

        my_local_key=file_format_path_name+".key"
        app_dev_pem =file_format_path_name+".pem"
        ResignAppObj = ResignApp(my_local_key,app_dev_pem)

        random_file_name = make_from_user_uuid(self.user_obj)

        release_obj = AppReleaseInfo.objects.filter(app_id=self.app_obj,is_master=True).first()

        org_file = os.path.join(MEDIA_ROOT, release_obj.release_id + ".ipa")
        new_file = os.path.join(MEDIA_ROOT, random_file_name + ".ipa")
        ResignAppObj.sign(self.get_profile_full_path(),org_file,new_file)

        newdata={
           "is_signed":True,
            "binary_file":random_file_name + ".ipa"
        }
        AppUDID.objects.filter(app_id=self.app_obj,udid=self.udid_info.get('udid')).update(**newdata)
