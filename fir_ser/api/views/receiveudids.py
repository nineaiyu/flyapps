#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6

from api.utils.app.supersignutils import udid_bytes_to_dict, get_redirect_server_domain, IosUtils
from api.models import Apps
from django.views import View
from django.http import HttpResponsePermanentRedirect
import logging

logger = logging.getLogger(__file__)


class IosUDIDView(View):

    def post(self, request, short):
        stream_f = str(request.body)
        format_udid_info = udid_bytes_to_dict(stream_f)
        logger.info("short %s get new udid %s" % (short, format_udid_info))
        server_domain = get_redirect_server_domain(request)
        msg = {}
        status = True
        try:
            app_info = Apps.objects.filter(short=short).first()

            if app_info:
                if app_info.issupersign and app_info.user_id.supersign_active:
                    ios_obj = IosUtils(format_udid_info, app_info.user_id, app_info)
                    status, msg = ios_obj.sign()
                else:
                    return HttpResponsePermanentRedirect(
                        "%s/%s" % (server_domain, short))
            else:
                return HttpResponsePermanentRedirect(
                    "%s/%s" % (server_domain, short))
        except Exception as e:
            logger.error("short %s receive udid Exception:%s" % (short, e))

        if not status:
            code = msg.get("code")
            if code == 0:
                msg = ""
            elif code == 1001:
                msg = "账户余额不足"
            elif code == 1002:
                msg = "维护中"
            elif code == 1003:
                msg = "应用余额不足"
            else:
                msg = "内部错误，请联系管理员"
        else:
            msg = ""
        return HttpResponsePermanentRedirect(
            "%s/%s?udid=%s&msg=%s" % (server_domain, short, format_udid_info.get("udid"), msg))
