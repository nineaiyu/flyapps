#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 1月 
# author: NinEveN
# date: 2021/1/9
import os
import sys
import plistlib
import random
import re
import json
import zipfile

from oss2 import determine_part_size, SizedFileAdapter
from oss2.models import PartInfo
from requests_toolbelt.multipart.encoder import MultipartEncoderMonitor
import oss2
import requests
from androguard.core.bytecodes import apk

'''
pip install --upgrade pip
pip install setuptools-rust
pip install oss2
pip install requests-toolbelt
pip install androguard
'''


def progress(percent, width=50):
    if percent >= 1:
        percent = 1
    show_str = ('[%%-%ds]' % width) % (int(width * percent) * '#')
    print('\r%s %d%% ' % (show_str, int(100 * percent)), file=sys.stdout, flush=True, end='')


def local_upload_callback(monitor):
    progress(monitor.bytes_read / monitor.len, width=100)


def qiniu_progress_callback(upload_size, total_size):
    progress(upload_size / total_size, width=100)


def alioss_progress_callback_fun(offset, total_size):
    def progress_callback(upload_size, now_part_size):
        percent = (offset + upload_size) / total_size  # 接收的比例
        progress(percent, width=100)

    return progress_callback


def upload_aliyunoss(access_key_id, access_key_secret, security_token, endpoint, bucket, local_file_full_path, filename,
                     headers=None):
    stsauth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
    bucket = oss2.Bucket(stsauth, endpoint, bucket)
    total_size = os.path.getsize(local_file_full_path)
    # determine_part_size方法用于确定分片大小。
    part_size = determine_part_size(total_size, preferred_size=1024 * 1024 * 10)
    upload_id = bucket.init_multipart_upload(filename, headers=headers).upload_id
    parts = []
    # 逐个上传分片。

    with open(local_file_full_path, 'rb') as f:
        part_number = 1
        offset = 0
        while offset < total_size:
            num_to_upload = min(part_size, total_size - offset)
            result = bucket.upload_part(filename, upload_id, part_number,
                                        SizedFileAdapter(f, num_to_upload),
                                        progress_callback=alioss_progress_callback_fun(offset, total_size))
            parts.append(PartInfo(part_number, result.etag))
            offset += num_to_upload
            part_number += 1
    bucket.complete_multipart_upload(filename, upload_id, parts)
    print("数据上传存储成功.")


def upload_qiniuyunoss(key, token, file_path):
    from qiniu import put_file
    ret, info = put_file(token, key, file_path, progress_handler=qiniu_progress_callback)
    if info.status_code == 200:
        print("数据上传存储成功.")
    else:
        raise AssertionError(info.text)


class FLYCliSer(object):

    def __init__(self, fly_cli_domain, fly_cli_token):
        self.fly_cli_domain = fly_cli_domain
        self._header = {
            "User-Agent": "fly-cli",
            "accept": "application/json",
            "APIAUTHORIZATION": fly_cli_token
        }

    def get_upload_token(self, bundleid, type):
        url = '%s/api/v2/fir/server/analyse' % self.fly_cli_domain
        data = {"bundleid": bundleid, "type": type}
        req = requests.post(url, json=data, headers=self._header)
        if req.status_code == 200:
            if req.json()['code'] == 1000:
                return req.json()['data']
        raise AssertionError(req.text)

    def analyse(self, data):
        url = '%s/api/v2/fir/server/analyse' % self.fly_cli_domain

        req = requests.put(url, json=data, headers=self._header)
        if req.status_code == 200:
            if req.json()['code'] == 1000:
                print("APP信息更新成功" + req.text)
                return
        raise AssertionError(req.text)

    def upload_local_storage(self, upload_key, upload_token, app_id, file_path):
        url = '%s/api/v2/fir/server/upload' % self.fly_cli_domain
        m = MultipartEncoderMonitor.from_fields(fields={
            'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream'),
            'certinfo': json.dumps(
                {
                    'upload_key': upload_key,
                    'upload_token': upload_token,
                    'ftype': "app",
                    'app_id': app_id,
                }
            ),
        }, callback=local_upload_callback)
        header = {
            'Content-Type': m.content_type,
        }
        req = requests.post(url, data=m, headers={**self._header, **header})
        if req.status_code == 200:
            if req.json()['code'] == 1000:
                print("数据上传存储成功." + req.text)
                return
        raise AssertionError(req.text)

    def upload_app(self, app_path):
        appobj = AppInfo(app_path)
        appinfo = appobj.get_app_data()
        icon_path = appobj.make_app_png(icon_path=appinfo.get("icon_path", None))
        bundle_id = appinfo.get("bundle_id")
        upcretsdata = self.get_upload_token(bundle_id, appinfo.get("type"))
        if appinfo.get('iOS', '') == 'iOS':
            f_type = '.ipa'
        else:
            f_type = '.apk'
        filename = "%s-%s-%s%s" % (appinfo.get('labelname'), appinfo.get('version'), upcretsdata.get('short'), f_type)
        headers = {
            'Content-Disposition': 'attachment; filename="%s"' % filename.encode(
                "utf-8").decode("latin1"),
            'Cache-Control': ''
        }
        if upcretsdata['storage'] == 1:
            # 七牛云存储
            upload_qiniuyunoss(upcretsdata['png_key'], upcretsdata['png_token'], icon_path)
            upload_qiniuyunoss(upcretsdata['upload_key'], upcretsdata['upload_token'], app_path)

        elif upcretsdata['storage'] == 2:
            # 阿里云存储
            png_auth = upcretsdata['png_token']

            upload_aliyunoss(png_auth['access_key_id'], png_auth['access_key_secret'], png_auth['security_token'],
                             png_auth['endpoint'], png_auth['bucket'], icon_path, upcretsdata['png_key'])
            file_auth = upcretsdata['upload_token']

            upload_aliyunoss(file_auth['access_key_id'], file_auth['access_key_secret'], file_auth['security_token'],
                             file_auth['endpoint'], file_auth['bucket'], app_path, upcretsdata['upload_key'], headers)
        elif upcretsdata['storage'] == 3:
            # 本地存储
            self.upload_local_storage(upcretsdata['png_key'], upcretsdata['png_token'], upcretsdata['app_uuid'],
                                      icon_path)
            self.upload_local_storage(upcretsdata['upload_key'], upcretsdata['upload_token'], upcretsdata['app_uuid'],
                                      app_path)

        app_data = {
            "filename": os.path.basename(app_path),
            "filesize": os.path.getsize(app_path),
            "appname": appinfo['labelname'],
            "bundleid": appinfo['bundle_id'],
            "version": appinfo['version'],
            "buildversion": appinfo['versioncode'],
            "miniosversion": appinfo['miniosversion'],
            "release_type": appinfo.get('release_type', ''),
            "release_type_id": 2,
            "udid": appinfo.get('udid', []),
            "type": appinfo['type'],
        }
        self.analyse({**app_data, **upcretsdata})


class AppInfo(object):
    def __init__(self, app_path):
        self.app_path = app_path
        self.result = {}

    def make_app_png(self, icon_path):
        zf = zipfile.ZipFile(self.app_path)
        iconfile = ""
        if icon_path:
            size = len(zf.read(icon_path))
            iconfile = icon_path
        else:
            name_list = zf.namelist()
            if self.app_path.endswith("apk"):
                pattern = re.compile(r'res/drawable[^/]*/app_icon.png')
            elif self.app_path.endswith("ipa"):
                pattern = re.compile(r'Payload/[^/]*.app/AppIcon[^/]*[^(ipad)].png')
            else:
                raise Exception("File type error")

            size = 0
            for path in name_list:
                m = pattern.match(path)
                if m is not None:
                    filepath = m.group()
                    fsize = len(zf.read(filepath))
                    if size == 0:
                        iconfile = filepath
                    if size < fsize:
                        size = fsize
                        iconfile = filepath
        if size == 0:
            raise Exception("File size error")
        if iconfile == "":
            raise Exception("read File icon error")

        filename = ''.join(random.sample(
            ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f',
             'e', 'd', 'c', 'b', 'a'], 16))
        if not os.path.isdir(os.path.join("tmp", "icon")):
            os.makedirs(os.path.join("tmp", "icon"))
        with open(os.path.join("tmp", "icon", filename + '.png'), 'wb') as f:
            f.write(zf.read(iconfile))

        return os.path.join("tmp", "icon", filename + '.png')

    def get_app_data(self):
        if self.app_path.endswith("apk"):
            return self.__get_android_data()
        elif self.app_path.endswith("ipa"):
            return self.__get_ios_data()
        else:
            raise Exception("File type error")

    def __get_ios_info_path(self, ipaobj):
        infopath_re = re.compile(r'Payload/[^/]*.app/Info.plist')
        for i in ipaobj.namelist():
            m = infopath_re.match(i)
            if m is not None:
                return m.group()

    def __get_android_data(self):
        try:
            apkobj = apk.APK(self.app_path)
        except Exception as err:
            raise err
        else:
            if apkobj.is_valid_APK():
                versioncode = apkobj.get_androidversion_code()
                bundle_id = apkobj.get_package()
                labelname = apkobj.get_app_name()
                version = apkobj.get_androidversion_name()
                self.result = {
                    "labelname": labelname,
                    "bundle_id": bundle_id,
                    "versioncode": versioncode,
                    "version": version,
                    "type": "Android",
                    "miniosversion": apkobj.get_min_sdk_version(),
                    "icon_path": apkobj.get_app_icon()
                }
        return self.result

    def __get_ios_data(self):
        if zipfile.is_zipfile(self.app_path):
            ipaobj = zipfile.ZipFile(self.app_path)
            info_path = self.__get_ios_info_path(ipaobj)
            if info_path:
                plist_data = ipaobj.read(info_path)
                plist_root = plistlib.loads(plist_data)
                labelname = plist_root['CFBundleDisplayName']
                versioncode = plist_root['CFBundleVersion']
                bundle_id = plist_root['CFBundleIdentifier']
                version = plist_root['CFBundleShortVersionString']
                self.result = {
                    "labelname": labelname,
                    "bundle_id": bundle_id,
                    "versioncode": versioncode,
                    "version": version,
                    "type": "iOS",
                    "miniosversion": plist_root['MinimumOSVersion']
                }

            release_type_info = self.__get_ios_release_type(ipaobj)
            if info_path:
                plist_data = ipaobj.read(release_type_info)
                if b"ProvisionedDevices" in plist_data:
                    b = re.findall(rb'<key>ProvisionedDevices</key><array>(.*)</array><key>TeamIdentifier</key>',
                                   plist_data.replace(b'\n', b'').replace(b'\r', b'').replace(b"\t", b""))[0]
                    clist = re.split(rb'<string>|</string>', b)
                    nudidlist = []
                    for x in clist:
                        if x:
                            nudidlist.append(x.decode('utf-8'))
                    self.result["release_type"] = "Adhoc"
                    self.result['udid'] = nudidlist
                else:
                    self.result["release_type"] = "Inhouse"
                    self.result["udid"] = []
        return self.result

    def __get_ios_release_type(self, ipaobj):
        infopath_re = re.compile(r'Payload/[^/]*.app/embedded.mobileprovision')
        for i in ipaobj.namelist():
            m = infopath_re.match(i)
            if m is not None:
                return m.group()


if __name__ == '__main__':
    fly_cli_domain = 'https://app.hehelucky.cn'
    fly_cli_token = 'f63d05d2bb0511eb9fa400163e069e27oTa51Q3N6rJT5yjddCrkmgiFeKRQNa0L3TctPLTYd0CrdIqgO3wfYCKsFnJysQXJ'
    fly_obj = FLYCliSer(fly_cli_domain, fly_cli_token)
    if len(sys.argv) != 2:
        raise ValueError('参数有误')
    app_path = sys.argv[1]
    if os.path.isfile(app_path):
        fly_obj.upload_app(app_path)
    else:
        raise FileNotFoundError(app_path)
