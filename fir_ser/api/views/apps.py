#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4

from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
from django.db.models import Sum
import os
from fir_ser import settings
from api.utils.app.randomstrings import make_from_user_uuid
from api.utils.storage.storage import Storage
from api.utils.storage.caches import del_cache_response_by_short,get_app_today_download_times
from api.models import Apps, AppReleaseInfo
from api.utils.serializer import AppsSerializer, AppReleaseSerializer, UserInfoSerializer
from rest_framework.pagination import PageNumberPagination


# REDIS_CONN = redis.Redis(decode_responses=True)


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
                    request.user.all_download_times += count_hits
                    request.user.save()
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
                res.msg = "未找到该应用"
                res.code = 1003
            userserializer = UserInfoSerializer(request.user)
            res.userinfo = {}
            res.userinfo = userserializer.data
        return Response(res.dict)

    def delete(self, request, app_id):
        res = BaseResponse()
        if app_id:
            apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if apps_obj:
                storage = Storage(request.user)
                for appreleaseobj in AppReleaseInfo.objects.filter(app_id=apps_obj).all():
                    storage.delete_file(appreleaseobj.release_id, appreleaseobj.release_type)
                    storage.delete_file(appreleaseobj.icon_url)
                    appreleaseobj.delete()

                has_combo = apps_obj.has_combo
                if has_combo:
                    del_cache_response_by_short(apps_obj.has_combo.short,apps_obj.has_combo.app_id)
                    apps_obj.has_combo.has_combo = None

                apps_obj.delete()
                del_cache_response_by_short(apps_obj.short,apps_obj.app_id)

        return Response(res.dict)

    def put(self, request, app_id):
        res = BaseResponse()
        if app_id:
            data = request.data

            has_combo = data.get("has_combo", None)
            if has_combo:
                actions = has_combo.get("action", None)
                hcombo_id = has_combo.get("hcombo_id", None)

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
                        del_cache_response_by_short(apps_obj.first().short,apps_obj.first().app_id)
                        del_cache_response_by_short(has_combo.first().short,has_combo.first().app_id)

                    except Exception as e:
                        res.code = 1004
                        res.msg = "该应用已经关联"
            else:
                try:
                    apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
                    apps_obj.description = data.get("description", apps_obj.description)
                    del_cache_response_by_short(apps_obj.short,apps_obj.app_id)
                    apps_obj.short = data.get("short", apps_obj.short)
                    apps_obj.name = data.get("name", apps_obj.name)
                    apps_obj.password = data.get("password", apps_obj.password)
                    apps_obj.isshow = data.get("isshow", apps_obj.isshow)
                    apps_obj.save()
                except Exception as e:
                    res.code = 1005
                    res.msg = "短连接已经存在"

        return Response(res.dict)

    def post(self, request, app_id):
        res = BaseResponse()

        # 获取多个file
        files = request.FILES.getlist('file', None)
        for file_obj in files:
            # 将文件缓存到本地后上传
            try:
                app_type = file_obj.name.split(".")[-1]
                if app_type in ['png', 'jpeg', 'jpg']:
                    # 上传图片
                    pass
                else:
                    raise
            except Exception as e:
                res.code = 1003
                res.msg = "错误的类型"
                return Response(res.dict)

            if app_id:
                apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
                if apps_obj:
                    release_obj = AppReleaseInfo.objects.filter(app_id=apps_obj, is_master=True).first()
                    if release_obj:

                        random_file_name = make_from_user_uuid(request.user)
                        old_file_name = os.path.basename(release_obj.icon_url)
                        local_file = os.path.join(settings.MEDIA_ROOT, "icons",
                                                  random_file_name + "." + old_file_name.split(".")[1])
                        # 读取传入的文件
                        try:
                            destination = open(local_file, 'wb+')
                            for chunk in file_obj.chunks():
                                # 写入本地文件
                                destination.write(chunk)
                            destination.close()
                        except Exception as e:
                            res.code = 1003
                            res.msg = "数据写入失败"
                            return Response(res.dict)
                        release_obj.icon_url = release_obj.icon_url.replace(old_file_name.split(".")[0],
                                                                            random_file_name)
                        release_obj.save()
                        del_cache_response_by_short(apps_obj.short,apps_obj.app_id)

                        storage = Storage(request.user)
                        storage.delete_file(old_file_name)

                    else:
                        res.code = 1003
                else:
                    res.code = 1003
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
                    storage.delete_file(appreleaseobj.release_id, appreleaseobj.release_type)
                    storage.delete_file(appreleaseobj.icon_url)

                    appreleaseobj.delete()
                elif appreleaseobj.is_master and apprelease_count < 2:
                    storage.delete_file(appreleaseobj.release_id, appreleaseobj.release_type)
                    storage.delete_file(appreleaseobj.icon_url)

                    appreleaseobj.delete()

                    has_combo = apps_obj.has_combo
                    if has_combo:
                        apps_obj.has_combo.has_combo = None
                    apps_obj.delete()
                else:
                    pass
                del_cache_response_by_short(apps_obj.short,apps_obj.app_id)

        return Response(res.dict)

    def put(self, request, app_id, act):
        res = BaseResponse()
        res.data = {}
        if app_id:
            apps_obj = Apps.objects.filter(user_id=request.user, app_id=app_id).first()
            if apps_obj:
                appreleaseobj = AppReleaseInfo.objects.filter(app_id=apps_obj, release_id=act)

                make_master = request.data.get("make_master", None)
                try:
                    if make_master and make_master == act:
                        AppReleaseInfo.objects.filter(app_id=apps_obj).update(**{"is_master": False})
                        appreleaseobj.update(**{"is_master": True})
                    else:
                        appreleaseobj.update(
                            **{"changelog": request.data.get("changelog", appreleaseobj.first().changelog)})
                        binary_url = request.data.get("binary_url", None)
                        if binary_url != '':
                            if binary_url:
                                if not binary_url.startswith('http'):
                                    binary_url = 'http://%s' % binary_url
                            else:
                                binary_url = appreleaseobj.first().binary_url

                        print(binary_url)
                        appreleaseobj.update(**{"binary_url": binary_url})

                except Exception as e:
                    res.code = 1006
                    res.msg = "更新失败"
                    return Response(res.dict)

                del_cache_response_by_short(apps_obj.short,apps_obj.app_id)
                app_serializer = AppsSerializer(apps_obj)
                res.data["currentapp"] = app_serializer.data

                app_release_obj = AppReleaseInfo.objects.filter(app_id=apps_obj).all().order_by("-created_time")
                app_release_serializer = AppReleaseSerializer(app_release_obj, many=True,
                                                              context={"storage": Storage(request.user)})
                res.data["release_apps"] = app_release_serializer.data

        return Response(res.dict)
