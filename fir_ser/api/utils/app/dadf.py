#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 12月 
# author: NinEveN
# date: 2019/12/19

import re
import os
import zipfile
# from biplist import *
from androguard.core.bytecodes import apk
import plistlib


def get_android_data(package_file):
    try:
        apkobj = apk.APK(package_file)
    except Exception as err:
        print(err)
    else:
        if apkobj.is_valid_APK():
            versioncode = apkobj.get_androidversion_code()
            bundle_id = apkobj.get_package()
            labelname = apkobj.get_app_name()
            versioname = apkobj.get_androidversion_name()
            sdk_version = apkobj.get_target_sdk_version()
            return labelname, bundle_id, versioncode, versioname, sdk_version


def get_ios_data(ios_file):
    if zipfile.is_zipfile(ios_file):
        ipaobj = zipfile.ZipFile(ios_file)
        info_path = get_ios_info_path(ipaobj)
        if info_path:
            plist_data = ipaobj.read(info_path)
            print(plist_data)
            if b"ProvisionedDevices" in plist_data:
                print("adhoc")
            else:
                print("inhouse")


def get_ios_info_path(ipaobj):
    infopath_re = re.compile(r'.*.app/embedded.mobileprovision')
    for i in ipaobj.namelist():
        m = infopath_re.match(i)
        if m is not None:
            return m.group()


def get_ios_icon_path(ipaobj):
    infopath_re = re.compile(r'Payload/[^/]*.app/AppIcon[^/]*[^(ipad)].png')
    for i in ipaobj.namelist():
        m = infopath_re.match(i)
        if m is not None:
            return m.group()


def get_package_size(package_path):
    fsize = os.path.getsize(package_path)
    fsize = fsize / float(1024 * 1024)
    return round(fsize, 2)


# a=get_ios_data("/root/v1.1.8/Riot.ipa")
# print(a)

ipaobj = zipfile.ZipFile("M:\\Breeze.ipa")
info_path = get_ios_icon_path(ipaobj)
print(info_path)

with open('111222.png', 'wb') as f:
    f.write(ipaobj.read(info_path))
