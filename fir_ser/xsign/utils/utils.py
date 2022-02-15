#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月
# author: liuyu
# date: 2020/5/7
import logging

from api.utils.utils import delete_local_files
from common.utils.storage import Storage
from xsign.models import APPToDeveloper

logger = logging.getLogger(__name__)


def delete_app_to_dev_and_file(developer_obj, app_id):
    app_to_developer_obj = APPToDeveloper.objects.filter(developerid=developer_obj, app_id_id=app_id)
    if app_to_developer_obj:
        binary_file = app_to_developer_obj.first().binary_file + ".ipa"
        delete_local_files(binary_file)
        storage = Storage(developer_obj.user_id)
        storage.delete_file(binary_file)
        app_to_developer_obj.delete()


def make_resigned(bin_url, img_url, bundle_id, app_version, name):
    ios_plist_tem = """<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict>
  <key>items</key>
  <array>
    <dict>
      <key>assets</key>
      <array>
        <dict>
          <key>kind</key>
          <string>software-package</string>
          <key>url</key>
          <string><![CDATA[{bin_url}]]></string>
        </dict>
        <dict>
          <key>kind</key>
          <string>display-image</string>
          <key>needs-shine</key>
          <integer>0</integer>
          <key>url</key>
          <string><![CDATA[{img_url}]]></string>
        </dict>
        <dict>
          <key>kind</key>
          <string>full-size-image</string>
          <key>needs-shine</key>
          <true/>
          <key>url</key>
          <string><![CDATA[{img_url}]]></string>
        </dict>
      </array>
      <key>metadata</key>
      <dict>
        <key>bundle-identifier</key>
        <string>{bundle_id}</string>
        <key>bundle-version</key>
        <string><![CDATA[{app_version}]]></string>
        <key>kind</key>
        <string>software</string>
        <key>title</key>
        <string><![CDATA[{name}]]></string>
      </dict>
    </dict>
  </array>
</dict>
</plist>""".format(bin_url=bin_url, img_url=img_url, bundle_id=bundle_id, app_version=app_version, name=name)
    logger.info(
        f"make_resigned bin_url {bin_url} ,img_url {img_url}, bundle_id {bundle_id}, app_version {app_version}, name {name}")
    return ios_plist_tem
