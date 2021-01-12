from django.contrib import auth
from api.models import Token, UserInfo, Apps
from rest_framework.response import Response
from api.utils.serializer import UserInfoSerializer
from django.core.cache import cache
from rest_framework.views import APIView
import binascii
import os, datetime, json
from api.utils.utils import get_captcha, valid_captcha, is_valid_domain, is_valid_phone, \
    get_sender_sms_token, is_valid_email, is_valid_sender_code, get_sender_email_token, get_random_username, \
    check_username_exists
from api.utils.auth import ApiTokenAuthentication
from api.utils.response import BaseResponse
from fir_ser.settings import CACHE_KEY_TEMPLATE, SERVER_DOMAIN, REGISTER, LOGIN
from api.utils.storage.caches import login_auth_failed, set_default_app_wx_easy
import logging

from api.views.login import UserInfoView

logger = logging.getLogger(__name__)


class CliUserInfoView(UserInfoView):
    authentication_classes = [ApiTokenAuthentication, ]

