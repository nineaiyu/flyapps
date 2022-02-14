#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4

import logging

from api.views.apps import AppsView, AppInfoView, AppReleaseInfoView
from common.core.auth import ApiTokenAuthentication

logger = logging.getLogger(__name__)


class CliAppsView(AppsView):
    authentication_classes = [ApiTokenAuthentication, ]


class CliAppInfoView(AppInfoView):
    authentication_classes = [ApiTokenAuthentication, ]


class CliAppReleaseInfoView(AppReleaseInfoView):
    authentication_classes = [ApiTokenAuthentication, ]
