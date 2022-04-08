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
