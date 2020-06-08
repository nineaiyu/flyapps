from django.contrib import auth
from api.models import Token, UserInfo, Apps
from rest_framework.response import Response
from api.utils.serializer import UserInfoSerializer
from django.core.cache import cache
from rest_framework.views import APIView
import binascii
import os, datetime
from api.utils.utils import get_captcha, valid_captcha
from api.utils.TokenManager import DownloadToken, generateNumericTokenOfLength
from api.utils.auth import ExpiringTokenAuthentication
from api.utils.response import BaseResponse
from django.middleware import csrf
from fir_ser.settings import CACHE_KEY_TEMPLATE, SERVER_DOMAIN
from api.utils.storage.caches import login_auth_failed, set_default_app_wx_easy
import logging

logger = logging.getLogger(__name__)


def get_token(request):
    token = csrf.get_token(request)
    return {'csrf_token': token}


class LoginView(APIView):
    def generate_key(self):
        return binascii.hexlify(os.urandom(32)).decode()

    def post(self, request):
        response = BaseResponse()
        receive = request.data

        if request.method == 'POST':
            username = receive.get("username", None)
            is_valid = valid_captcha(receive.get("cptch_key", None), receive.get("authcode", None), username)
            if is_valid:
                if login_auth_failed("get", username):
                    password = receive.get("password")
                    user = auth.authenticate(username=username, password=password)
                    logger.info("username:%s  password:%s" % (username, password))
                    if user is not None:
                        if user.is_active:
                            login_auth_failed("del", username)
                            # update the token
                            key = self.generate_key()
                            now = datetime.datetime.now()
                            user_info = UserInfo.objects.get(pk=user.pk)

                            auth_key = "_".join([CACHE_KEY_TEMPLATE.get('user_auth_token_key'), key])
                            cache.set(auth_key, {'uid': user_info.uid, 'username': user_info.username}, 3600 * 24 * 7)
                            Token.objects.create(user=user, **{"access_token": key, "created": now})

                            serializer = UserInfoSerializer(user_info, )
                            data = serializer.data
                            response.msg = "验证成功!"
                            response.userinfo = data
                            response.token = key
                        else:
                            response.msg = "用户被禁用"
                            response.code = 1005
                    else:
                        login_auth_failed("set", username)
                        try:
                            UserInfo.objects.get(username=username)
                            response.msg = "密码或者账户有误"
                            response.code = 1002
                        except UserInfo.DoesNotExist:
                            response.msg = "用户不存在!"
                            response.code = 1003
                else:
                    response.code = 1006
                    logger.error("username:%s failed too try , locked" % (username,))
                    response.msg = "用户登录失败次数过多，已被锁定，请1小时之后再次尝试"
            else:
                response.code = 1001
                response.msg = "验证码有误"

            return Response(response.dict)

    def get(self, request):
        response = BaseResponse()
        response.data = get_captcha()
        return Response(response.dict)


class UserInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        serializer = UserInfoSerializer(request.user)
        res.data = serializer.data
        act = request.query_params.get("act", None)
        if act and act == "sms":
            sms_token_obj = DownloadToken()
            sms_code = generateNumericTokenOfLength(6)
            sms_token = sms_token_obj.make_token(sms_code)
            res.data["sms_token"] = sms_token
            res.data["sms_code"] = sms_code

        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        logger.info("user:%s update old data:%s" % (request.user, request.user.__dict__))
        logger.info("user:%s update new data:%s" % (request.user, data))

        oldpassword = data.get("oldpassword", None)
        surepassword = data.get("surepassword", None)

        if oldpassword and surepassword:
            user = auth.authenticate(username=request.user.username, password=oldpassword)
            if user is not None:
                user.set_password(surepassword)
                user.save()
                res.msg = "密码修改成功"
                logger.info("user:%s change password success,old %s new %s" % (request.user, oldpassword, surepassword))

                auth_token = request.auth
                for token_obj in Token.objects.filter(user=user):
                    if token_obj.access_token != auth_token:
                        cache.delete(token_obj.access_token)
                        token_obj.delete()

                return Response(res.dict)
            else:
                res.code = 1004
                res.msg = "老密码校验失败"
        else:
            # 修改个人资料
            domain_name = data.get("domain_name", None)
            if domain_name:
                domain_name_list = domain_name.strip(' ').strip("http://").strip("https://").split("/")
                if len(domain_name_list) > 1:
                    domain_name = domain_name_list[0]
                    if len(domain_name) > 3:
                        if domain_name == SERVER_DOMAIN.get("REDIRECT_UDID_DOMAIN").split("//")[1]:
                            serializer = UserInfoSerializer(request.user)
                            res.data = serializer.data
                            res.code = 1004
                            res.msg = "域名设置失败，请更换其他域名"
                            return Response(res.dict)
                        else:
                            request.user.domain_name = domain_name
                            set_default_app_wx_easy(request.user)

            if domain_name == '':
                request.user.domain_name = None
                Apps.objects.filter(user_id=request.user).update(wxeasytype=True)
                set_default_app_wx_easy(request.user)

            request.user.job = data.get("job", request.user.job)
            request.user.first_name = data.get("first_name", request.user.first_name)

            sms_token = data.get("sms_token", None)
            if sms_token:
                sms_token_obj = DownloadToken()
                if sms_token_obj.verify_token(sms_token, data.get("sms_code", None)):
                    request.user.mobile = data.get("mobile", request.user.mobile)
            request.user.save()
            serializer = UserInfoSerializer(request.user)
            res.data = serializer.data
            return Response(res.dict)

        return Response(res.dict)
