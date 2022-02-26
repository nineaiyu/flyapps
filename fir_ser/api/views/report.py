#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 11月 
# author: NinEveN
# date: 2021/11/4
import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Apps, AppReportInfo
from api.utils.auth.util import AuthInfo
from api.utils.modelutils import add_remote_info_from_request
from api.utils.response import BaseResponse
from api.utils.serializer import AppReportSerializer
from common.base.baseutils import get_real_ip_address, get_choices_dict
from common.core.sysconfig import Config
from common.core.throttle import InstallThrottle2
from common.utils.caches import login_auth_failed
from common.utils.sendmsg import is_valid_sender_code

logger = logging.getLogger(__name__)


class ReportView(APIView):
    throttle_classes = [InstallThrottle2]

    def get(self, request):
        response = BaseResponse()
        response.data = {}
        allow_f = Config.REPORT.get("enable")
        if allow_f:
            auth_obj = AuthInfo(Config.REPORT.get("captcha"), Config.REPORT.get("geetest"))
            response.data['auth_rules'] = auth_obj.make_rules_info()
            response.data['report_type'] = Config.REPORT.get("report_type")
            response.data['s_list'] = get_choices_dict(AppReportInfo.report_type_choices)
        response.data['enable'] = allow_f
        return Response(response.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        msg = f"add new app report data:{data}"
        logger.info(msg)
        email = data.get('email', '')
        is_valid, target = is_valid_sender_code(data.get('act'), data.get("auth_token", None),
                                                data.get("seicode", None), True)
        if is_valid and str(target) == str(email):
            if login_auth_failed("get", email):
                add_remote_info_from_request(request, msg)
                if data.get('app_id'):
                    app_obj = Apps.objects.filter(app_id=data.get('app_id')).first()
                    ext_info = {
                        'app_name': app_obj.name,
                        'bundle_id': app_obj.bundle_id,
                        'remote_addr': get_real_ip_address(request),
                        'app_id': app_obj.pk
                    }
                    data.update(ext_info)
                    serializer = AppReportSerializer(data=data, context={'user_obj': request.user})
                    if serializer.is_valid():
                        serializer.save()
                    else:
                        logger.info(f"add new app report failed")
                        res.msg = serializer.errors
                        res.code = 1005
            else:
                res.code = 1006
                logger.error("email:%s failed too try , locked" % (email,))
                res.msg = "失败次数过多，已被锁定，请1小时之后再次尝试"
        else:
            res.code = 1001
            res.msg = "验证码有误或失效"

        return Response(res.dict)
