#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6

from api.utils.app.supersignutils import udid_bytes_to_dict, get_redirect_server_domain, IosUtils
from api.models import Apps
from django.views import View
from django.http import HttpResponsePermanentRedirect
from rest_framework.response import Response
from api.tasks import run_sign_task
from api.utils.response import BaseResponse
from api.utils.storage.caches import check_app_permission
from fir_ser.celery import app
import logging
from rest_framework.views import APIView

from api.utils.baseutils import get_app_domain_name
from celery.exceptions import TimeoutError

logger = logging.getLogger(__file__)


class IosUDIDView(View):

    def post(self, request, short):
        stream_f = str(request.body)
        format_udid_info = udid_bytes_to_dict(stream_f)
        logger.info("short %s get new udid %s" % (short, format_udid_info))
        server_domain = get_redirect_server_domain(request)
        if True:
            app_info = Apps.objects.filter(short=short).first()
            if app_info:
                server_domain = get_redirect_server_domain(request, app_info.user_id, get_app_domain_name(app_info))
                if app_info.issupersign and app_info.user_id.supersign_active:
                    res = check_app_permission(app_info, BaseResponse())
                    if res.code != 1000:
                        msg = "&msg=%s" % res.msg
                    else:
                        c_task = run_sign_task.apply_async((format_udid_info, short))
                        task_id = c_task.id
                        logger.info("sign app %s task_id:%s" % (app_info, task_id))
                        try:
                            result = c_task.get(propagate=False, timeout=2)
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
        # except Exception as e:
        #     logger.error("short %s receive udid Exception:%s" % (short, e))

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
                logger.info("app %s sign task state %s  AA %s" % (app_info, result.state, result.successful()))
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
