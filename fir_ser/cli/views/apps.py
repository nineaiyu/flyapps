#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/4

from api.utils.auth import ApiTokenAuthentication
from api.views.apps import AppsView, AppInfoView, AppReleaseInfoView
import logging

logger = logging.getLogger(__name__)


class CliAppsView(AppsView):
    authentication_classes = [ApiTokenAuthentication, ]


class CliAppInfoView(AppInfoView):
    authentication_classes = [ApiTokenAuthentication, ]


class CliAppReleaseInfoView(AppReleaseInfoView):
    authentication_classes = [ApiTokenAuthentication, ]
