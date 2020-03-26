#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6
from api.utils.app.randomstrings import make_app_uuid
from api.models import AppReleaseInfo,Apps
import random,xmltodict,json
from api.utils.storage.storage import Storage

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



def SaveAppInfos(app_file_name,user_obj,appinfo,bundle_id,app_img,short,size):
    app_uuid = make_app_uuid(user_obj,bundle_id+app_file_name.split(".")[1])
    ##判断是否存在该app
    appmobj = Apps.objects.filter(app_id=app_uuid, user_id=user_obj).first()
    storage = Storage(user_obj)
    if not appmobj:
        appdata = {
            "app_id": app_uuid,
            "user_id": user_obj,
            "type": get_app_type(app_file_name),
            "name": appinfo["labelname"],
            "short": short,
            "bundle_id": bundle_id,
            "count_hits": 0
        }
        try:
            appmobj = Apps.objects.create(**appdata)
        except Exception as e:
            print(e)
            storage.delete_file(app_file_name)
            storage.delete_file(app_img)
            return
    else:
        try:
            appmobj.short = short
            appmobj.name = appinfo["labelname"]
            appmobj.save()
        except Exception as e:
            print(e)
            appmobj.name = appinfo["labelname"]
            appmobj.save()

    AppReleaseInfo.objects.filter(app_id=appmobj).update(**{"is_master": False})

    release_data = {
        "app_id": appmobj,
        "icon_url": app_img,
        "release_id": app_file_name.split(".")[0],
        "build_version": appinfo.get("version"),
        "app_version": appinfo.get("versioncode"),
        "release_type": get_release_type(app_file_name, appinfo),
        "minimum_os_version": appinfo.get("miniOSversion", None),
        "binary_size": size,
        "is_master": True,
        "changelog":appinfo.get("changelog",'')
    }

    AppReleaseInfo.objects.create(**release_data)
    try:
        history_release_limit = int(user_obj.history_release_limit)
    except Exception as e:
        print(e)
        return

    if history_release_limit == 0:
        pass
    else:
        release_queryset = AppReleaseInfo.objects.filter(app_id=appmobj).order_by("-created_time")
        if release_queryset.count() > history_release_limit:
            flag = 0
            for release_obj in release_queryset:
                flag +=1
                if flag > history_release_limit:
                    storage.delete_file(release_obj.release_id,appmobj.type)
                    storage.delete_file(release_obj.icon_url)
                    release_obj.delete()

