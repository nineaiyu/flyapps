#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6
import json
import logging
from urllib.parse import quote

from celery.exceptions import TimeoutError
from django.http import HttpResponsePermanentRedirect, FileResponse, HttpResponse
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Apps, AppDownloadToken
from api.utils.modelutils import get_redirect_server_domain, add_remote_info_from_request, \
    get_app_download_uri
from api.utils.response import BaseResponse
from common.base.baseutils import get_real_ip_address, make_random_uuid, get_server_domain_from_request, AesBaseCrypt
from common.cache.storage import TaskStateCache
from common.core.sysconfig import Config
from common.core.throttle import ReceiveUdidThrottle1, ReceiveUdidThrottle2, VisitShortThrottle, InstallShortThrottle
from common.utils.caches import check_app_permission
from common.utils.download import check_app_download_token
from common.utils.pending import get_pending_result
from common.utils.token import verify_token, make_token
from fir_ser.celery import app
from xsign.tasks import run_sign_task
from xsign.utils.supersignutils import udid_bytes_to_dict, make_sign_udid_mobile_config

logger = logging.getLogger(__name__)


class IosUDIDView(APIView):
    throttle_classes = [ReceiveUdidThrottle1, ReceiveUdidThrottle2]

    def post(self, request, short):
        p_info = request.query_params.get('p')
        p_token = app_id = ''
        if p_info:
            p_token = p_info[:52]
            app_id = p_info[55:len(p_info) - 3]

        if not p_token or not app_id:
            return HttpResponsePermanentRedirect(Config.WEB_DOMAIN)
        stream_f = str(request.body)
        format_udid_info = udid_bytes_to_dict(stream_f)
        logger.info(f"short {short} receive new udid {format_udid_info}")
        server_domain = get_redirect_server_domain(request)
        try:
            app_obj = Apps.objects.filter(short=short, app_id=app_id).first()
            if app_obj:
                if p_token and verify_token(p_token, app_obj.app_id, True):
                    server_domain = get_app_download_uri(request, app_obj.user_id, app_obj, preview=False)
                    if app_obj.issupersign and app_obj.user_id.supersign_active:
                        res = check_app_permission(app_obj, BaseResponse())
                        if res.code != 1000:
                            msg = "&msg=%s" % res.msg
                        else:
                            client_ip = get_real_ip_address(request)
                            logger.info(f"client_ip {client_ip} short {short} app_info {app_obj}")

                            # from api.utils.app.supersignutils import IosUtils
                            # ios_obj = IosUtils(format_udid_info, app_obj.user_id, app_obj)
                            # ios_obj.sign_ipa(client_ip)
                            # return Response('ok')
                            data = {
                                'format_udid_info': format_udid_info,
                                'short': short,
                                'app_id': app_id,
                                'client_ip': client_ip,
                                'r_token': make_token(app_obj.app_id, time_limit=30, key='receive_udid', force_new=True)
                            }
                            encrypt_data = AesBaseCrypt().get_encrypt_uid(json.dumps(data))
                            msg = "&task_token=%s" % quote(encrypt_data, safe='/', encoding=None, errors=None)
                            token_obj = AppDownloadToken.objects.filter(app_id__app_id=app_id,
                                                                        bind_udid=format_udid_info.get('udid')).first()
                            if token_obj:
                                msg = f"{msg}&password={token_obj.token}"
                    else:
                        return HttpResponsePermanentRedirect(f"{server_domain}/{short}")
                else:
                    return HttpResponsePermanentRedirect(f"{server_domain}/{short}")
            else:
                return HttpResponsePermanentRedirect(f"{server_domain}/{short}")
        except Exception as e:
            msg = "&msg=系统内部错误"
            logger.error(f"short {short} receive udid Exception:{e}")

        return HttpResponsePermanentRedirect(f"{server_domain}/{short}?udid={format_udid_info.get('udid')}{msg}")


def expect_func(result, *args, **kwargs):
    app_info = kwargs.get('app_info')
    logger.info(f"app {app_info} sign task state {result.state}  AA {result.successful()}")
    cache = TaskStateCache(app_info.pk, kwargs.get('task_id'))
    if result.state == 'SUCCESS':
        cache.del_storage_cache()
        return True
    cache_data = cache.get_storage_cache()
    if not cache_data:
        cache.set_storage_cache(result.state)
        return True
    else:
        if cache_data == result.state:
            return False
        else:
            cache.set_storage_cache(result.state)
            return True


def task_func(task_id, *args, **kwargs):
    return app.AsyncResult(task_id)


class TaskView(APIView):
    throttle_classes = [VisitShortThrottle, InstallShortThrottle]

    def get(self, request, short):
        res = BaseResponse()
        task_id = request.query_params.get('task_id', None)
        unique_key = request.query_params.get('unique_key', task_id)
        if task_id and unique_key:
            app_info = Apps.objects.filter(short=short).first()
            if app_info:
                status, result = get_pending_result(task_func, expect_func, task_id=task_id,
                                                    locker_key=task_id, app_info=app_info, unique_key=unique_key)
                if status and result.get('data'):
                    result = result.get('data')
                    if result.successful():
                        res.msg = result.get(propagate=False)
                        return Response(res.dict)
                    elif result.state in ['PENDING']:
                        res.msg = '签名队列中'
                    elif result.state in ['STARTED']:
                        res.msg = '正在签名中'
                else:
                    res.msg = ''
                res.code = 1001
                return Response(res.dict)
        res.code = 1002
        return Response(res.dict)

    def post(self, request, short):
        res = BaseResponse()
        task_token = request.data.get('task_token', None)
        password = request.data.get('password', None)
        client_ip = get_real_ip_address(request)
        if task_token:
            data = json.loads(AesBaseCrypt().get_decrypt_uid(task_token))
            if client_ip != data.get('client_ip', ''):
                res.msg = '检测到网络异常，请重试'
                res.code = 1001
            if short != data.get('short', ''):
                res.msg = '数据异常，请重试'
                res.code = 1002

            app_obj = Apps.objects.filter(short=short, app_id=data.get('app_id')).first()
            if not app_obj:
                res.msg = '错误，数据异常，请重试'
                res.code = 1003

            format_udid_info = data.get('format_udid_info')
            udid = format_udid_info.get('udid')

            if not verify_token(data.get('r_token', ''), app_obj.app_id, False):
                res.msg = '授权过期，请重试'
                res.code = 1004

            if not check_app_download_token(app_obj.need_password, False, app_obj.app_id, password, False, udid):
                res.code = 1006
                res.msg = '下载授权码有误'

            if res.code != 1000:
                return Response(res.dict)

            c_task = run_sign_task.apply_async((format_udid_info, short, client_ip))
            add_remote_info_from_request(request, f'{app_obj}-{format_udid_info}')
            task_id = c_task.id
            logger.info(f"sign app {app_obj} task_id:{task_id}")
            try:
                result = c_task.get(propagate=False, timeout=1)
            except TimeoutError:
                logger.error(f"get task task_id:{task_id} result timeout")
                result = ''
            if c_task.successful():
                c_task.forget()
                res.result = result
            else:
                res.task_id = task_id
            return Response(res.dict)
        else:
            res.code = 1001
            res.msg = '数据异常，请重试'
        return Response(res.dict)


class ShowUdidView(View):
    def get(self, request):
        udid = request.GET.get("udid")
        if udid:
            return HttpResponse("udid: %s" % udid)
        server_domain = get_server_domain_from_request(request, Config.POST_UDID_DOMAIN)
        path_info_lists = [server_domain, "show_udid"]
        udid_url = "/".join(path_info_lists)
        ios_udid_mobile_config = make_sign_udid_mobile_config(udid_url, 'flyapps.cn', '查询设备udid')
        response = FileResponse(ios_udid_mobile_config)
        response['Content-Type'] = "application/x-apple-aspen-config"
        response['Content-Disposition'] = 'attachment; filename=' + make_random_uuid() + '.mobileconfig'
        return response

    def post(self, request):
        stream_f = str(request.body)
        format_udid_info = udid_bytes_to_dict(stream_f)
        logger.info(f"show_udid receive new udid {format_udid_info}")
        server_domain = get_server_domain_from_request(request, Config.POST_UDID_DOMAIN)
        return HttpResponsePermanentRedirect(
            "%s/show_udid?udid=%s" % (server_domain, format_udid_info.get("udid")))
