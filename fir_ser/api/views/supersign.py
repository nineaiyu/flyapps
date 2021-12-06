#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4
import datetime
import logging

from django.db.models import Count, Q, Sum
from django.http.response import FileResponse
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import AppIOSDeveloperInfo, APPSuperSignUsedInfo, AppUDID, IosDeveloperPublicPoolBill, \
    UDIDsyncDeveloper
from api.utils.app.supersignutils import IosUtils
from api.utils.auth import ExpiringTokenAuthentication, SuperSignPermission
from api.utils.modelutils import get_user_public_used_sign_num, get_user_public_sign_num
from api.utils.response import BaseResponse
from api.utils.serializer import DeveloperSerializer, SuperSignUsedSerializer, DeviceUDIDSerializer, BillInfoSerializer, \
    DeveloperDeviceSerializer
from api.utils.storage.caches import CleanSignDataState
from api.utils.utils import get_developer_devices, get_choices_dict

logger = logging.getLogger(__name__)


class PageNumber(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class DeveloperView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):

        res = BaseResponse()

        app_id = request.query_params.get("appid", None)
        developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user)
        res.use_num = get_developer_devices(developer_obj)
        if app_id:
            developer_obj = developer_obj.filter(issuer_id=app_id)

        page_obj = PageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=developer_obj.order_by("-updated_time"),
                                                         request=request,
                                                         view=self)
        developer_serializer = DeveloperSerializer(app_page_serializer, many=True, )

        res.data = developer_serializer.data
        res.count = developer_obj.count()

        res.apple_auth_list = get_choices_dict(AppIOSDeveloperInfo.auth_type_choices)
        return Response(res.dict)

    def put(self, request):
        data = request.data
        issuer_id = data.get("issuer_id", "").strip()
        if issuer_id:
            developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user, issuer_id=issuer_id).first()
        else:
            act = data.get("act", '').strip()
            if act == "syncalldevice":
                res = BaseResponse()
                result_list = []
                for developer_s_obj in AppIOSDeveloperInfo.objects.filter(user_id=request.user, is_actived=True).all():
                    status, result = IosUtils.get_device_from_developer(developer_s_obj)
                    if not status:
                        result_list.append(result.get("err_info"))
                if len(result_list):
                    logger.warning(result_list)
                return Response(res.dict)
            return self.get(request)

        if developer_obj:
            act = data.get("act", "").strip()
            if act:
                res = BaseResponse()
                logger.info(f"user {request.user} ios developer {developer_obj} act {act}")
                if act == "checkauth":
                    status, result = IosUtils.active_developer(developer_obj)
                    if status:
                        if not developer_obj.certid:
                            IosUtils.get_device_from_developer(developer_obj)
                        return self.get(request)
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
                            res.msg = result.get("err_info")
                            return Response(res.dict)
                elif act == "renewcert":
                    if developer_obj.certid:
                        # clean developer somethings. remove profile and  revoke cert
                        IosUtils.clean_developer(developer_obj, request.user)
                        status, result = IosUtils.revoke_developer_cert(developer_obj, request.user)
                        if status:
                            pass
                            # status, result = IosUtils.create_developer_cert(developer_obj, request.user)
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
                        res.msg = result.get("err_info")
                        return Response(res.dict)
                elif act == "cleandevice":
                    if CleanSignDataState.get_state(request.user.uid):
                        res.code = 1008
                        res.msg = "数据清理中,请耐心等待"
                        return Response(res.dict)
                    CleanSignDataState.set_state(request.user.uid, timeout=60 * 10)
                    status, result = IosUtils.clean_developer(developer_obj, request.user, False)
                    CleanSignDataState.del_state(request.user.uid)
                    if not status:
                        res.code = 1008
                        res.msg = result.get("err_info")
                        return Response(res.dict)
                elif act == 'disable':
                    developer_obj.is_actived = False
                    developer_obj.save(update_fields=['is_actived'])
                    return self.get(request)
            else:
                update_fields = []
                logger.info(f"user {request.user} ios developer {developer_obj} update input data {data}")
                logger.info(
                    f"user {request.user} ios developer {developer_obj} update old data {developer_obj.__dict__}")
                try:
                    usable_number = int(data.get("usable_number", developer_obj.usable_number))
                    if 0 <= usable_number <= 100:
                        developer_obj.usable_number = usable_number
                        update_fields.append("usable_number")
                except Exception as e:
                    logger.error(
                        f"developer {developer_obj} usable_number {data.get('usable_number', developer_obj.usable_number)} get failed Exception:{e}")
                developer_obj.description = data.get("description", developer_obj.description)
                update_fields.append("description")
                private_key_id = data.get("private_key_id", developer_obj.private_key_id)
                p8key = data.get("p8key", developer_obj.p8key)
                if private_key_id != "" and private_key_id != developer_obj.private_key_id:
                    developer_obj.private_key_id = private_key_id
                    developer_obj.is_actived = False
                    update_fields.append("private_key_id")
                if p8key != "" and p8key != developer_obj.p8key:
                    developer_obj.p8key = p8key
                    developer_obj.is_actived = False
                    update_fields.append("p8key")
                try:
                    update_fields.append("is_actived")
                    developer_obj.save(update_fields=update_fields)
                    logger.info(
                        f"user {request.user} ios developer {developer_obj} update now data {developer_obj.__dict__}")
                except Exception as e:
                    logger.error(
                        f"user {request.user} ios developer {developer_obj} update error data {data} Exception {e}")

        return self.get(request)

    def post(self, request):
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
        except Exception as e:
            logger.error(f"user {request.user} create developer {data_info} failed Exception:{e}")
            res = BaseResponse()
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

        if developer_obj:
            logger.error(f"user {request.user} delete developer {developer_obj}")
            if developer_obj.certid:
                IosUtils.clean_developer(developer_obj, request.user)
                IosUtils.revoke_developer_cert(developer_obj, request.user)
            developer_obj.delete()

        return self.get(request)


def base_super_sign_used_info(request):
    udid = request.query_params.get("udid", None)
    bundle_id = request.query_params.get("bundleid", None)
    developer_id = request.query_params.get("appid", None)
    mine = True
    super_sign_used_objs = APPSuperSignUsedInfo.objects.filter(developerid__user_id=request.user, )
    if not super_sign_used_objs:
        super_sign_used_objs = APPSuperSignUsedInfo.objects.filter(user_id=request.user, )
        mine = False
    if developer_id:
        super_sign_used_objs = super_sign_used_objs.filter(developerid__issuer_id=developer_id)
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
        app_id = request.query_params.get("aid", None)
        app_udid_obj = AppUDID.objects.filter(pk=pk)
        if app_udid_obj:
            super_sign_used_obj = APPSuperSignUsedInfo.objects.filter(udid=app_udid_obj.first()).first()
            if super_sign_used_obj and super_sign_used_obj.developerid.user_id.pk == request.user.pk:
                logger.error(f"user {request.user} delete devices {app_udid_obj}")
                IosUtils.disable_udid(app_udid_obj.first(), app_id)
                app_udid_obj.delete()
            else:
                res.code = 10002
                res.msg = '公共账号池不允许删除'
        return Response(res.dict)


class DeveloperDeviceView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()

        udid = request.query_params.get("udid", None)
        developer_id = request.query_params.get("appid", None)
        super_sign_used_objs = UDIDsyncDeveloper.objects.filter(developerid__user_id=request.user, )
        if developer_id:
            super_sign_used_objs = super_sign_used_objs.filter(developerid__issuer_id=developer_id)
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

    def delete(self, request):
        res = BaseResponse()
        pk = request.query_params.get("id", None)
        app_id = request.query_params.get("aid", None)
        app_udid_obj = AppUDID.objects.filter(pk=pk)
        if app_udid_obj:
            super_sign_used_obj = APPSuperSignUsedInfo.objects.filter(udid=app_udid_obj.first()).first()
            if super_sign_used_obj and super_sign_used_obj.developerid.user_id.pk == request.user.pk:
                logger.error(f"user {request.user} delete devices {app_udid_obj}")
                IosUtils.disable_udid(app_udid_obj.first(), app_id)
                app_udid_obj.delete()
            else:
                res.code = 10002
                res.msg = '公共账号池不允许删除'
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
        user_used_list = IosDeveloperPublicPoolBill.objects.filter(
            Q(to_user_id=request.user) | Q(user_id=request.user))
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


class DeviceUsedRankInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [SuperSignPermission, ]

    def get(self, request):
        res = BaseResponse()
        page_obj = PageNumber()
        appnamesearch = request.query_params.get("appnamesearch")
        start_time = request.query_params.get("start_time")
        end_time = request.query_params.get("end_time")
        app_used_sign_objs = APPSuperSignUsedInfo.objects.filter(user_id=request.user)
        if appnamesearch:
            app_used_sign_objs = app_used_sign_objs.filter(
                Q(app_id__name=appnamesearch) | Q(app_id__bundle_id=appnamesearch))
        if end_time and start_time:
            try:
                start_time = datetime.date.fromtimestamp(int(start_time) / 1000)
                end_time = datetime.date.fromtimestamp(int(end_time) / 1000 + 24 * 60 * 60 - 1)
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
