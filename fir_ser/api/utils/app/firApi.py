#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 12月 
# author: NinEveN
# date: 2019/12/19

import requests
import zipfile, re, os, random,io
from androguard.core.bytecodes import apk
import plistlib
import qrcode
from PIL import Image


def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return '%sB' % n



class AppInfo(object):
    def __init__(self, app_path):
        self.app_path = app_path
        self.result = {}

    def make_app_png(self,png_path,filename):
        zf = zipfile.ZipFile(self.app_path)
        name_list = zf.namelist()
        if self.app_path.endswith("apk"):
            # pattern = re.compile(r'res/drawable[^/]*/app_icon.png')
            iconfile = apk.APK(self.app_path).get_app_icon()
            size = 999

        elif self.app_path.endswith("ipa"):
            size = 0
            pattern = re.compile(r'Payload/[^/]*.app/AppIcon[^/]*[^(ipad)].png')
            iconfile = ""
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

        else:
            raise Exception("File type error")

        if size == 0:
            raise Exception("File size error")


        if not os.path.isdir(png_path):
            os.makedirs(png_path)

        with open(os.path.join(png_path, "%s.png" %filename), 'wb') as f:
            f.write(zf.read(iconfile))

        return "%s.png" %filename

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
                sdk_version = apkobj.get_min_sdk_version()
                self.result = {
                    "labelname": labelname,
                    "bundle_id": bundle_id,
                    "versioncode": versioncode,
                    "version": version,
                    "miniOSversion": sdk_version,
                    "type": "android",
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
                miniOSversion  = plist_root["MinimumOSVersion"]
                self.result = {
                    "labelname": labelname,
                    "bundle_id": bundle_id,
                    "versioncode": versioncode,
                    "version": version,
                    "miniOSversion":miniOSversion,
                    "type": "ios",
                }

            release_type_info = self.__get_ios_release_type(ipaobj)
            if info_path:
                plist_data = ipaobj.read(release_type_info)
                if b"ProvisionedDevices" in plist_data:
                    self.result["release_type"] = "Adhoc"
                else:
                    self.result["release_type"] = "Inhouse"
        return self.result

    def __get_ios_release_type(self, ipaobj):
        infopath_re = re.compile(r'Payload/[^/]*.app/embedded.mobileprovision')
        for i in ipaobj.namelist():
            m = infopath_re.match(i)
            if m is not None:
                return m.group()


class FirApi(object):
    def __init__(self, api_token):
        '''
        :param api_token: 长度为 32, 用户在 fir 的 api_token
        '''
        self.api_token = api_token
        self.app_url = "http://api.fir.im/apps"

    def __request(self, action, *args, **kwargs):

        fun_re = getattr(requests, action, None)
        res = fun_re(*args, **kwargs)
        return res

    def get_version_by_id(self, id):
        '''

        :param id: 应用ID，可在"应用管理"->"基本信息"查看
        :return:
        '''
        url = "%s/latest/%s?api_token=%s" % (self.app_url, id, self.api_token)
        res = self.__request("get", url)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(res.content)

    def get_version_by_bundle_id(self, bundle_id, type):
        '''

        :param bundle_id: Bundle ID(iOS) / Package name(Android)
        :param type: 应用类型 ( ios / android )
        :return:
        '''
        url = "%s/latest/%s?api_token=%s&type=%s" % (self.app_url,
                                                     bundle_id, self.api_token,
                                                     type)  # 使用 bundle_id 请求必填 ( ios / android )
        res = self.__request("get", url)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(res.content)

    def __get_upload_token(self, bundle_id, type):
        '''

        :param bundle_id: App 的 bundleId（发布新应用时必填）
        :param type: ios 或者 android（发布新应用时必填）
        :return:
        '''
        data = {
            "type": type,
            "bundle_id": bundle_id,
            "api_token": self.api_token,
        }
        res = self.__request("post", self.app_url, data)
        if res.status_code == 201:
            return res.json()
        else:
            raise Exception(res.content)

    def upload_app(self, app_path):
        appobj = AppInfo(app_path)
        appinfo = appobj.get_app_data()
        icon_path = appobj.make_app_png()
        bundle_id = appinfo.get("bundle_id")
        upcretsdata = self.__get_upload_token(bundle_id, appinfo.get("type"))

        icon_key = upcretsdata["cert"]["icon"]["key"]
        icon_token = upcretsdata["cert"]["icon"]["token"]
        icon_upload_url = upcretsdata["cert"]["icon"]["upload_url"]
        short_url = upcretsdata["short"]

        icon_data = {
            "key": icon_key,
            "token": icon_token,
        }
        files = {'file': (os.path.basename(icon_path), open(icon_path, 'rb'), {'Expires': '0'})}
        res = self.__request("post", icon_upload_url, data=icon_data, files=files)
        if res.status_code == 200:
            print(res.json())
        else:
            raise Exception(res.content)

        binary_key = upcretsdata["cert"]["binary"]["key"]
        binary_token = upcretsdata["cert"]["binary"]["token"]
        binary_upload_url = upcretsdata["cert"]["binary"]["upload_url"]

        binary_data = {
            "key": binary_key,
            "token": binary_token,
            "x:name": appinfo["labelname"],
            "x:version": appinfo["version"],
            "x:build": appinfo["versioncode"],
            "x:changelog": ""
        }

        if appinfo["type"] == "ios": binary_data["x:release_type"] = appinfo.get("release_type",
                                                                                 "Adhoc")  # Adhoc： 内测版   Inhouse：企业版

        files = {'file': (os.path.basename(app_path), open(app_path, 'rb'), {'Expires': '0'})}
        res = self.__request("post", binary_upload_url, data=binary_data, files=files)
        if res.status_code == 200:
            print(res.json())
            QrCode.make_logo_qr(os.path.join("https://fir.im/", short_url), icon_path, "fir_%s.png"%(appinfo["labelname"]))

        else:
            raise Exception(res.content)


    def get_app_list(self):
        url = "%s?api_token=%s" % (self.app_url, self.api_token)
        res = self.__request("get", url)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(res.content)

    def get_app_infos_by_id(self, id):
        '''

        :param id: 应用id，可在"应用管理"->"基本信息"查看
        :return:
        '''
        url = "%s/%s?api_token=%s" % (self.app_url, id, self.api_token)
        res = self.__request("get", url)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(res.content)

    def modify_app_info(self, id, name=None, desc=None, short=None, genre_id=None,
                        is_opened=None, is_show_plaza=None, passwd=None,
                        store_link_visible=None):
        '''

        :param id: 应用id，可在"应用管理"->"基本信息"查看
        :param name: app 名称
        :param desc: app 详细描述
        :param short: 	app 短链接
        :param genre_id: 类别 id
        :param is_opened: 是否公开
        :param is_show_plaza: 是否展示在广场页
        :param passwd: 密码访问(不能和is_opened is_show_plaza联合使用)
        :param store_link_visible: 应用市场链接是否显示
        :return:
        '''
        url = "%s/%s" % (self.app_url, id)
        data = {
            "api_token": self.api_token,
        }
        if name: data["name"] = name
        if desc: data["desc"] = desc
        if short: data["short"] = short
        if genre_id: data["genre_id"] = genre_id
        if is_opened: data["is_opened"] = is_opened
        if is_show_plaza and not passwd: data["is_show_plaza"] = is_show_plaza
        if passwd and not is_show_plaza: data["passwd"] = passwd
        if is_show_plaza and passwd:
            raise Exception("密码访问不能和is_opened is_show_plaza联合使用")
        if store_link_visible: data["name"] = store_link_visible

        res = self.__request("put", url, data)
        if res.status_code == 200:
            return res.json()
        else:
            raise Exception(res.content)


class QrCode(object):

    @staticmethod
    def make_logo_qr(str, logo_path, save_path=None):
        qr = qrcode.QRCode(
            version=4,
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=8,
            border=2
        )
        # 添加转换内容
        qr.add_data(str)
        qr.make(fit=True)
        # 生成二维码
        img = qr.make_image()
        #
        img = img.convert("RGBA")

        # 添加logo
        if logo_path and os.path.exists(logo_path):
            icon = Image.open(logo_path)
            # 获取二维码图片的大小
            img_w, img_h = img.size

            factor = 4
            size_w = int(img_w / factor)
            size_h = int(img_h / factor)

            # logo图片的大小不能超过二维码图片的1/4
            icon_w, icon_h = icon.size
            if icon_w > size_w:
                icon_w = size_w
            if icon_h > size_h:
                icon_h = size_h
            icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
            # 详见：http://pillow.readthedocs.org/handbook/tutorial.html

            # 计算logo在二维码图中的位置
            w = int((img_w - icon_w) / 2)
            h = int((img_h - icon_h) / 2)
            icon = icon.convert("RGBA")
            img.paste(icon, (w, h), icon)
            # 详见：http://pillow.readthedocs.org/reference/Image.html#PIL.Image.Image.paste

        # 保存处理后图片
        if save_path:
            if not os.path.isdir(os.path.dirname(save_path)):
                os.makedirs(os.path.dirname(save_path))
            img.save(save_path)
        else:
            imgByteArr = io.BytesIO()
            img.save(imgByteArr,format="PNG")
            return imgByteArr.getvalue()

if __name__ == '__main__':
    apk_path = "/root/hehemajiang.apk"
    API_TOKEN = "3d2a41159a7d8c396ddf0e88799de14a"

    fir = FirApi(API_TOKEN)

    #上传
    fir.upload_app(apk_path)

    # 获取版本信息
    # print(fir.get_version_by_id("5dfb54d3b2eb4612589c3040"))

    #获取app详细信息
    # print(fir.get_app_infos_by_id("5dfb54d3b2eb4612589c3040"))
    #获取列表
    # print(fir.get_app_list())

