#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6
from fir_ser.settings import MEDIA_ROOT,MEDIA_URL
import os
from .firApi import AppInfo
from api.utils.randomstrings import make_app_uuid
from api.models import AppReleaseInfo,Apps
import random,xmltodict,json
from .TokenManager import DownloadToken


def make_download_token(release_id,time_limit):
    release_ids = []
    if release_id:
        release_ids = [release_id]
    dtoken = DownloadToken()
    download_token = dtoken.make_token(release_ids,time_limit)
    return download_token


def make_resigned(bin_url,img_url,bundle_id,bundle_version,name):

    ios_plist_tem = """
    {
        "plist": {
            "@version": "1.0",
            "dict": {
                "key": "items",
                "array": {
                    "dict": {
                        "key": [
                            "assets",
                            "metadata"
                        ],
                        "array": {
                            "dict": [
                                {
                                    "key": [
                                        "kind",
                                        "url"
                                    ],
                                    "string": [
                                        "software-package",
                                        "%s"
                                    ]
                                },
                                {
                                    "key": [
                                        "kind",
                                        "needs-shine",
                                        "url"
                                    ],
                                    "string": [
                                        "display-image",
                                        "%s"
                                    ],
                                    "integer": "0"
                                },
                                {
                                    "key": [
                                        "kind",
                                        "needs-shine",
                                        "url"
                                    ],
                                    "string": [
                                        "full-size-image",
                                        "%s"
                                    ],
                                    "true": null
                                }
                            ]
                        },
                        "dict": {
                            "key": [
                                "bundle-identifier",
                                "bundle-version",
                                "kind",
                                "title"
                            ],
                            "string": [
                                "%s",
                                "%s",
                                "software",
                                "%s"
                            ]
                        }
                    }
                }
            }
        }
    }
    """ % (bin_url, img_url, img_url, bundle_id, bundle_version, name)

    return xmltodict.unparse(json.loads(ios_plist_tem),pretty=True)

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if float(n) >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return '%sB' % n


def delete_apps_storage(app_file_name,release_type):
    app_path = os.path.join(MEDIA_ROOT,"apps")
    icon_path = os.path.join(MEDIA_ROOT,"icons")

    try:
        if release_type == 0:
            app_file_full_name="%s.apk" %app_file_name
        else:
            app_file_full_name="%s.ipa" %app_file_name

        remove_lists=[
            os.path.join(app_path, app_file_full_name),
            os.path.join(icon_path, "%s.png" % (app_file_name))
        ]
        for delfiles in remove_lists:
            os.remove(delfiles)
    except Exception as e:
        print(e)


def delete_apps_icon_storage(app_file_name,type='icons'):
    icon_path = os.path.join(MEDIA_ROOT,type)

    try:
        os.remove(os.path.join(icon_path, app_file_name))
    except Exception as e:
        print(e)


def get_release_type(app_file_name,appinfo):
    extension = app_file_name.split(".")[1]
    if extension == "ipa":
        release_type = appinfo.get("release_type")
        if release_type == "Adhoc": # Adhoc： 内测版   Inhouse：企业版
            return 1
        elif release_type == "Inhouse":
            return 2
        else:
            return 3
    else:
        return 0

def get_app_type(app_file_name):
    extension = app_file_name.split(".")[1]
    if extension == "ipa":
        return 1
    if extension == "apk":
        return 0
    else:
        return 2

def get_random_short():

    short_url = ''.join(random.sample(
        ['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f',
         'e', 'd', 'c', 'b', 'a'], 4))
    appobj=Apps.objects.filter(short=short_url).first()
    if appobj:
        return get_random_short()
    else:
        return short_url



def AnalyzeUtil(app_file_name,request):

    user_obj = request.user

    app_path = os.path.join(MEDIA_ROOT,"apps")
    icon_path = os.path.join(MEDIA_ROOT,"icons")
    app_full_path = os.path.join(app_path,app_file_name)

    try:
        apiobj = AppInfo(app_full_path)
        appinfo = apiobj.get_app_data()
        app_img=apiobj.make_app_png(icon_path,app_file_name.split(".")[0])
    except Exception as e:
        print(e)
        delete_apps_storage(app_file_name.split(".")[0], 0)
        delete_apps_storage(app_file_name.split(".")[0], 1)

        return


    bundle_id = appinfo.get("bundle_id")
    app_uuid = make_app_uuid(user_obj,bundle_id+app_file_name.split(".")[1])

    ##判断是否存在该app
    appmobj=Apps.objects.filter(app_id=app_uuid,user_id=user_obj).first()
    if not appmobj:
        appdata={
            "app_id":app_uuid,
            "user_id":user_obj,
            "type":get_app_type(app_file_name),
            "name": appinfo["labelname"],
            "short":get_random_short(),
            "bundle_id":bundle_id,
            "count_hits":0
        }
        try:
            appmobj=Apps.objects.create(**appdata)
        except Exception as e:
            print(e)
            delete_apps_storage(app_file_name.split(".")[0],get_release_type(app_file_name,appinfo))
            return





    AppReleaseInfo.objects.filter(app_id=appmobj).update(**{"is_master":False})

    release_data={
        "app_id":appmobj,
        "icon_url":"/".join([MEDIA_URL.strip("/"),"icons",app_img]),
        "release_id":app_file_name.split(".")[0],
        "build_version":appinfo.get("version"),
        "app_version":appinfo.get("versioncode"),
        "release_type":get_release_type(app_file_name,appinfo),
        "minimum_os_version":appinfo.get("miniOSversion", None),
        "binary_size":os.path.getsize(app_full_path),
        "is_master":True
    }

    AppReleaseInfo.objects.create(**release_data)



