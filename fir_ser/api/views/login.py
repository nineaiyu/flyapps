from django.contrib import auth
from api.models import Token, UserInfo, Apps
from rest_framework.response import Response
from api.utils.serializer import UserInfoSerializer
from django.core.cache import cache
from rest_framework.views import APIView
import binascii
import os, datetime, json
from api.utils.utils import get_captcha, valid_captcha, is_valid_domain, is_valid_phone, \
    get_sender_sms_token, is_valid_email, is_valid_sender_code, get_sender_email_token
from api.utils.auth import ExpiringTokenAuthentication
from api.utils.response import BaseResponse
from django.middleware import csrf
from fir_ser.settings import CACHE_KEY_TEMPLATE, SERVER_DOMAIN, REGISTER
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


class RegistView(APIView):
    def generate_key(self):
        return binascii.hexlify(os.urandom(32)).decode()

    def post(self, request):
        response = BaseResponse()
        receive = request.data

        username = receive.get("username", None)
        act = 'sms'
        if is_valid_email(username):
            act = 'email'
        is_valid, target = is_valid_sender_code(act, receive.get("auth_token", None), receive.get("auth_key", None))
        if is_valid and str(target) == str(username):
            if login_auth_failed("get", username):
                password = receive.get("password")
                password2 = receive.get("password2")
                if password == password2:
                    try:
                        UserInfo.objects.get(username=username)
                        login_auth_failed("set", username)
                        response.msg = "邮箱已经存在，请更换其他邮箱"
                        response.code = 1002
                    except UserInfo.DoesNotExist:
                        if is_valid_email(username):

                            user_obj = UserInfo.objects.create_user(username, email=username, password=password,
                                                                    first_name=username[:8])
                        else:
                            user_obj = UserInfo.objects.create_user(username, mobile=username, password=password,
                                                                    first_name=username[:8])
                        if user_obj:
                            response.msg = "注册成功"
                            response.code = 1000
                else:
                    response.code = 1001
                    response.msg = "密码不一致"
            else:
                response.code = 1006
                logger.error("username:%s failed too try , locked" % (username,))
                response.msg = "用户注册失败次数过多，已被锁定，请1小时之后再次尝试"
        else:
            response.code = 1001
            response.msg = "邮件或短信验证码有误"

        return Response(response.dict)

    def get(self, request):
        response = BaseResponse()
        response.data = {}
        allow_f = REGISTER.get("enable")
        if allow_f:
            response.data = get_captcha()
            response.data['ways'] = REGISTER.get("ways")
        response.data['enable'] = allow_f
        return Response(response.dict)


class UserInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        serializer = UserInfoSerializer(request.user)
        res.data = serializer.data

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
                domain_name_list = domain_name.strip(' ').replace("http://", "").replace("https://", "").split("/")
                if len(domain_name_list) > 0:
                    domain_name = domain_name_list[0]
                    if len(domain_name) > 3 and is_valid_domain(domain_name_list[0]):
                        if domain_name == SERVER_DOMAIN.get("REDIRECT_UDID_DOMAIN").split("//")[1]:
                            admin_storage = UserInfo.objects.filter(is_superuser=True).order_by('pk').first()
                            if admin_storage and admin_storage.uid == request.user.uid:
                                request.user.domain_name = domain_name
                                set_default_app_wx_easy(request.user)
                            else:
                                serializer = UserInfoSerializer(request.user)
                                res.data = serializer.data
                                res.code = 1004
                                res.msg = "域名设置失败，请更换其他域名"
                                return Response(res.dict)
                        else:
                            request.user.domain_name = domain_name
                            set_default_app_wx_easy(request.user)
                    else:
                        serializer = UserInfoSerializer(request.user)
                        res.data = serializer.data
                        res.code = 1004
                        res.msg = "域名校验失败"
                        return Response(res.dict)

            if domain_name == '':
                request.user.domain_name = None
                Apps.objects.filter(user_id=request.user).update(wxeasytype=True)
                set_default_app_wx_easy(request.user)

            request.user.job = data.get("job", request.user.job)
            request.user.first_name = data.get("first_name", request.user.first_name)

            sms_token = data.get("auth_token", None)
            if sms_token:
                status, target = is_valid_sender_code(request.user.uid, sms_token, data.get("sms_code", None))
                mobile = data.get("mobile", request.user.mobile)
                if target == mobile:
                    if is_valid_phone(mobile):
                        request.user.mobile = data.get("mobile", request.user.mobile)
                else:
                    res.code = 1005
                    res.msg = "手机号异常"
                    return Response(res.dict)
            else:
                res.code = 1005
                res.msg = "手机号校验失败"
                return Response(res.dict)

            try:
                request.user.save()
            except Exception as e:
                serializer = UserInfoSerializer(request.user)
                res.data = serializer.data
                res.code = 1004
                res.msg = "信息保存失败"
                logger.error("User %s info save failed. Excepiton:%s" % (request.user, e))
                return Response(res.dict)
            serializer = UserInfoSerializer(request.user)
            res.data = serializer.data
            return Response(res.dict)

        return Response(res.dict)


class AuthorizationView(APIView):

    def get(self, request):
        res = BaseResponse()
        res.data = {}
        act = request.query_params.get("act", None)
        target = request.query_params.get("target", None)
        ext = request.query_params.get("ext", None)
        if ext:
            ext = json.loads(ext)
        ways = REGISTER.get("ways")
        if ways.get('code') and ext and ext.get('icode'):
            if ext.get('icode') == '689888666':
                pass
            else:
                res.code = 1008
                res.msg = "邀请码已失效"
                return Response(res.dict)

        if ext and valid_captcha(ext.get("cptch_key", None), ext.get("authcode", None), target):
            pass
        else:
            res.code = 1008
            res.msg = "图片验证码有误"
            return Response(res.dict)

        times_key = "register_%s_%s" % (act, target)
        if act == "sms":
            if is_valid_phone(target):
                if login_auth_failed("get", times_key):
                    login_auth_failed("set", times_key)
                    if UserInfo.objects.filter(mobile=target):
                        res.code = 1005
                        res.msg = "手机号已经存在"
                    else:
                        token, code = get_sender_sms_token(act, target)
                        res.data["auth_token"] = token
                else:
                    res.code = 1009
                    res.msg = "该手机号今日注册次数已经达到上限"
            else:
                res.code = 1005
                res.msg = "手机号校验失败"

        elif act == "email":
            if is_valid_email(target):
                if login_auth_failed("get", times_key):
                    login_auth_failed("set", times_key)
                    if UserInfo.objects.filter(email=target):
                        res.code = 1005
                        res.msg = "邮箱已经存在"
                    else:
                        token, code = get_sender_email_token(act, target)
                        res.data["auth_token"] = token
                else:
                    res.code = 1009
                    res.msg = "该邮箱今日注册次数已经达到上限"
            else:
                res.code = 1006
                res.msg = "邮箱校验失败"
        elif act == "ways":

            if ways['sms']:
                pass
            elif ways['email']:
                pass

            elif ways['code']:
                pass
            else:
                pass

        else:
            res.code = 1007
            res.msg = "信息发送失败"
        return Response(res.dict)


class AuthorizationViewbak(APIView):
    # authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        res.data = {}
        act = request.query_params.get("act", None)
        target = request.query_params.get("target", None)
        ext = request.query_params.get("ext", None)
        ways = REGISTER.get("ways")
        if ways.get('code') and ext:
            if ext == '689888666':
                pass
            else:
                res.code = 1008
                res.msg = "邀请码已失效"
                return Response(res.dict)

        if act == "sms":
            if is_valid_phone(target) and str(request.user.mobile) != str(target):
                token, code = get_sender_sms_token(request.user.uid, target)
                res.data["auth_token"] = token
            else:
                res.code = 1005
                res.msg = "手机号校验失败"

        elif act == "email":
            if is_valid_email(target) and str(request.user.email) != str(target):
                token, code = get_sender_email_token(request.user.uid, target)
                res.data["auth_token"] = token
            else:
                res.code = 1006
                res.msg = "邮箱校验失败"
        elif act == "ways":

            if ways['sms']:
                pass
            elif ways['email']:
                pass

            elif ways['code']:
                pass
            else:
                pass

        else:
            res.code = 1007
            res.msg = "信息发送失败"
        return Response(res.dict)
