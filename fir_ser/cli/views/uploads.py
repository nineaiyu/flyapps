#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6


from api.views.uploads import AppAnalyseView, UploadView
from common.core.auth import ApiTokenAuthentication


class CliAppAnalyseView(AppAnalyseView):
    authentication_classes = [ApiTokenAuthentication, ]


class CliUploadView(UploadView):
    authentication_classes = [ApiTokenAuthentication, ]
