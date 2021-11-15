#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6
import logging

from celery.exceptions import TimeoutError
from django.http import HttpResponsePermanentRedirect, FileResponse, HttpResponse
from django.views import View
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Apps
from api.tasks import run_sign_task
from api.utils.app.supersignutils import udid_bytes_to_dict, make_sign_udid_mobile_config
from api.utils.baseutils import get_real_ip_address, get_http_server_domain, make_random_uuid
from api.utils.modelutils import get_app_domain_name, get_redirect_server_domain, add_remote_info_from_request
from api.utils.response import BaseResponse
from api.utils.storage.caches import check_app_permission
from api.utils.throttle import ReceiveUdidThrottle1, ReceiveUdidThrottle2
from fir_ser.celery import app

logger = logging.getLogger(__name__)


class UdidView(View):
    throttle_classes = []

    def check_throttles(self, request):
        """
        Check if request should be throttled.
        Raises an appropriate exception if the request is throttled.
        """
        throttle_durations = []
        for throttle in [throttle() for throttle in self.throttle_classes]:
            if not throttle.allow_request(request, self):
                throttle_durations.append(throttle.wait())

        if throttle_durations:
            durations = [
                duration for duration in throttle_durations
                if duration is not None
            ]

            duration = max(durations, default=None)
            raise exceptions.Throttled(duration)

    def dispatch(self, request, *args, **kwargs):
        try:
            self.check_throttles(request)
        except Exception as e:
            r_url = f"{get_redirect_server_domain(request)}/{kwargs.get('short')}?udid={str(e)}&msg=访问受限制，请稍后再试"
            logger.error(f"ip:{get_real_ip_address(request)} short:{kwargs.get('short')} {str(e)}")
            return HttpResponsePermanentRedirect(r_url)
        return super().dispatch(request, *args, **kwargs)


class IosUDIDView(UdidView):
    throttle_classes = [ReceiveUdidThrottle1, ReceiveUdidThrottle2]

    def post(self, request, short):
        stream_f = str(request.body)
        format_udid_info = udid_bytes_to_dict(stream_f)
        logger.info(f"short {short} receive new udid {format_udid_info}")
        server_domain = get_redirect_server_domain(request)
        try:
            app_obj = Apps.objects.filter(short=short).first()
            if app_obj:
                server_domain = get_redirect_server_domain(request, app_obj.user_id, get_app_domain_name(app_obj))
                if app_obj.issupersign and app_obj.user_id.supersign_active:
                    res = check_app_permission(app_obj, BaseResponse())
                    if res.code != 1000:
                        msg = "&msg=%s" % res.msg
                    else:
                        client_ip = get_real_ip_address(request)
                        logger.info(f"client_ip {client_ip} short {short} app_info {app_obj}")

                        # ios_obj = IosUtils(format_udid_info, app_obj.user_id, app_obj)
                        # ios_obj.sign(client_ip)
                        # return Response('ok')
                        c_task = run_sign_task.apply_async((format_udid_info, short, client_ip))
                        add_remote_info_from_request(request, f'{app_obj}-{format_udid_info}')
                        task_id = c_task.id
                        logger.info(f"sign app {app_obj} task_id:{task_id}")
                        try:
                            result = c_task.get(propagate=False, timeout=0.5)
                        except TimeoutError:
                            result = ''
                        if c_task.successful():
                            c_task.forget()
                            msg = "&msg=%s" % result
                        else:
                            msg = "&task_id=%s" % task_id
                else:
                    return HttpResponsePermanentRedirect(
                        "%s/%s" % (server_domain, short))
            else:
                return HttpResponsePermanentRedirect(
                    "%s/%s" % (server_domain, short))
        except Exception as e:
            msg = "&msg=系统内部错误"
            logger.error(f"short {short} receive udid Exception:{e}")

        return HttpResponsePermanentRedirect(
            "%s/%s?udid=%s%s" % (server_domain, short, format_udid_info.get("udid"), msg))


class TaskView(APIView):

    def get(self, request, short):
        res = BaseResponse()
        task_id = request.query_params.get('task_id', None)
        if task_id:
            app_info = Apps.objects.filter(short=short).first()
            if app_info:
                result = app.AsyncResult(task_id)
                logger.info(f"app {app_info} sign task state {result.state}  AA {result.successful()}")
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


class ShowUdidView(View):
    def get(self, request):
        udid = request.GET.get("udid")
        if udid:
            return HttpResponse("udid: %s" % udid)
        server_domain = get_http_server_domain(request)
        path_info_lists = [server_domain, "show_udid"]
        udid_url = "/".join(path_info_lists)
        ios_udid_mobile_config = make_sign_udid_mobile_config(udid_url, 'show_udid_info', 'flyapps.cn', '查询设备udid')
        response = FileResponse(ios_udid_mobile_config)
        response['Content-Type'] = "application/x-apple-aspen-config"
        response['Content-Disposition'] = 'attachment; filename=' + make_random_uuid() + '.mobileconfig'
        return response

    def post(self, request):
        stream_f = str(request.body)
        format_udid_info = udid_bytes_to_dict(stream_f)
        logger.info(f"show_udid receive new udid {format_udid_info}")
        server_domain = get_http_server_domain(request)
        return HttpResponsePermanentRedirect(
            "%s/show_udid?udid=%s" % (server_domain, format_udid_info.get("udid")))
