#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: NinEveN
# date: 2022/2/15
import logging

from django.dispatch import Signal, receiver

from api.models import Apps
from xsign.models import AppUDID, APPToDeveloper
from xsign.tasks import run_resign_task
from xsign.utils.supersignutils import IosUtils

logger = logging.getLogger(__name__)

"""
更新应用的时候，是否同时更新超级签名数据
"""
run_resign_task_signal = Signal(providing_args=["app_pk"])


@receiver(run_resign_task_signal)
def run_resign_task_callback(sender, **kwargs):
    app_obj = Apps.objects.filter(pk=kwargs.get('app_pk')).first()
    if app_obj:
        AppUDID.objects.filter(app_id=app_obj, sign_status__gte=3).update(sign_status=3)
        if app_obj.change_auto_sign:
            c_task = run_resign_task(app_obj.pk, False, False)
            logger.info(f"app {app_obj} run_resign_task end msg:{c_task}")


"""
删除应用时的信号，用户清理签名相关数据
"""

delete_app_signal = Signal(providing_args=["app_pk"])


@receiver(delete_app_signal)
def delete_app_callback(sender, **kwargs):
    app_obj = Apps.objects.filter(pk=kwargs.get('app_pk')).first()
    if app_obj:
        count = APPToDeveloper.objects.filter(app_id=app_obj).count()
        if app_obj.issupersign or count > 0:
            logger.info(f"app_id:{app_obj.app_id} is supersign ,delete this app need clean IOS developer")
            IosUtils.clean_app_by_user_obj(app_obj)
