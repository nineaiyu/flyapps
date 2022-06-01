#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: fir_ser
# filename: getip
# author: liuyu
# date: 2022/3/28

import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from common.base.baseutils import get_real_ip_address

logger = logging.getLogger(__name__)


class GetRemoteIp(APIView):

    def get(self, request):
        logger.info(f"real_ip:{get_real_ip_address(request)}")
        return Response({'real_ip': get_real_ip_address(request)})
