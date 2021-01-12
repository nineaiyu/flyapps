#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6


from api.utils.auth import ApiTokenAuthentication
from api.views.uploads import AppAnalyseView, UploadView


class CliAppAnalyseView(AppAnalyseView):
    authentication_classes = [ApiTokenAuthentication, ]


class CliUploadView(UploadView):
    authentication_classes = [ApiTokenAuthentication, ]
