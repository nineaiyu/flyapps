#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7
import datetime
import logging
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor

from django.template import loader

from common.core.sysconfig import Config
from common.notify.notify import check_developer_status_notify
from fir_ser.settings import SUPER_SIGN_ROOT, SYNC_CACHE_TO_DATABASE
from xsign.models import UserInfo, AppIOSDeveloperInfo, APPSuperSignUsedInfo
from xsign.utils.modelutils import get_developer_devices
from xsign.utils.supersignutils import IosUtils

logger = logging.getLogger(__name__)


def auto_delete_ios_mobile_tmp_file():
    mobile_config_tmp_dir = os.path.join(SUPER_SIGN_ROOT, 'tmp', 'mobile_config')
    for root, dirs, files in os.walk(mobile_config_tmp_dir, topdown=False):
        now_time = time.time()
        for name in files:
            file_path = os.path.join(root, name)
            st_mtime = os.stat(file_path).st_mtime
            if now_time - st_mtime > SYNC_CACHE_TO_DATABASE.get('clean_local_tmp_file_from_mtime', 30 * 60):
                try:
                    os.remove(file_path)
                except Exception as e:
                    logger.error(f"auto_delete_tmp_file {file_path} Failed . Exception {e}")


def auto_check_ios_developer_active():
    error_issuer_id = {}

    def check_active_task(developer_obj):
        time.sleep(random.randint(1, 5))
        user_obj = developer_obj.user_id
        err_issuer_id = error_issuer_id.get(user_obj.uid, [])
        if user_obj.supersign_active:
            status, result = IosUtils.active_developer(developer_obj, False)
            msg = f"auto_check_ios_developer_active  user:{user_obj}  ios.developer:{developer_obj}  status:{status}  result:{result}"
            err_issuer_id.append(developer_obj)
            error_issuer_id[user_obj.uid] = list(set(err_issuer_id))

            if status:
                IosUtils.get_device_from_developer(developer_obj)
                logger.info(msg)
            else:
                logger.error(msg)

    ios_developer_queryset = AppIOSDeveloperInfo.objects.filter(status__in=Config.DEVELOPER_AUTO_CHECK_STATUS,
                                                                auto_check=True, user_id__is_active=True,
                                                                user_id__supersign_active=True)
    pools = ThreadPoolExecutor(10)

    for ios_developer_obj in ios_developer_queryset:
        pools.submit(check_active_task, ios_developer_obj)
    pools.shutdown()

    for uid, developer_obj_list in error_issuer_id.items():
        userinfo = UserInfo.objects.filter(uid=uid).first()
        developer_used_info = get_developer_devices(AppIOSDeveloperInfo.objects.filter(user_id=userinfo))

        end_time = datetime.datetime.now().date()
        start_time = end_time - datetime.timedelta(days=1)
        yesterday_used_number = APPSuperSignUsedInfo.objects.filter(developerid__user_id=userinfo,
                                                                    created_time__range=[start_time, end_time]).count()
        content = loader.render_to_string('check_developer.html',
                                          {
                                              'username': userinfo.first_name,
                                              'developer_obj_list': developer_obj_list,
                                              'developer_used_info': developer_used_info,
                                              'yesterday_used_number': yesterday_used_number,
                                          })
        # send_ios_developer_active_status(userinfo, content)
        check_developer_status_notify(userinfo, developer_obj_list, content)
