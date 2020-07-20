#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from django.db.models import Sum, F
from api.utils.app.supersignutils import IosUtils
from api.utils.storage.storage import Storage
from api.utils.storage.caches import del_cache_response_by_short, get_app_today_download_times
from api.models import Apps, AppReleaseInfo, APPToDeveloper, AppIOSDeveloperInfo, UserInfo
from api.utils.serializer import AppsSerializer, AppReleaseSerializer, UserInfoSerializer
from rest_framework.pagination import PageNumberPagination
import logging

logger = logging.getLogger(__name__)


class AppsPageNumber(PageNumberPagination):
    page_size = 20  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class AppsView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):

        app_type = request.query_params.get("type", None)
        act_type = request.query_params.get("act", None)
        res = BaseResponse()
        res.hdata = {"all_hits_count": 0}
        res.hdata["upload_domain"] = request.user.domain_name
        res.hdata["ios_count"] = Apps.objects.filter(type=1, user_id=request.user).values('app_id').count()
        res.hdata["android_count"] = Apps.objects.filter(type=0, user_id=request.user).values('app_id').count()

        android_app_ids = Apps.objects.filter(**{"user_id": request.user, "type": 0}).values('app_id')
        res.hdata["android_today_hits_count"] = get_app_today_download_times(android_app_ids)

        ios_app_ids = Apps.objects.filter(**{"user_id": request.user, "type": 1}).values('app_id')
        res.hdata["ios_today_hits_count"] = get_app_today_download_times(ios_app_ids)

        all_hits_obj = Apps.objects.filter(user_id=request.user).aggregate(count_hits=Sum('count_hits'))
        if all_hits_obj:
            count_hits = all_hits_obj.get("count_hits", 0)
            if count_hits:
                if count_hits > 0:
                    logger.info(
                        "update user all_download_times  old:%s  now:%s" % (
                            count_hits, request.user.all_download_times))
                    UserInfo.objects.filter(pk=request.user.id).update(
                        all_download_times=count_hits)
            else:
                count_hits = 0
            res.hdata["all_hits_count"] = count_hits
        else:
            res.hdata["all_hits_count"] = 0

        if app_type == "android":
            filter_data = {"user_id": request.user, "type": 0}

        elif app_type == "ios":
            filter_data = {"user_id": request.user, "type": 1}
        else:
            filter_data = {"user_id": request.user}

        if act_type == "combo":
            filter_data["has_combo"] = None

        apps_obj = Apps.objects.filter(**filter_data)
        logger.info(filter_data)
        page_obj = AppsPageNumber()
        app_page_serializer = page_obj.paginate_queryset(queryset=apps_obj.order_by("-updated_time"), request=request,
                                                         view=self)

        app_serializer = AppsSerializer(app_page_serializer, many=True, context={"storage": Storage(request.user)})

        userserializer = UserInfoSerializer(request.user)
        res.userinfo = {}
        res.has_next = {}
        res.userinfo = userserializer.data
        res.data = app_serializer.data
        res.has_next = page_obj.page.has_next()
        return Response(res.dict)


class AppInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request, app_id):
        res = BaseResponse()
        if app_id:
            apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if apps_obj:
                app_serializer = AppsSerializer(apps_obj, context={"storage": Storage(request.user)})
                res.data = app_serializer.data
            else:
                logger.error("app_id:%s is not found in user:%s " % (app_id, request.user))
                res.msg = "未找到该应用"
                res.code = 1003
            userserializer = UserInfoSerializer(request.user)
            res.userinfo = {}
            res.userinfo = userserializer.data
            count = APPToDeveloper.objects.filter(app_id=apps_obj).count()
            res.data["count"] = count

        return Response(res.dict)

    def delete(self, request, app_id):
        res = BaseResponse()
        if app_id:
            apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if apps_obj:
                if apps_obj.issupersign:
                    logger.info("app_id:%s is supersign ,delete this app need clean IOS developer" % (app_id))
                    IosUtils.clean_app_by_user_obj(apps_obj, request.user)

                storage = Storage(request.user)
                has_combo = apps_obj.has_combo
                if has_combo:
                    logger.info(
                        "app_id:%s has_combo ,delete this app need uncombo and clean del_cache_response_by_short" % (
                            app_id))
                    apps_obj.has_combo.has_combo = None
                del_cache_response_by_short(apps_obj.app_id)
                for appreleaseobj in AppReleaseInfo.objects.filter(app_id=apps_obj).all():
                    logger.info("delete app_id:%s  need clean all release,release_id:%s" % (
                        app_id, appreleaseobj.release_id))
                    storage.delete_file(appreleaseobj.release_id, appreleaseobj.release_type)
                    storage.delete_file(appreleaseobj.icon_url)
                    appreleaseobj.delete()
                apps_obj.delete()

        return Response(res.dict)

    def put(self, request, app_id):
        res = BaseResponse()
        if app_id:
            data = request.data

            clean = data.get("clean", None)
            if clean:
                logger.info("app_id:%s clean:%s ,close supersign should clean_app_by_user_obj" % (app_id, clean))
                apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
                IosUtils.clean_app_by_user_obj(apps_obj, request.user)
                return Response(res.dict)

            has_combo = data.get("has_combo", None)
            if has_combo:
                actions = has_combo.get("action", None)
                hcombo_id = has_combo.get("hcombo_id", None)
                logger.info("app_id:%s actions:%s  hcombo_id:%s" % (app_id, actions, hcombo_id))

                if actions and hcombo_id:
                    has_combo = Apps.objects.filter(user_id=request.user, app_id=hcombo_id)
                    apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id)
                    try:
                        if actions == "UNCOMBO":
                            if apps_obj.filter(has_combo=has_combo.first()).first():
                                apps_obj.update(**{"has_combo": None})
                                has_combo.update(**{"has_combo": None})

                        elif actions == "COMBO":
                            apps_obj.update(**{"has_combo": has_combo.first()})
                            has_combo.update(**{"has_combo": apps_obj.first()})
                        else:
                            pass
                        del_cache_response_by_short(apps_obj.first().app_id)

                    except Exception as e:
                        logger.error("app_id:%s actions:%s hcombo_id:%s Exception:%s" % (app_id, actions, hcombo_id, e))
                        res.code = 1004
                        res.msg = "该应用已经关联"
            else:
                try:
                    apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
                    logger.info("app_id:%s update old data:%s" % (app_id, apps_obj.__dict__))
                    apps_obj.description = data.get("description", apps_obj.description)
                    apps_obj.short = data.get("short", apps_obj.short)
                    apps_obj.name = data.get("name", apps_obj.name)
                    apps_obj.password = data.get("password", apps_obj.password)
                    apps_obj.isshow = data.get("isshow", apps_obj.isshow)
                    if request.user.domain_name and len(request.user.domain_name) > 3:
                        apps_obj.wxeasytype = data.get("wxeasytype", apps_obj.wxeasytype)
                    else:
                        apps_obj.wxeasytype = 1

                    apps_obj.wxredirect = data.get("wxredirect", apps_obj.wxredirect)
                    if apps_obj.type == 1:
                        # 为啥注释掉，就是该udid已经在该平台使用了，虽然已经没有余额，但是其他应用也是可以超级签名的
                        # developer_obj = AppIOSDeveloperInfo.objects.filter(user_id=request.user)
                        # use_num = get_developer_devices(developer_obj)
                        # if use_num.get("flyapp_used_sum") >= use_num.get("all_usable_number"):
                        #     res.code = 1008
                        #     res.msg = "超级签余额不足，无法开启"
                        #     return Response(res.dict)
                        developer_count = AppIOSDeveloperInfo.objects.filter(user_id=request.user).count()
                        if developer_count == 0:
                            logger.error("app_id:%s can't open supersign,owner has no ios developer" % (app_id))
                            res.code = 1008
                            res.msg = "超级签开发者不存在，无法开启"
                            return Response(res.dict)
                        apps_obj.issupersign = data.get("issupersign", apps_obj.issupersign)
                    logger.info("app_id:%s update new data:%s" % (app_id, apps_obj.__dict__))
                    apps_obj.save()
                    del_cache_response_by_short(apps_obj.app_id)
                except Exception as e:
                    logger.error("app_id:%s update Exception:%s" % (app_id, e))
                    res.code = 1005
                    res.msg = "短连接已经存在"

        return Response(res.dict)


class AppReleaseinfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request, app_id, act):
        res = BaseResponse()
        res.data = {}
        if app_id:
            apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if apps_obj:
                app_serializer = AppsSerializer(apps_obj, context={"storage": Storage(request.user)})
                res.data["currentapp"] = app_serializer.data

                app_release_obj = AppReleaseInfo.objects.filter(app_id=apps_obj).all().order_by("-created_time")
                app_release_serializer = AppReleaseSerializer(app_release_obj, many=True,
                                                              context={"storage": Storage(request.user)})
                res.data["release_apps"] = app_release_serializer.data

            else:
                res.msg = "未找到该应用"
                res.code = 1003
        return Response(res.dict)

    def delete(self, request, app_id, act):
        res = BaseResponse()
        if app_id:
            apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if apps_obj:
                storage = Storage(request.user)
                apprelease_count = AppReleaseInfo.objects.filter(app_id=apps_obj).values("release_id").count()
                appreleaseobj = AppReleaseInfo.objects.filter(app_id=apps_obj, release_id=act).first()
                if not appreleaseobj.is_master:
                    logger.info("delete app release %s" % (appreleaseobj))
                    storage.delete_file(appreleaseobj.release_id, appreleaseobj.release_type)
                    storage.delete_file(appreleaseobj.icon_url)

                    appreleaseobj.delete()
                elif appreleaseobj.is_master and apprelease_count < 2:
                    logger.info("delete app master release %s and clean app %s " % (appreleaseobj, apps_obj))

                    if apps_obj.issupersign:
                        logger.info("app_id:%s is supersign ,delete this app need clean IOS developer" % (app_id))
                        IosUtils.clean_app_by_user_obj(apps_obj, request.user)

                    storage.delete_file(appreleaseobj.release_id, appreleaseobj.release_type)
                    storage.delete_file(appreleaseobj.icon_url)

                    appreleaseobj.delete()

                    has_combo = apps_obj.has_combo
                    if has_combo:
                        apps_obj.has_combo.has_combo = None
                    apps_obj.delete()
                else:
                    pass
                del_cache_response_by_short(apps_obj.app_id)

        return Response(res.dict)

    def put(self, request, app_id, act):
        res = BaseResponse()
        res.data = {}
        if app_id:
            apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if apps_obj:
                appreleaseobj = AppReleaseInfo.objects.filter(app_id=apps_obj, release_id=act)
                data = request.data
                make_master = data.get("make_master", None)
                try:
                    if make_master and make_master == act:
                        AppReleaseInfo.objects.filter(app_id=apps_obj).update(**{"is_master": False})
                        appreleaseobj.update(**{"is_master": True})
                    else:
                        appreleaseobj.update(
                            **{"changelog": data.get("changelog", appreleaseobj.first().changelog)})
                        binary_url = data.get("binary_url", None)
                        if binary_url != '':
                            if binary_url:
                                if not binary_url.startswith('http'):
                                    binary_url = 'http://%s' % binary_url
                            else:
                                binary_url = appreleaseobj.first().binary_url

                        appreleaseobj.update(**{"binary_url": binary_url})
                    logger.info("update app:%s release:%s data:%s" % (apps_obj, appreleaseobj, data))
                except Exception as e:
                    logger.error("update app:%s release:%s failed Exception:%s" % (apps_obj, appreleaseobj, e))
                    res.code = 1006
                    res.msg = "更新失败"
                    return Response(res.dict)

                del_cache_response_by_short(apps_obj.app_id)
                app_serializer = AppsSerializer(apps_obj)
                res.data["currentapp"] = app_serializer.data

                app_release_obj = AppReleaseInfo.objects.filter(app_id=apps_obj).all().order_by("-created_time")
                app_release_serializer = AppReleaseSerializer(app_release_obj, many=True,
                                                              context={"storage": Storage(request.user)})
                res.data["release_apps"] = app_release_serializer.data

        return Response(res.dict)
