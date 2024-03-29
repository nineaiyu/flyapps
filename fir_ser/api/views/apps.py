#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4
import copy
import logging

from django.db.models import Sum, F, Q
from django.db.models.functions import Length
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from api.base_views import app_delete
from api.models import Apps, AppReleaseInfo, UserInfo, AppScreenShot, AppDownloadToken
from api.utils.apputils import bytes2human
from api.utils.modelutils import get_user_domain_name, get_app_domain_name, get_app_storage_used
from api.utils.response import BaseResponse
from api.utils.serializer import AppsSerializer, AppReleaseSerializer, AppsListSerializer, AppsQrListSerializer, \
    AppDownloadTokenSerializer
from api.utils.signalutils import run_delete_app_signal
from api.utils.utils import delete_local_files, delete_app_screenshots_files
from common.base.magic import MagicCacheData
from common.cache.state import MigrateStorageState
from common.core.auth import ExpiringTokenAuthentication
from common.utils.caches import del_cache_response_by_short, get_app_today_download_times, del_cache_by_delete_app
from common.utils.download import get_app_download_url
from common.utils.storage import Storage
from common.utils.token import verify_token, get_random_download_token

logger = logging.getLogger(__name__)


def get_release_apps(request, res, app_serializer, apps_obj, storage):
    page_obj = AppsPageNumber()
    app_release_obj = AppReleaseInfo.objects.filter(app_id=apps_obj).all().order_by("-created_time")
    app_release_page_serializer = page_obj.paginate_queryset(queryset=app_release_obj, request=request)
    app_release_serializer = AppReleaseSerializer(app_release_page_serializer, many=True,
                                                  context={"storage": storage})
    res.data['has_next'] = page_obj.page.has_next()
    res.data["currentapp"] = app_serializer.data
    res.data["release_apps"] = app_release_serializer.data
    return res


def apps_filter(request):
    app_type = request.query_params.get("type", None)
    act_type = request.query_params.get("act", None)
    search = request.query_params.get("search", None)
    filter_data = {"user_id": request.user}
    if app_type == "android":
        filter_data["type"] = 0
    elif app_type == "ios":
        filter_data["type"] = 1
    if act_type == "combo":
        filter_data["has_combo"] = None
    app_query_set = Apps.objects.filter(**filter_data)
    if search:
        app_query_set = app_query_set.filter(Q(short=search) | Q(name__contains=search))
    return app_query_set.all()


class AppsPageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = 100  # 最大页码数限制


class AppsView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        res.hdata = {"all_hits_count": 0,
                     "ios_count": Apps.objects.filter(type=1, user_id=request.user).values('app_id').count(),
                     "android_count": Apps.objects.filter(type=0, user_id=request.user).values('app_id').count()}

        android_app_ids = Apps.objects.filter(**{"user_id": request.user, "type": 0}).values('app_id')
        android_app_ids = [app_dict.get('app_id') for app_dict in android_app_ids]
        res.hdata["android_today_hits_count"] = get_app_today_download_times(android_app_ids)

        ios_app_ids = Apps.objects.filter(**{"user_id": request.user, "type": 1}).values('app_id')
        ios_app_ids = [app_dict.get('app_id') for app_dict in ios_app_ids]
        res.hdata["ios_today_hits_count"] = get_app_today_download_times(ios_app_ids)

        all_hits_obj = Apps.objects.filter(user_id=request.user).aggregate(count_hits=Sum('count_hits'))
        if all_hits_obj:
            count_hits = all_hits_obj.get("count_hits", 0)
            if count_hits:
                if count_hits > 0:
                    logger.info(
                        f"update user all_download_times  old:{count_hits}  now:{request.user.all_download_times}")
                    UserInfo.objects.filter(pk=request.user.id).update(
                        all_download_times=count_hits)
            else:
                count_hits = 0
            res.hdata["all_hits_count"] = count_hits
        else:
            res.hdata["all_hits_count"] = 0

        apps_obj = apps_filter(request)
        page_obj = AppsPageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=apps_obj.order_by("-updated_time"), request=request,
                                                         view=self)

        app_serializer = AppsListSerializer(app_page_serializer, many=True, context={"storage": Storage(request.user)})

        res.data = app_serializer.data
        res.has_next = page_obj.page.has_next()
        return Response(res.dict)


class AppInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request, app_id):
        res = BaseResponse()
        if app_id:
            app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if app_obj:
                app_serializer = AppsSerializer(app_obj, context={"storage": Storage(request.user)})
                res.data = app_serializer.data
                res.data['storage_used'] = bytes2human(get_app_storage_used(app_obj))
            else:
                logger.error(f"app_id:{app_id} is not found in user:{request.user}")
                res.msg = "未找到该应用"
                res.code = 1003

        return Response(res.dict)

    def delete(self, request, app_id):
        res = BaseResponse()
        if app_id:
            app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            res = app_delete(app_obj)
        return Response(res.dict)

    def put(self, request, app_id):
        res = BaseResponse()
        if app_id:
            data = request.data
            if MigrateStorageState(request.user.uid).get_state():
                res.code = 1008
                res.msg = "数据迁移中，无法处理该操作"
                return Response(res.dict)

            has_combo = data.get("has_combo", None)
            if has_combo:
                actions = has_combo.get("action", None)
                hcombo_id = has_combo.get("hcombo_id", None)
                logger.info(f"app_id:{app_id} actions:{actions}  hcombo_id:{hcombo_id}")

                if actions and hcombo_id:
                    has_combo = Apps.objects.filter(user_id=request.user, app_id=hcombo_id)
                    apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id)
                    try:
                        if actions == "UNCOMBO":
                            if apps_obj.filter(has_combo=has_combo.first()).first():
                                apps_obj.update(has_combo=None)
                                has_combo.update(has_combo=None)

                        elif actions == "COMBO":
                            apps_obj.update(has_combo=has_combo.first())
                            has_combo.update(has_combo=apps_obj.first())
                        else:
                            pass
                        del_cache_response_by_short(apps_obj.first().app_id)
                        del_cache_response_by_short(has_combo.first().app_id)

                    except Exception as e:
                        logger.error(f"app_id:{app_id} actions:{actions} hcombo_id:{hcombo_id} Exception:{e}")
                        res.code = 1004
                        res.msg = "该应用已经关联"
            else:
                try:
                    app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
                    logger.info(f"app_id:{app_id} update old data:{app_obj.__dict__}")
                    app_obj.description = data.get("description", app_obj.description)
                    app_obj.short = data.get("short", app_obj.short)
                    app_obj.name = data.get("name", app_obj.name)
                    app_obj.need_password = data.get("need_password", app_obj.need_password)
                    app_obj.isshow = data.get("isshow", app_obj.isshow)
                    update_fields = ["description", "short", "name", "need_password", "isshow"]
                    if get_user_domain_name(request.user) or get_app_domain_name(app_obj):
                        app_obj.wxeasytype = data.get("wxeasytype", app_obj.wxeasytype)
                    else:
                        app_obj.wxeasytype = 1
                    update_fields.append("wxeasytype")
                    app_obj.wxredirect = data.get("wxredirect", app_obj.wxredirect)
                    update_fields.append("wxredirect")
                    logger.info(f"app_id:{app_id} update new data:{app_obj.__dict__}")
                    app_obj.save(update_fields=update_fields)
                    del_cache_response_by_short(app_obj.app_id)
                except Exception as e:
                    logger.error(f"app_id:{app_id} update Exception:{e}")
                    res.code = 1005
                    res.msg = "短连接已经存在"

        return Response(res.dict)

    def post(self, request, app_id):
        res = BaseResponse()
        res.data = Apps.objects.filter(short=app_id).count()
        return Response(res.dict)


class AppReleaseInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request, app_id, act):
        res = BaseResponse()
        res.data = {}
        if app_id:
            app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if app_obj:
                storage = Storage(request.user)
                app_serializer = AppsSerializer(app_obj, context={"storage": storage})
                res = get_release_apps(request, res, app_serializer, app_obj, storage)
            else:
                res.msg = "未找到该应用"
                res.code = 1003
        return Response(res.dict)

    def delete(self, request, app_id, act):
        res = BaseResponse()
        if app_id:

            if MigrateStorageState(request.user.uid).get_state():
                res.code = 1008
                res.msg = "数据迁移中，无法处理该操作"
                return Response(res.dict)

            app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if app_obj:
                storage = Storage(request.user)
                if act == 'screen':
                    screen_id = request.query_params.get('screen_id', None)
                    if screen_id:
                        screen_obj = AppScreenShot.objects.filter(pk=screen_id, app_id=app_obj).first()
                        if screen_obj:
                            storage.delete_file(screen_obj.screenshot_url)
                            screen_obj.delete()
                            del_cache_response_by_short(app_obj.app_id)
                    return Response(res.dict)

                app_release_count = AppReleaseInfo.objects.filter(app_id=app_obj).values("release_id").count()
                app_release_obj = AppReleaseInfo.objects.filter(app_id=app_obj, release_id=act).first()
                if app_release_obj:
                    if not app_release_obj.is_master:
                        logger.info(f"delete app release {app_release_obj}")
                        storage.delete_file(app_release_obj.release_id, app_release_obj.release_type)
                        delete_local_files(app_release_obj.release_id, app_release_obj.release_type)
                        storage.delete_file(app_release_obj.icon_url)

                        app_release_obj.delete()
                    elif app_release_obj.is_master and app_release_count < 2:
                        logger.info(f"delete app master release {app_release_obj} and clean app {app_obj}")
                        run_delete_app_signal(app_obj)

                        storage.delete_file(app_release_obj.release_id, app_release_obj.release_type)
                        delete_local_files(app_release_obj.release_id, app_release_obj.release_type)
                        storage.delete_file(app_release_obj.icon_url)
                        del_cache_by_delete_app(app_obj.app_id)

                        app_release_obj.delete()
                        delete_app_screenshots_files(storage, app_obj)
                        has_combo = app_obj.has_combo
                        if has_combo:
                            has_combo.has_combo = None
                            has_combo.save(update_fields=["has_combo"])
                            del_cache_response_by_short(has_combo.app_id)
                        MagicCacheData.invalid_cache(app_obj.app_id)
                        app_obj.delete()
                    else:
                        pass
                    if app_obj:
                        MagicCacheData.invalid_cache(app_obj.app_id)
                        del_cache_response_by_short(app_obj.app_id)

        return Response(res.dict)

    def put(self, request, app_id, act):
        res = BaseResponse()
        res.data = {}
        if app_id:

            if MigrateStorageState(request.user.uid).get_state():
                res.code = 1008
                res.msg = "数据迁移中，无法处理该操作"
                return Response(res.dict)

            app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if app_obj:
                app_release_objs = AppReleaseInfo.objects.filter(app_id=app_obj, release_id=act)
                data = request.data
                make_master = data.get("make_master", None)
                try:
                    if make_master and make_master == act:
                        AppReleaseInfo.objects.filter(app_id=app_obj).update(is_master=False)
                        app_release_objs.update(is_master=True)
                    else:
                        app_release_objs.update(changelog=data.get("changelog", app_release_objs.first().changelog))
                        binary_url = data.get("binary_url", None)
                        if binary_url != '':
                            if binary_url:
                                if not binary_url.startswith('http'):
                                    binary_url = f'http://{binary_url}'
                            else:
                                binary_url = app_release_objs.first().binary_url

                        app_release_objs.update(binary_url=binary_url)
                    logger.info(f"update app:{app_obj} release:{app_release_objs} data:{data}")
                except Exception as e:
                    logger.error(f"update app:{app_obj} release:{app_release_objs} failed Exception:{e}")
                    res.code = 1006
                    res.msg = "更新失败"
                    return Response(res.dict)

                del_cache_response_by_short(app_obj.app_id)
                app_serializer = AppsSerializer(app_obj)
                res = get_release_apps(request, res, app_serializer, app_obj, Storage(request.user))

        return Response(res.dict)

    def post(self, request, app_id, act):
        res = BaseResponse()
        downtoken = request.data.get("token", '')
        short = request.data.get("short", '')

        if not downtoken or not short or not act or not app_id:
            res.code = 1004
            res.msg = "参数丢失"
            return Response(res.dict)

        if verify_token(downtoken, act):
            res = get_app_download_url(request, res, app_id, short, None, act, True, '')
        else:
            res.code = 1004
            res.msg = "token校验失败"
        return Response(res.dict)


class AppsQrcodeShowView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        apps_obj = apps_filter(request)
        page_obj = AppsPageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=apps_obj.order_by("-updated_time"), request=request,
                                                         view=self)

        app_serializer = AppsQrListSerializer(app_page_serializer, many=True,
                                              context={"storage": Storage(request.user)})

        res.data = app_serializer.data
        res.has_next = page_obj.page.has_next()
        return Response(res.dict)


class AppDownloadTokenView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request, app_id):
        res = BaseResponse()
        dpwdsearch = request.query_params.get('dpwdsearch')
        app_token_queryset = AppDownloadToken.objects.filter(app_id__user_id=request.user, app_id__app_id=app_id)
        if dpwdsearch:
            app_token_queryset = app_token_queryset.filter(Q(token=dpwdsearch) | Q(bind_udid=dpwdsearch))
        page_obj = AppsPageNumber()
        app_token_page_serializer = page_obj.paginate_queryset(queryset=app_token_queryset.order_by("-create_time"),
                                                               request=request, view=self)

        app_token_serializer = AppDownloadTokenSerializer(app_token_page_serializer, many=True)

        res.data = app_token_serializer.data
        res.count = app_token_queryset.count()
        return Response(res.dict)

    def post(self, request, app_id):
        res = BaseResponse()
        data = request.data
        token = data.get('token')
        token_length = data.get('token_length')
        token_number = data.get('token_number')
        bind_status = data.get('bind_status')
        token_max_used_number = data.get('token_max_used_number')
        udid_list_str = data.get('udids')
        udid_list = []

        if not isinstance(bind_status, bool):
            bind_status = False
        if bind_status:
            token_max_used_number = 1
            if udid_list_str and len(udid_list_str) > 10:
                udid_list = udid_list_str.replace('  ', ' ').replace('\n', ' ').replace(',', ' ').replace('\r\n',
                                                                                                          ' ').split()
                udid_list = set(filter(lambda x: len(x) > 10, udid_list))
                token = ''

        app_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
        if token and isinstance(token, str) and len(token) >= 4:
            AppDownloadToken.objects.update_or_create(app_id=app_obj, token=token,
                                                      defaults={"max_limit_count": token_max_used_number,
                                                                "bind_status": bind_status})
        else:
            if isinstance(token_length, int) and 4 <= token_length <= 32:
                pass
            else:
                token_length = 6
            if isinstance(token_number, int) and 1 <= token_number <= 1024:
                pass
            else:
                token_number = 20

            if udid_list:
                bind_udid_list = AppDownloadToken.objects.filter(app_id=app_obj, bind_udid__isnull=False).values_list(
                    'bind_udid')
                udid_list = list(udid_list - set([x[0] for x in bind_udid_list]))
                token_number = len(udid_list)

            download_token_queryset = AppDownloadToken.objects.filter(app_id=app_obj).annotate(
                token_len=Length('token')).filter(token_len=token_length).values('token').all()
            exist_token = [d_token['token'] for d_token in download_token_queryset]
            make_token_list = get_random_download_token(token_length=token_length,
                                                        token_number=token_number + download_token_queryset.count(),
                                                        exist_token=copy.deepcopy(exist_token))
            bulk_list = []
            d_index = 0
            for d_token in list(set(make_token_list) - set(exist_token))[:token_number]:
                n_data = {
                    'token': d_token,
                    'max_limit_count': token_max_used_number,
                    'app_id': app_obj,
                    'bind_status': bind_status,
                }
                if udid_list:
                    n_data['bind_udid'] = udid_list[d_index]
                    n_data['used_count'] = 1
                    d_index += 1
                bulk_list.append(AppDownloadToken(**n_data))
            AppDownloadToken.objects.bulk_create(bulk_list)

        return Response(res.dict)

    def put(self, request, app_id):
        res = BaseResponse()
        token = request.data.get('token')
        act = request.data.get('act')
        if token is not None:
            AppDownloadToken.objects.filter(app_id__user_id=request.user,
                                            app_id__app_id=app_id, token=token).update(used_count=0, bind_udid=None)
        if act:
            if act == 'all':
                AppDownloadToken.objects.filter(app_id__user_id=request.user, app_id__app_id=app_id).delete()
            elif act == 'invalid':
                AppDownloadToken.objects.filter(app_id__user_id=request.user,
                                                app_id__app_id=app_id,
                                                used_count__gte=F('max_limit_count'),
                                                max_limit_count__gt=0, bind_udid__isnull=False).delete()
            elif act == 'some':
                tokens = request.data.get('tokens')
                if tokens and isinstance(tokens, list):
                    AppDownloadToken.objects.filter(app_id__user_id=request.user,
                                                    app_id__app_id=app_id, token__in=tokens).delete()

        return Response(res.dict)
