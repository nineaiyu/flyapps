#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6
import logging

from rest_framework.views import APIView

from api.models import Apps
from common.cache.state import MigrateStorageState, CleanAppSignDataState
from common.constants import SignStatus
from common.core.auth import ExpiringTokenAuthentication
from common.core.response import ApiResponse
from common.core.sysconfig import Config
from common.utils.caches import del_cache_response_by_short
from xsign.models import AppUDID
from xsign.tasks import run_resign_task
from xsign.utils.modelutils import get_app_sign_info, check_super_sign_permission
from xsign.utils.supersignutils import IosUtils

logger = logging.getLogger(__name__)


class AppSignInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request, app_id):
        data = None
        if app_id:
            app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if app_obj:
                data = get_app_sign_info(app_obj)
            else:
                logger.error(f"app_id:{app_id} is not found in user:{request.user}")
                return ApiResponse(code=1003, msg="应用不存在")

        return ApiResponse(data=data)

    def put(self, request, app_id):
        if app_id:
            data = request.data
            if MigrateStorageState(request.user.uid).get_state():
                return ApiResponse(code=1008, msg="数据迁移中，无法处理该操作")

            clean = data.get("clean", None)
            if clean:
                with CleanAppSignDataState(request.user.uid) as state:
                    if state:
                        logger.info(f"app_id:{app_id} clean:{clean} ,close super_sign should clean_app_by_user_obj")
                        app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
                        IosUtils.clean_app_by_user_obj(app_obj)
                    else:
                        return ApiResponse(code=1008, msg="数据清理中,请耐心等待")
                return ApiResponse()

            try:
                do_sign_flag = 0
                app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
                logger.info(f"app_id:{app_id} update old data:{app_obj.__dict__}")
                update_fields = []
                if app_obj.issupersign:
                    app_obj.supersign_limit_number = data.get("supersign_limit_number", app_obj.supersign_limit_number)
                    app_obj.supersign_redirect_url = data.get("supersign_redirect_url", app_obj.supersign_redirect_url)
                    app_obj.abnormal_redirect = data.get("abnormal_redirect", app_obj.abnormal_redirect)
                    update_fields.extend(["supersign_limit_number", "supersign_redirect_url", "abnormal_redirect"])
                    if app_obj.supersign_type in [x[0] for x in list(app_obj.supersign_type_choices)]:
                        if app_obj.supersign_type != data.get("supersign_type", app_obj.supersign_type):
                            do_sign_flag = 1
                        app_obj.supersign_type = data.get("supersign_type", app_obj.supersign_type)
                        update_fields.append("supersign_type")
                    new_bundle_id = data.get("new_bundle_id", None)
                    new_bundle_name = data.get("new_bundle_name", None)
                    if new_bundle_id is not None:
                        if new_bundle_id and new_bundle_id != app_obj.bundle_id and len(new_bundle_id) > 3:
                            if new_bundle_id != app_obj.new_bundle_id:
                                do_sign_flag = 2
                            app_obj.new_bundle_id = new_bundle_id
                        if new_bundle_id == '' or (app_obj.new_bundle_id != new_bundle_id):
                            if app_obj.bundle_id != app_obj.new_bundle_id:
                                do_sign_flag = 2
                            app_obj.new_bundle_id = app_obj.bundle_id
                        update_fields.append('new_bundle_id')
                    if new_bundle_name is not None:
                        if new_bundle_name and new_bundle_name != app_obj.name and len(new_bundle_name) > 0:
                            if new_bundle_name != app_obj.new_bundle_name:
                                do_sign_flag = 2
                            app_obj.new_bundle_name = new_bundle_name
                        if new_bundle_name == '' or (app_obj.new_bundle_name != new_bundle_name):
                            if app_obj.name != app_obj.new_bundle_name:
                                do_sign_flag = 2
                            app_obj.new_bundle_name = app_obj.name
                        update_fields.append('new_bundle_name')
                if app_obj.type == 1 and data.get('issupersign', -1) != -1:
                    if data.get('issupersign', -1) == 1 and not check_super_sign_permission(request.user):
                        logger.error(f"app_id:{app_id} can't open super_sign,owner has no ios developer")
                        return ApiResponse(code=1008, msg="超级签余额不足，无法开启")
                    do_sign_flag = 3
                    app_obj.issupersign = data.get("issupersign", app_obj.issupersign)
                    update_fields.append("issupersign")
                if app_obj.issupersign and data.get('change_auto_sign', -1) != -1:
                    if data.get('change_auto_sign', -1) == 1:
                        do_sign_flag = 3
                    app_obj.change_auto_sign = data.get("change_auto_sign", app_obj.change_auto_sign)
                    update_fields.append("change_auto_sign")

                logger.info(f"app_id:{app_id} update new data:{app_obj.__dict__}")
                app_obj.save(update_fields=update_fields)
                if app_obj.issupersign:
                    c_task = None
                    if do_sign_flag == 1:
                        AppUDID.objects.filter(app_id=app_obj).update(sign_status=SignStatus.APP_REGISTRATION_COMPLETE)
                        if app_obj.change_auto_sign:
                            c_task = run_resign_task(app_obj.pk, True)

                    if do_sign_flag == 2:
                        sign_status = SignStatus.PROFILE_DOWNLOAD_COMPLETE
                        AppUDID.objects.filter(app_id=app_obj, sign_status__gte=sign_status).update(
                            sign_status=sign_status)
                        if app_obj.change_auto_sign:
                            flag = False
                            if AppUDID.objects.filter(app_id=app_obj, sign_status=SignStatus.APP_REGISTRATION_COMPLETE,
                                                      udid__developerid__status__in=Config.DEVELOPER_WRITE_STATUS).first():
                                flag = True
                            c_task = run_resign_task(app_obj.pk, flag)

                    if do_sign_flag == 3:
                        if app_obj.change_auto_sign:
                            flag = False
                            if AppUDID.objects.filter(app_id=app_obj, sign_status=SignStatus.APP_REGISTRATION_COMPLETE,
                                                      udid__developerid__status__in=Config.DEVELOPER_WRITE_STATUS).first():
                                flag = True
                            c_task = run_resign_task(app_obj.pk, flag, False)

                    if c_task:
                        logger.info(f"app {app_obj} run_resign_task msg:{c_task}")
                del_cache_response_by_short(app_obj.app_id)
            except Exception as e:
                logger.error(f"app_id:{app_id} update Exception:{e}")
                return ApiResponse(code=1005, msg="短连接已经存在")

        return ApiResponse()


class AppCanSignView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        if check_super_sign_permission(request.user):
            return ApiResponse(data={'sign': True})
        return ApiResponse(data={'sign': False})
