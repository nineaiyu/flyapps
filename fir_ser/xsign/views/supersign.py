#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4
import datetime
import json
import logging

from django.db.models import Count, Q, Sum
from django.http.response import FileResponse
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Apps, UserInfo
from api.utils.modelutils import PageNumber
from api.utils.response import BaseResponse
from common.base.baseutils import get_choices_dict, get_choices_name_from_key, AppleDeveloperUid, get_real_ip_address
from common.cache.state import CleanSignDataState, MigrateStorageState
from common.core.auth import ExpiringTokenAuthentication, SuperSignPermission
from common.core.sysconfig import Config
from common.utils.download import get_app_download_url
from xsign.models import AppIOSDeveloperInfo, APPSuperSignUsedInfo, AppUDID, IosDeveloperPublicPoolBill, \
    UDIDsyncDeveloper, AppleDeveloperToAppUse, DeveloperAppID, APPToDeveloper, DeveloperDevicesID, \
    IosDeveloperBill
from xsign.tasks import run_resign_task_do
from xsign.utils.modelutils import get_user_public_used_sign_num, get_user_public_sign_num, check_uid_has_relevant, \
    get_developer_devices
from xsign.utils.serializer import DeveloperSerializer, SuperSignUsedSerializer, DeviceUDIDSerializer, \
    BillInfoSerializer, \
    DeveloperDeviceSerializer, AppleDeveloperToAppUseSerializer, AppleDeveloperToAppUseAppsSerializer, \
    BillTransferSerializer
from xsign.utils.supersignutils import IosUtils

logger = logging.getLogger(__name__)


def delete_developer_and_clean(developer_obj, user_obj):
    if developer_obj and user_obj:
        logger.error(f"user {user_obj} delete developer {developer_obj}")
        if developer_obj.certid:
            IosUtils.clean_developer(developer_obj, user_obj)
            IosUtils.revoke_developer_cert(developer_obj, user_obj)
        developer_obj.delete()


class DeveloperView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()
        issuer_id = request.query_params.get("issuer_id", '')
        developer_choice = request.query_params.get("developer_choice", None)
        developer_status_choice = request.query_params.get("developer_status_choice", None)
        developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user)
        if developer_choice and developer_choice in ['private', 'public']:
            if developer_choice == 'public':
                developer_obj = developer_obj.exclude(appledevelopertoappuse__developerid__isnull=False)
            else:
                developer_obj = developer_obj.filter(appledevelopertoappuse__developerid__isnull=False)
        try:
            status_choice = json.loads(developer_status_choice)
        except Exception as e:
            status_choice = None
        if status_choice is not None and isinstance(status_choice, list) and status_choice:
            developer_obj = developer_obj.filter(status__in=status_choice)
        developer_obj = developer_obj.distinct()
        res.use_num = get_developer_devices(developer_obj)
        if issuer_id:
            developer_obj = developer_obj.filter(
                Q(developerappid__app_id__bundle_id=issuer_id, developerappid__app_id__user_id=request.user) | Q(
                    issuer_id=issuer_id) | Q(description__contains=issuer_id))

        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=developer_obj.order_by("-updated_time"),
                                                         request=request,
                                                         view=self)
        developer_serializer = DeveloperSerializer(app_page_serializer, many=True)

        res.data = developer_serializer.data
        res.count = developer_obj.count()
        res.status_choices = get_choices_dict(AppIOSDeveloperInfo.status_choices, Config.DEVELOPER_DISABLED_STATUS)
        res.apple_auth_list = get_choices_dict(AppIOSDeveloperInfo.auth_type_choices)
        return Response(res.dict)

    def put(self, request):
        data = request.data
        res = BaseResponse()
        issuer_id = data.get("issuer_id", "").strip()
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
        else:
            act = data.get("act", '').strip()
            if act == "syncalldevice":
                res = BaseResponse()
                result_list = []
                for developer_s_obj in AppIOSDeveloperInfo.objects.filter(user_id=request.user,
                                                                          status__in=Config.DEVELOPER_USE_STATUS).all():
                    status, result = IosUtils.get_device_from_developer(developer_s_obj)
                    if not status:
                        result_list.append(result.get("err_info"))
                if len(result_list):
                    logger.warning(result_list)
                return Response(res.dict)
            elif act == "checkauth":
                issuer_ids = data.get("issuer_ids", [])
                if issuer_ids:
                    for developer_s_obj in AppIOSDeveloperInfo.objects.filter(user_id=request.user,
                                                                              issuer_id__in=issuer_ids).all():
                        status, result = IosUtils.active_developer(developer_s_obj, False)
                        if status:
                            IosUtils.get_device_from_developer(developer_s_obj)
            elif act == "setstatus":
                issuer_ids = data.get("issuer_ids", [])
                status = data.get("status", None)
                if issuer_ids and status is not None and status not in Config.DEVELOPER_DISABLED_STATUS:
                    status_text = get_choices_name_from_key(AppIOSDeveloperInfo.status_choices, status)
                    if status_text:
                        AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id__in=issuer_ids).update(
                            status=status)

            return Response(res.dict)

        if developer_obj:
            act = data.get("act", "").strip()
            if act:
                logger.info(f"user {request.user} ios developer {developer_obj} act {act}")
                if act == "checkauth":
                    status, result = IosUtils.active_developer(developer_obj, False)
                    if status:
                        IosUtils.get_device_from_developer(developer_obj)
                        return Response(res.dict)
                    else:
                        res.code = 1008
                        res.msg = result.get("return_info", "未知错误")
                        return Response(res.dict)

                elif act == "ioscert":
                    if not developer_obj.certid:
                        status, result = IosUtils.create_developer_cert(developer_obj, request.user)
                        if status:
                            IosUtils.get_device_from_developer(developer_obj)
                        else:
                            res.code = 1008
                            res.msg = result.get("return_info")
                            return Response(res.dict)
                elif act in ["renewcert", "cleancert"]:
                    if developer_obj.certid:
                        # clean developer somethings. remove profile and  revoke cert
                        if act == 'cleancert':
                            IosUtils.clean_developer(developer_obj, request.user)
                        status, result = IosUtils.revoke_developer_cert(developer_obj, request.user)
                        if status:
                            if act == 'renewcert':
                                AppUDID.objects.filter(udid__developerid=developer_obj).update(
                                    sign_status=2)

                                status, result = IosUtils.create_developer_cert(developer_obj, request.user)
                            # if status:
                            #     IosUtils.get_device_from_developer(developer_obj, request.user)
                            # else:
                            #     res.code = 1008
                            #     res.msg = result.get("err_info")
                            #     return Response(res.dict)
                        else:
                            res.code = 1008
                            res.msg = result.get("err_info", '')
                            return Response(res.dict)
                elif act in ["syncdevice", "syncalldevice"]:
                    status, result = IosUtils.get_device_from_developer(developer_obj)
                    if not status:
                        res.code = 1008
                        res.msg = result.get("return_info")
                        return Response(res.dict)
                elif act == "cleandevice":
                    with CleanSignDataState(request.user.uid) as state:
                        if state:
                            status, result = IosUtils.clean_developer(developer_obj, request.user, False)
                            if not status:
                                res.code = 1008
                                res.msg = result.get("err_info")
                        else:
                            res.code = 1008
                            res.msg = "数据清理中,请耐心等待"
                    return Response(res.dict)
                elif act == 'disable':
                    developer_obj.status = 0
                    developer_obj.save(update_fields=['status'])
                    return Response(res.dict)
            else:
                update_fields = []
                logger.info(f"user {request.user} ios developer {developer_obj} update input data {data}")
                logger.info(
                    f"user {request.user} ios developer {developer_obj} update old data {developer_obj.__dict__}")
                try:
                    usable_number = int(data.get("usable_number", developer_obj.usable_number))
                    app_limit_number = int(data.get("app_limit_number", developer_obj.app_limit_number))
                    if 0 <= usable_number <= 100:
                        developer_obj.usable_number = usable_number
                        update_fields.append("usable_number")
                    if 0 <= app_limit_number <= 160:
                        developer_obj.app_limit_number = app_limit_number
                        update_fields.append("app_limit_number")
                except Exception as e:
                    logger.error(
                        f"developer {developer_obj} usable_number {data.get('usable_number', developer_obj.usable_number)} get failed Exception:{e}")

                developer_obj.description = data.get("description", developer_obj.description)
                update_fields.append("description")

                developer_obj.clean_status = data.get("clean_status", developer_obj.clean_status)
                update_fields.append("clean_status")
                developer_obj.auto_check = data.get("auto_check", developer_obj.auto_check)
                update_fields.append("auto_check")

                private_key_id = data.get("private_key_id", developer_obj.private_key_id)
                p8key = data.get("p8key", developer_obj.p8key)
                if private_key_id != "" and private_key_id != developer_obj.private_key_id:
                    developer_obj.private_key_id = private_key_id
                    developer_obj.status = 0
                    update_fields.append("private_key_id")
                if p8key != "" and p8key != developer_obj.p8key:
                    developer_obj.p8key = p8key
                    developer_obj.status = 0
                    update_fields.append("p8key")

                read_only_mode = data.get("read_only_mode", '')
                if developer_obj.status == 1 and read_only_mode == 'on':
                    developer_obj.status = 3
                    update_fields.append("status")

                try:
                    # update_fields.append("status")
                    developer_obj.save(update_fields=update_fields)
                    logger.info(
                        f"user {request.user} ios developer {developer_obj} update now data {developer_obj.__dict__}")
                except Exception as e:
                    logger.error(
                        f"user {request.user} ios developer {developer_obj} update error data {data} Exception {e}")

        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        data_info = {}
        if data.get("auth_type") == 0:
            data_info = {
                "usable_number": data.get("usable_number", ""),
                "description": data.get("description", ""),
                "issuer_id": data.get("issuer_id", ""),
                "private_key_id": data.get("private_key_id", ""),
                "p8key": data.get("p8key", ""),
                "auth_type": 0
            }
        try:
            logger.error(f"user {request.user} add new developer {data.get('issuer_id', '')} data {data_info}")
            developer_obj = AppIOSDeveloperInfo.objects.create(user_id=request.user, **data_info)
            IosUtils.create_developer_space(developer_obj, request.user)
            status, result = IosUtils.active_developer(developer_obj, False)
            if not status:
                res.code = 1008
                res.msg = result.get("return_info", "未知错误")
                delete_developer_and_clean(developer_obj, request.user)
                return Response(res.dict)
            else:
                IosUtils.get_device_from_developer(developer_obj)

        except Exception as e:
            logger.error(f"user {request.user} create developer {data_info} failed Exception:{e}")
            res.code = 1005
            res.msg = "添加失败"
            return Response(res.dict)

        return self.get(request)

    def delete(self, request):
        issuer_id = request.query_params.get("issuer_id", None)
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
        else:
            return self.get(request)
        delete_developer_and_clean(developer_obj, request.user)
        return self.get(request)


def base_super_sign_used_info(request):
    udid = request.query_params.get("udid", None)
    bundle_id = request.query_params.get("bundleid", None)
    issuer_id = request.query_params.get("issuer_id", None)
    mine = True
    super_sign_used_objs = APPSuperSignUsedInfo.objects.filter(developerid__user_id=request.user, )
    if not super_sign_used_objs:
        super_sign_used_objs = APPSuperSignUsedInfo.objects.filter(user_id=request.user, )
        mine = False
    if issuer_id:
        super_sign_used_objs = super_sign_used_objs.filter(developerid__issuer_id=issuer_id)
    if udid:
        super_sign_used_objs = super_sign_used_objs.filter(udid__udid__udid=udid)
    if bundle_id:
        super_sign_used_objs = super_sign_used_objs.filter(app_id__bundle_id=bundle_id)
    return super_sign_used_objs, mine


class SuperSignUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()
        super_sign_used_objs, mine = base_super_sign_used_info(request)
        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=super_sign_used_objs.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
        app_serializer = SuperSignUsedSerializer(app_page_serializer, many=True,
                                                 context={'mine': mine, 'user_obj': request.user})
        res.data = app_serializer.data
        res.count = super_sign_used_objs.count()
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        device_udid = data.get('device_udid', '')
        developer_id = data.get('developer_id', '')
        bundle_id = data.get('bundle_id', '')
        other_uid_info = data.get('other_uid', '')
        if device_udid and developer_id and bundle_id:
            app_obj = Apps.objects.filter(user_id=request.user, bundle_id=bundle_id).first()
            if app_obj is None and not developer_id.startswith(Config.DEVELOPER_UID_KEY):
                if other_uid_info:
                    other_uid = other_uid_info.get('uid')
                    if other_uid and check_uid_has_relevant(request.user.uid, other_uid):
                        app_obj = Apps.objects.filter(bundle_id=bundle_id).first()
            if developer_id.startswith(Config.DEVELOPER_UID_KEY):
                developer_id = AppleDeveloperUid().get_decrypt_uid(developer_id.lstrip('T:'))

            app_to_dev_obj = APPToDeveloper.objects.filter(app_id=app_obj, developerid__issuer_id=developer_id).first()
            if app_obj and app_to_dev_obj:
                developer_app_id_obj = DeveloperAppID.objects.filter(app_id=app_obj,
                                                                     developerid__issuer_id=developer_id).first()
                appudid_obj = AppUDID.objects.filter(app_id=app_obj, udid__udid=device_udid,
                                                     udid__developerid__issuer_id=developer_id).last()
                need_download_profile = True
                if appudid_obj.sign_status in [3, 4]:
                    need_download_profile = False
                c_task = run_resign_task_do.apply_async((app_obj.pk, app_to_dev_obj.developerid.pk,
                                                         developer_app_id_obj.aid, need_download_profile, False))
                msg = c_task.get(propagate=False)
                logger.info(f"app {app_obj} run_resign_task msg:{msg}")
                if c_task.successful():
                    c_task.forget()
                app_to_dev_obj = APPToDeveloper.objects.filter(app_id=app_obj,
                                                               developerid__issuer_id=developer_id).first()

                res = get_app_download_url(request, res, app_obj.app_id, app_obj.short, app_obj.password,
                                           app_to_dev_obj.binary_file, True, device_udid)

        return Response(res.dict)


class AppUDIDUsedView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()
        super_sign_used_objs, mine = base_super_sign_used_info(request)
        page_obj = PageNumber()
        app_udid_objs = AppUDID.objects.filter(appsupersignusedinfo__in=super_sign_used_objs)
        app_page_serializer = page_obj.paginate_queryset(queryset=app_udid_objs.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
        app_serializer = DeviceUDIDSerializer(app_page_serializer, many=True,
                                              context={'mine': mine, 'user_obj': request.user})
        res.data = app_serializer.data
        res.count = app_udid_objs.count()
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        pk = request.query_params.get("id", None)
        other_uid = request.query_params.get("uid", None)
        app_id = request.query_params.get("aid", None)
        disabled = request.query_params.get("disabled", None)
        if disabled is not None and disabled == '1':
            disabled = True
        else:
            disabled = False
        app_udid_obj = AppUDID.objects.filter(pk=pk, app_id__user_id=request.user)
        if not app_udid_obj and check_uid_has_relevant(request.user.uid, other_uid):
            app_udid_obj = AppUDID.objects.filter(pk=pk, app_id__user_id__uid=other_uid)
        if app_udid_obj:
            super_sign_used_obj = APPSuperSignUsedInfo.objects.filter(udid=app_udid_obj.first()).first()
            if super_sign_used_obj:
                if super_sign_used_obj.developerid.user_id.pk == request.user.pk:
                    logger.error(f"user {request.user} delete devices {app_udid_obj}")
                    IosUtils.disable_udid(app_udid_obj.first(), app_id, disabled)
                else:
                    IosUtils.disable_udid(app_udid_obj.first(), app_id)
                    # res.code = 10002
                    # res.msg = '公共账号池不允许禁用删除'
                app_udid_obj.delete()
            else:
                res.code = 10003
                res.msg = '数据异常，删除失败'
        return Response(res.dict)


class DeveloperDeviceView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()

        udid = request.query_params.get("udid", None)
        issuer_id = request.query_params.get("issuer_id", None)
        super_sign_used_objs = UDIDsyncDeveloper.objects.filter(developerid__user_id=request.user, )
        if issuer_id:
            super_sign_used_objs = super_sign_used_objs.filter(developerid__issuer_id=issuer_id)
        if udid:
            super_sign_used_objs = super_sign_used_objs.filter(udid=udid)
        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=super_sign_used_objs.order_by('-id'),
                                                         request=request,
                                                         view=self)
        app_serializer = DeveloperDeviceSerializer(app_page_serializer, many=True)
        res.data = app_serializer.data
        res.count = super_sign_used_objs.count()
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        developer_id = request.data.get("developer_id", None)
        udid = request.data.get("udid", None)
        disabled = request.data.get("disabled", None)
        if developer_id and udid and disabled is not None and disabled in [0, 1]:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=developer_id).first()
            udid_sync_obj_queryset = UDIDsyncDeveloper.objects.filter(udid=udid, developerid=developer_obj).all()

            if disabled == 1:
                for udid_sync_obj in udid_sync_obj_queryset:
                    IosUtils.do_enable_device_by_sync(developer_obj, udid_sync_obj)
            else:
                app_udid_obj_list = AppUDID.objects.filter(udid__udid=udid, app_id__user_id=request.user,
                                                           udid__developerid=developer_obj).all()
                for app_udid_obj in app_udid_obj_list:
                    for app_id_info in DeveloperDevicesID.objects.filter(udid=app_udid_obj.udid,
                                                                         developerid=developer_obj).values(
                        'app_id').all().distinct():
                        logger.error(f"user {request.user} delete devices {app_udid_obj}")
                        IosUtils.disable_udid(app_udid_obj, app_id_info.get('app_id'), True)
                        AppUDID.objects.filter(pk=app_udid_obj.pk).delete()

                for udid_sync_obj in udid_sync_obj_queryset:
                    IosUtils.do_disable_device_by_sync(developer_obj, udid_sync_obj)
        return Response(res.dict)


class SuperSignCertView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        issuer_id = request.query_params.get('issuer_id', None)
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
            resign_app_obj = IosUtils.get_resign_obj(request.user, developer_obj)
            if not resign_app_obj.check_p12_exists():
                resign_app_obj.make_p12_from_cert(developer_obj.certid)
            if developer_obj:
                zip_file_path = IosUtils.zip_cert(request.user, developer_obj)
                response = FileResponse(open(zip_file_path, 'rb'))
                response['Content-Type'] = "application/octet-stream"
                response["Access-Control-Expose-Headers"] = "Content-Disposition"
                response['Content-Disposition'] = 'attachment; filename=' + developer_obj.certid + '.zip'
                return response
        res = BaseResponse()
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        issuer_id = request.data.get('issuer_id', None)
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
            if developer_obj:
                resign_app_obj = IosUtils.get_resign_obj(request.user, developer_obj)
                status, result = resign_app_obj.make_cert_from_p12(request.data.get('cert_pwd', ''),
                                                                   request.data.get('cert_content', None))
                if status:
                    status, result = IosUtils.auto_get_cert_id_by_p12(developer_obj, request.user)
                    if status:
                        resign_app_obj.write_cert()
                    else:
                        res.code = 1003
                        res.msg = '证书未在开发者账户找到，请检查推送证书是否属于该开发者'
                else:
                    res.code = 1002
                    res.msg = str(result['err_info'])
                    return Response(res.dict)
        return Response(res.dict)


class DeviceUsedBillView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()
        udid = request.query_params.get("udid", None)
        act = request.query_params.get("act", None)

        receive_user_id_list = IosDeveloperBill.objects.filter(user_id=request.user, to_user_id__isnull=False,
                                                               status=2).values(
            'to_user_id').distinct()
        user_used_list = IosDeveloperPublicPoolBill.objects.filter(
            Q(user_id=request.user) | Q(user_id_id__in=receive_user_id_list))
        page_obj = PageNumber()
        if udid:
            user_used_list = user_used_list.filter(udid=udid)
        else:
            user_used_list = user_used_list.filter(udid__isnull=False)
        if act and act == 'info':
            app_page_serializer = page_obj.paginate_queryset(queryset=user_used_list.order_by("-created_time"),
                                                             request=request,
                                                             view=self)
            app_serializer = BillInfoSerializer(app_page_serializer, many=True, context={'user_obj': request.user})
            res.data = app_serializer.data
            res.count = user_used_list.count()

        else:

            if udid:
                user_used_list = user_used_list.filter(udid=udid)
            user_used_list3 = user_used_list.values('udid', 'product', 'version', 'udid_sync_info_id').annotate(
                counts=Count('udid'))
            res.count = user_used_list3.count()
            user_used_list3 = page_obj.paginate_queryset(queryset=user_used_list3.order_by('-udid_sync_info_id'),
                                                         request=request, view=self)
            for user_used in user_used_list3:
                user_used['counts'] = user_used_list.filter(udid=user_used.get('udid')).count()
            res.data = user_used_list3
            res.balance_info = {
                'used_balance': get_user_public_used_sign_num(request.user),
                'all_balance': get_user_public_sign_num(request.user)
            }
        return Response(res.dict)


class DeviceTransferBillView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()
        uidsearch = request.query_params.get("uidsearch", None)

        user_used_list = IosDeveloperBill.objects.filter(
            Q(user_id=request.user) | Q(to_user_id=request.user)).distinct()
        page_obj = PageNumber()
        if uidsearch:
            user_used_list = user_used_list.filter(Q(user_id__uid=uidsearch) | Q(to_user_id__uid=uidsearch))

        app_page_serializer = page_obj.paginate_queryset(queryset=user_used_list.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
        app_serializer = BillTransferSerializer(app_page_serializer, many=True, context={'user_obj': request.user})
        res.data = app_serializer.data
        res.count = user_used_list.count()

        res.balance_info = {
            'used_balance': get_user_public_used_sign_num(request.user),
            'all_balance': get_user_public_sign_num(request.user)
        }
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        uid = request.data.get('uid')
        number = request.data.get('number')
        if uid and number:
            to_user_obj = UserInfo.objects.filter(uid=uid, is_active=True, supersign_active=True).first()
            if to_user_obj:
                if isinstance(number, int) and 0 < number < 99999:
                    user_obj = request.user
                    if user_obj.pk != to_user_obj.pk:
                        try:
                            use_num = get_developer_devices(AppIOSDeveloperInfo.objects.filter(user_id=user_obj))
                            all_balance = use_num.get('max_total', 0)
                            if all_balance > 0 and number <= all_balance:
                                bill_obj = IosDeveloperBill.objects.filter(user_id=user_obj, to_user_id=to_user_obj,
                                                                           status=2).first()
                                if bill_obj:
                                    bill_obj.number = number + bill_obj.number
                                    if bill_obj.number >= all_balance:
                                        bill_obj.number = all_balance
                                    bill_obj.remote_addr = get_real_ip_address(request)
                                    bill_obj.description = f'{user_obj.first_name} 共享给 {to_user_obj.first_name} {bill_obj.number} 设备数'
                                    bill_obj.save(update_fields=['number', 'remote_addr', 'description'])
                                else:
                                    IosDeveloperBill.objects.create(user_id=user_obj, to_user_id=to_user_obj,
                                                                    status=2, number=number,
                                                                    remote_addr=get_real_ip_address(request),
                                                                    description=f'{user_obj.first_name} 共享给 {to_user_obj.first_name} {number} 设备数')
                                return Response(res.dict)
                            else:
                                res.msg = f'设备余额不足,当前设备余额最大为 {all_balance}'
                        except Exception as e:
                            res.msg = str(e)
                    else:
                        res.msg = '用户不合法'
                else:
                    res.msg = '划转数量异常'
            else:
                res.msg = '用户信息不存在'
        else:
            res.msg = '参数有误'
        res.code = 1003
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        uid = request.data.get("uid", None)
        status = request.data.get("status", None)
        number = request.data.get("number", None)

        if uid and status and number:
            if check_uid_has_relevant(uid, request.user.uid):
                if MigrateStorageState(uid).get_state():
                    res.code = 1008
                    res.msg = "数据迁移中，无法处理该操作"
                    return Response(res.dict)
                bill_obj = IosDeveloperBill.objects.filter(user_id__uid=uid, to_user_id=request.user, status=status,
                                                           number=abs(int(number))).first()
                if bill_obj:
                    for app_obj in Apps.objects.filter(user_id=request.user, type=1):
                        count = APPToDeveloper.objects.filter(app_id=app_obj).count()
                        if app_obj.issupersign or count > 0:
                            logger.info(f"app_id:{app_obj} is super_sign ,clean IOS developer")
                            IosUtils.clean_app_by_user_obj(app_obj)
                    return Response(res.dict)

        res.code = 1003
        res.msg = '转移记录不存在'
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        uid = request.query_params.get("uid", None)
        status = request.query_params.get("status", None)
        number = request.query_params.get("number", None)
        if MigrateStorageState(request.user.uid).get_state():
            res.code = 1008
            res.msg = "数据迁移中，无法处理该操作"
            return Response(res.dict)
        if uid and status and number:
            bill_obj = IosDeveloperBill.objects.filter(user_id=request.user, to_user_id__uid=uid, status=status,
                                                       number=abs(int(number))).first()
            if bill_obj:
                target_user_obj = UserInfo.objects.filter(uid=uid).first()
                if target_user_obj:
                    for app_obj in Apps.objects.filter(user_id=target_user_obj, type=1):
                        app_obj.issupersign = False
                        app_obj.save(update_fields=['issupersign'])
                        count = APPToDeveloper.objects.filter(app_id=app_obj).count()
                        if app_obj.issupersign or count > 0:
                            logger.info(f"app_id:{app_obj} is super_sign ,clean IOS developer")
                            IosUtils.clean_app_by_user_obj(app_obj)
                bill_obj.status = 1
                bill_obj.save(update_fields=['status'])
            else:
                res.code = 1003
                res.msg = '转移记录不存在'
        return Response(res.dict)


class DeviceUsedRankInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()
        page_obj = PageNumber()
        search_key = request.query_params.get("appnamesearch")
        start_time = request.query_params.get("start_time")
        end_time = request.query_params.get("end_time")
        receive_user_id_list = IosDeveloperBill.objects.filter(user_id=request.user, to_user_id__isnull=False,
                                                               status=2).values(
            'to_user_id').distinct()
        app_used_sign_objs = APPSuperSignUsedInfo.objects.filter(
            Q(user_id=request.user) | Q(user_id_id__in=receive_user_id_list))
        if search_key:
            app_used_sign_objs = app_used_sign_objs.filter(
                Q(app_id__name=search_key) | Q(app_id__bundle_id=search_key) | Q(
                    developerid__issuer_id=search_key))
        if end_time and start_time:
            try:
                start_time = datetime.date.fromtimestamp(int(start_time) / 1000)
                end_time = datetime.date.fromtimestamp(int(end_time) / 1000) + datetime.timedelta(days=1)
                app_used_sign_objs = app_used_sign_objs.filter(created_time__range=[start_time, end_time])
            except Exception as e:
                logger.error(f"get time range failed {e}")

        app_used_sign_objs = app_used_sign_objs.values('app_id__app_id', 'app_id__name', 'app_id__bundle_id').annotate(
            count=Count('app_id__app_id')).order_by('-count')
        res.count = app_used_sign_objs.count()
        res.number = app_used_sign_objs.aggregate(Sum('count')).get('count__sum')

        app_used_sign_infos = page_obj.paginate_queryset(queryset=app_used_sign_objs,
                                                         request=request, view=self)
        new_app_used_sign_infos = []
        for app_used_info in app_used_sign_infos:
            new_app_used_info = {}
            for key, value in app_used_info.items():
                new_key = key.replace('app_id__', '')
                new_app_used_info[new_key] = value
            new_app_used_sign_infos.append(new_app_used_info)
        res.data = new_app_used_sign_infos
        return Response(res.dict)


class AppleDeveloperBindAppsView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()
        act = request.query_params.get("act", '')
        issuer_id = request.query_params.get("issuer_id", '')
        app_id = request.query_params.get("app_id", '')
        if act == 'apps':
            res.app_limit_number = 0
            apps_obj_list = Apps.objects.filter(user_id=request.user, type=1).all()
            app_serializer = AppleDeveloperToAppUseAppsSerializer(apps_obj_list, many=True,
                                                                  context={'issuer_id': issuer_id})
            if issuer_id:
                developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
                if developer_obj:
                    res.app_limit_number = developer_obj.app_limit_number
        elif act == 'developer':
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user).all()
            app_serializer = DeveloperSerializer(developer_obj, many=True, context={'app_id': app_id})
        else:
            apple_to_app_obj = AppleDeveloperToAppUse.objects.filter(app_id__user_id=request.user)
            if issuer_id:
                apple_to_app_obj = apple_to_app_obj.filter(developerid__issuer_id=issuer_id)
            if app_id:
                apple_to_app_obj = apple_to_app_obj.filter(app_id__app_id=app_id)

            app_serializer = AppleDeveloperToAppUseSerializer(apple_to_app_obj.all(), many=True)
        res.data = app_serializer.data
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        issuer_id = request.data.get('issuer_id', '')
        app_id = request.data.get('app_id', '')
        choices_data = request.data.get('choices_data', [])
        logger.info(f"change apple to app data:{request.data}")
        many_obj = []
        if app_id:
            app_obj = Apps.objects.filter(app_id=app_id, type=1, user_id=request.user).first()

            issuer_id_list = [apple_to_app['developerid__issuer_id'] for apple_to_app in
                              AppleDeveloperToAppUse.objects.filter(app_id=app_obj).values(
                                  'developerid__issuer_id').all().distinct()]

            add_issuer_ids = list(set(choices_data) - set(issuer_id_list))
            remove_issuer_ids = list(set(issuer_id_list) - set(choices_data))

            for item in add_issuer_ids:
                developer_obj = AppIOSDeveloperInfo.objects.filter(issuer_id=item, user_id=request.user,
                                                                   status__in=Config.DEVELOPER_USE_STATUS,
                                                                   certid__isnull=False).first()
                developer_aid_obj = DeveloperAppID.objects.filter(developerid=developer_obj)
                is_exist = developer_aid_obj.filter(app_id=app_obj).count()
                if developer_obj:
                    app_flag = False
                    if is_exist:
                        app_flag = True
                    else:
                        if developer_aid_obj.count() < developer_obj.app_limit_number:
                            app_flag = True
                    if app_flag:
                        many_obj.append(AppleDeveloperToAppUse(developerid=developer_obj, app_id=app_obj))
            AppleDeveloperToAppUse.objects.filter(developerid__issuer_id__in=remove_issuer_ids, app_id=app_obj).delete()

        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(issuer_id=issuer_id, user_id=request.user).first()
            app_id_list = [apple_to_app['app_id__app_id'] for apple_to_app in
                           AppleDeveloperToAppUse.objects.filter(developerid=developer_obj).values(
                               'app_id__app_id').all().distinct()]

            add_app_ids = list(set(choices_data) - set(app_id_list))
            remove_app_ids = list(set(app_id_list) - set(choices_data))

            exist_app_id_queryset = DeveloperAppID.objects.filter(developerid=developer_obj).values(
                'app_id__app_id').all()
            exist_app_ids = [exist_app_id_obj.get('app_id__app_id') for exist_app_id_obj in exist_app_id_queryset]
            can_add_number = developer_obj.app_limit_number - len(exist_app_ids)
            for item in add_app_ids:
                app_obj = Apps.objects.filter(app_id=item, type=1, user_id=request.user).first()
                if app_obj:
                    app_flag = False
                    if item in exist_app_ids:
                        app_flag = True
                    else:
                        if can_add_number > 0:
                            can_add_number -= 1
                            app_flag = True
                    if app_flag:
                        many_obj.append(AppleDeveloperToAppUse(developerid=developer_obj, app_id=app_obj))

            AppleDeveloperToAppUse.objects.filter(developerid=developer_obj, app_id__app_id__in=remove_app_ids,
                                                  app_id__user_id=request.user).delete()

        if many_obj:
            AppleDeveloperToAppUse.objects.bulk_create(many_obj)
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        issuer_id = request.data.get('issuer_id', '')
        app_id = request.data.get('app_id', '')
        infos = request.data.get('infos', {})
        logger.info(f"change apple to app data:{request.data}")
        if issuer_id and not app_id:
            app_id = infos.get('app_id', '')
        if app_id and not issuer_id:
            issuer_id = infos.get('issuer_id', '')
        if app_id and issuer_id:
            try:
                app_usable_number = int(infos.get('app_usable_number', 100))
                if 0 < app_usable_number < 101:
                    AppleDeveloperToAppUse.objects.filter(developerid__issuer_id=issuer_id,
                                                          app_id__app_id=app_id, app_id__user_id=request.user).update(
                        usable_number=int(app_usable_number))

            except Exception as e:
                logger.error(f'update app developer used failed infos:{infos} Exception:{e}')
        return Response(res.dict)
