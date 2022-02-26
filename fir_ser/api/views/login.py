import logging

from django.contrib import auth
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import UserInfo, UserCertificationInfo, CertificationInfo, Apps
from api.utils.auth.util import AuthInfo
from api.utils.modelutils import get_min_default_domain_cname_obj, add_remote_info_from_request
from api.utils.response import BaseResponse
from api.utils.serializer import UserInfoSerializer, CertificationSerializer, UserCertificationSerializer
from api.utils.utils import get_random_username, check_username_exists, set_user_token, clean_user_token_and_cache
from common.base.baseutils import is_valid_phone, is_valid_email
from common.core.auth import ExpiringTokenAuthentication
from common.core.sysconfig import Config
from common.core.throttle import VisitRegister1Throttle, VisitRegister2Throttle, GetAuthC1Throttle, GetAuthC2Throttle
from common.utils.caches import login_auth_failed, new_user_download_times_gift
from common.utils.sendmsg import get_sender_sms_token, is_valid_sender_code, get_sender_email_token

logger = logging.getLogger(__name__)


def get_login_type():
    return Config.LOGIN.get("login_type")


def get_register_type():
    return Config.REGISTER.get("register_type")


def reset_user_pwd(user, sure_password, old_password=''):
    if user is not None:
        user.set_password(sure_password)
    user.save(update_fields=["password"])
    logger.info(f"user:{user} change password success,old {old_password} new {sure_password}")
    clean_user_token_and_cache(user)


def get_authenticate(target, password, act, allow_type):
    user_obj = None
    if act == 'email' and allow_type[act]:
        if is_valid_email(target):
            user_obj = UserInfo.objects.filter(email=target).values('username').first()
    elif act == 'sms' and allow_type[act]:
        if is_valid_phone(target):
            user_obj = UserInfo.objects.filter(mobile=target).values('username').first()
    elif act == 'up' and allow_type[act]:
        user_obj = auth.authenticate(username=target, password=password)

    if user_obj and act in ['email', 'sms']:
        user_obj = auth.authenticate(username=user_obj['username'], password=password)

    return user_obj


def check_register_userinfo(target, act, key, ftype=None):
    res = BaseResponse()
    res.data = {}
    times_key = "%s_%s_%s" % (key, act, target)

    if key == "register":
        if not get_register_type()[act]:
            res.code = 1002
            res.msg = "暂不允许该类型注册"
            return res

    if act == "sms":
        if is_valid_phone(target):
            if login_auth_failed("get", times_key):
                login_auth_failed("set", times_key)
                if UserInfo.objects.filter(mobile=target) and ftype is None:
                    res.code = 1005
                    res.msg = "手机号已经存在"
                else:
                    token, code = get_sender_sms_token(act, target, 'register')
                    if token:
                        res.data["auth_token"] = token
                    else:
                        res.code = 1009
                        res.msg = "短信服务异常，请联系管理员"
            else:
                res.code = 1009
                res.msg = "该手机号今日使用次数已经达到上限"
        else:
            res.code = 1005
            res.msg = "手机号校验失败"

    elif act == "email":
        if is_valid_email(target):
            if login_auth_failed("get", times_key):
                login_auth_failed("set", times_key)
                if UserInfo.objects.filter(email=target) and ftype is None:
                    res.code = 1005
                    res.msg = "邮箱已经存在"
                else:
                    token, code = get_sender_email_token(act, target, 'register')
                    if token:
                        res.data["auth_token"] = token
                    else:
                        res.code = 1009
                        res.msg = "邮件服务异常，请联系管理员"
            else:
                res.code = 1009
                res.msg = "该邮箱今日注册次数已经达到上限"
        else:
            res.code = 1006
            res.msg = "邮箱校验失败"
    elif act == "up":
        if login_auth_failed("get", times_key):
            login_auth_failed("set", times_key)
            if UserInfo.objects.filter(username=target) and ftype is None:
                res.code = 1005
                res.msg = "用户名已经存在"
            else:
                token, code = get_sender_email_token(act, target, 'register')
                if token:
                    res.data["auth_token"] = token
                else:
                    res.code = 1009
                    res.msg = "未知错误"
        else:
            res.code = 1009
            res.msg = "用户名已经存在"

    else:
        res.code = 1007
        res.msg = "信息发送失败"
    return res


def check_change_userinfo(target, act, key, user, ftype=None):
    res = BaseResponse()
    res.data = {}

    if key == "change":
        if not get_login_type()[act]:
            res.code = 1002
            res.msg = "暂不允许该类型修改"
            return res
    times_key = "%s_%s_%s" % (user.uid, act, target)
    if act == "sms":
        if is_valid_phone(target) and str(user.mobile) != str(target):
            if login_auth_failed("get", times_key):
                login_auth_failed("set", times_key)
                if UserInfo.objects.filter(mobile=target) and ftype is None:
                    res.code = 1005
                    res.msg = "手机号已经存在"
                else:
                    token, code = get_sender_sms_token(act, target, 'change')
                    if token:
                        res.data["auth_token"] = token
                    else:
                        res.code = 1009
                        res.msg = "短信服务异常，请联系管理员"
            else:
                res.code = 1009
                res.msg = "该手机号今日使用次数已经达到上限"
        else:
            res.code = 1005
            res.msg = "手机号校验失败"

    elif act == "email":
        if is_valid_email(target) and str(user.email) != str(target):
            if login_auth_failed("get", times_key):
                login_auth_failed("set", times_key)
                if UserInfo.objects.filter(email=target) and ftype is None:
                    res.code = 1005
                    res.msg = "邮箱已经存在"
                else:
                    token, code = get_sender_email_token(act, target, 'change')
                    if token:
                        res.data["auth_token"] = token
                    else:
                        res.code = 1009
                        res.msg = "邮件服务异常，请联系管理员"
            else:
                res.code = 1009
                res.msg = "该邮箱今日使用次数已经达到上限"
        else:
            res.code = 1006
            res.msg = "邮箱校验失败"
    elif act == "up":
        if login_auth_failed("get", times_key):
            login_auth_failed("set", times_key)
            if UserInfo.objects.filter(username=target) and ftype is None:
                res.code = 1005
                res.msg = "用户名已经存在"
            else:
                token, code = get_sender_email_token(act, target, 'change')
                res.data["auth_token"] = token
        else:
            res.code = 1009
            res.msg = "用户名已经存在"

    else:
        res.code = 1007
        res.msg = "信息发送失败"
    return res


def check_common_info(target, act):
    res = BaseResponse()
    res.data = {}

    times_key = "%s_%s_%s" % ('report', act, target)
    if act == "sms":
        if is_valid_phone(target):
            if login_auth_failed("get", times_key):
                login_auth_failed("set", times_key)
                token, code = get_sender_sms_token(act, target, 'common')
                if token:
                    res.data["auth_token"] = token
                else:
                    res.code = 1009
                    res.msg = "短信服务异常，请联系管理员"
            else:
                res.code = 1009
                res.msg = "该手机号今日使用次数已经达到上限"
        else:
            res.code = 1005
            res.msg = "手机号校验失败"
    elif act == "email":
        if is_valid_email(target):
            if login_auth_failed("get", times_key):
                login_auth_failed("set", times_key)
                token, code = get_sender_email_token(act, target, 'common')
                if token:
                    res.data["auth_token"] = token
                else:
                    res.code = 1009
                    res.msg = "邮件服务异常，请联系管理员"
            else:
                res.code = 1009
                res.msg = "该邮箱今日使用次数已经达到上限"
        else:
            res.code = 1006
            res.msg = "邮箱校验失败"
    else:
        res.code = 1007
        res.msg = "信息发送失败"
    return res


class LoginView(APIView):
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]

    def post(self, request):
        response = BaseResponse()
        receive = request.data
        username = receive.get("username", None)
        auth_obj = AuthInfo(Config.LOGIN.get("captcha"), Config.LOGIN.get("geetest"))
        is_valid, msg = auth_obj.valid(receive)
        if not is_valid or username is None:
            response.code = 1001
            response.msg = msg
            return Response(response.dict)

        login_type = receive.get("login_type", None)
        seicode = receive.get("seicode", None)
        if login_auth_failed("get", username):
            if login_type == 'reset':
                user1_obj = None
                user2_obj = None
                act = None
                if is_valid_email(username):
                    user1_obj = UserInfo.objects.filter(email=username).first()
                    act = "email"

                if is_valid_phone(username):
                    user2_obj = UserInfo.objects.filter(mobile=username).first()
                    act = "sms"

                if user1_obj or user2_obj:
                    user_obj = user1_obj if user1_obj else user2_obj
                    password = get_random_username()[:16]

                    if login_auth_failed("get", user_obj.uid):
                        login_auth_failed("set", user_obj.uid)

                        if seicode:
                            is_valid, target = is_valid_sender_code(act, receive.get("auth_token", None), seicode)
                            if is_valid and str(target) == str(username):
                                if user2_obj:
                                    a, b = get_sender_sms_token('sms', username, 'password', password)
                                else:
                                    a, b = get_sender_email_token('email', username, 'password', password)
                                if a and b:
                                    reset_user_pwd(user_obj, password)
                                    login_auth_failed("del", username)
                                    msg = f'{user_obj} 找回密码成功，您的新密码为 {password} 请用新密码登录之后，及时修改密码'
                                    add_remote_info_from_request(request, msg)
                                    logger.warning(f'{user_obj} 找回密码成功，您的新密码为 {password} 请用新密码登录之后，及时修改密码')
                                else:
                                    response.code = 1007
                                    response.msg = "密码重置失败，请稍后重试或者联系管理员"
                            else:
                                response.code = 1009
                                response.msg = "验证码有误，请检查或者重新尝试"

                        else:
                            res = check_register_userinfo(username, act, 'change', 'reset')
                            return Response(res.dict)

                    else:
                        response.code = 1008
                        response.msg = "手机或者邮箱已经超过最大发送，请24小时后重试"
                else:
                    response.code = 1002
                    response.msg = "邮箱或者手机号不存在"
                return Response(response.dict)

            password = receive.get("password")
            user = get_authenticate(username, password, login_type, get_login_type())
            logger.info(f"username:{username}  password:{password}")
            if user:
                if user.is_active:
                    login_auth_failed("del", username)
                    # update the token
                    key, user_info = set_user_token(user, request)
                    serializer = UserInfoSerializer(user_info, )
                    data = serializer.data
                    response.msg = "验证成功!"
                    response.userinfo = data
                    response.token = key
                    add_remote_info_from_request(request, f"登录成功， token: {key}")
                else:
                    response.msg = "用户被禁用"
                    response.code = 1005
            else:
                login_auth_failed("set", username)
                #
                # try:
                #     UserInfo.objects.get(username=username)
                response.msg = "密码账户有误或用户被禁用"
                response.code = 1002
                # except UserInfo.DoesNotExist:
                #     response.msg = "用户不存在!"
                #     response.code = 1003
        else:
            response.code = 1006
            logger.error(f"username:{username} failed too try , locked")
            response.msg = "用户登录失败次数过多，已被锁定，请1小时之后再次尝试"
        add_remote_info_from_request(request, response.msg)
        return Response(response.dict)

    def get(self, request):
        response = BaseResponse()
        response.data = {}
        auth_obj = AuthInfo(Config.LOGIN.get("captcha"), Config.LOGIN.get("geetest"))
        response.data['auth_rules'] = auth_obj.make_rules_info()
        response.data['login_type'] = get_login_type()
        allow_f = Config.REGISTER.get("enable")
        response.data['register_enable'] = allow_f
        return Response(response.dict)

    def put(self, request):
        response = BaseResponse()
        user_id = request.data.get('user_id', None)
        if user_id:
            auth_obj = AuthInfo(Config.LOGIN.get("captcha"), Config.LOGIN.get("geetest"))
            response.data = auth_obj.make_geetest_info(user_id, request.META.get('REMOTE_ADDR'))
        else:
            response.code = 1002
            response.msg = '参数错误'
        return Response(response.dict)


class RegistView(APIView):
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]

    def post(self, request):
        response = BaseResponse()
        receive = request.data

        username = receive.get("username", None)

        if is_valid_email(username):
            act = 'email'
        elif is_valid_phone(username):
            act = 'sms'
        else:
            response.code = 1001
            response.msg = "邮箱或手机校验有误"
            return Response(response.dict)

        if not get_register_type()[act]:
            response.code = 1002
            response.msg = "不允许该类型注册"
            return Response(response.dict)

        auth_obj = AuthInfo(Config.REGISTER.get("captcha"), Config.REGISTER.get("geetest"))
        is_valid, msg = auth_obj.valid(request.data)
        if not is_valid:
            response.code = 1001
            response.msg = msg
            return Response(response.dict)

        is_valid, target = is_valid_sender_code(act, receive.get("auth_token", None), receive.get("auth_key", None))
        if is_valid and str(target) == str(username):
            if login_auth_failed("get", username):
                password = receive.get("password")
                password2 = receive.get("password2")
                if password == password2:
                    random_username = get_random_username()
                    new_data = {
                        "username": random_username,
                        "password": password,
                        "first_name": random_username[:8],
                        "default_domain_name": get_min_default_domain_cname_obj(True)
                    }
                    if is_valid_email(username):

                        user_obj = UserInfo.objects.create_user(**new_data, email=username)
                    elif is_valid_phone(username):
                        user_obj = UserInfo.objects.create_user(**new_data, mobile=username)
                    else:
                        user_obj = None
                        response.msg = "注册异常"
                        response.code = 1000
                    if user_obj:
                        try:
                            new_user_download_times_gift(user_obj, Config.NEW_USER_GIVE_DOWNLOAD_TIMES)
                        except Exception as e:
                            logger.error(f"用户{user_obj}赠送下载次数失败{e}")
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
        add_remote_info_from_request(request, response.msg)
        return Response(response.dict)

    def get(self, request):
        response = BaseResponse()
        response.data = {}
        allow_f = Config.REGISTER.get("enable")
        if allow_f:
            auth_obj = AuthInfo(Config.REGISTER.get("captcha"), Config.REGISTER.get("geetest"))
            response.data['auth_rules'] = auth_obj.make_rules_info()
            response.data['register_type'] = get_register_type()
        response.data['enable'] = allow_f
        return Response(response.dict)


class UserInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        serializer = UserInfoSerializer(request.user)
        res.data = serializer.data
        del res.data['username']
        res.data['login_type'] = get_login_type()
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        logger.info(f"user:{request.user} update old data:{request.user.__dict__}")
        logger.info(f"user:{request.user} update new data:{data}")

        old_password = data.get("oldpassword", None)
        sure_password = data.get("surepassword", None)

        mobile = data.get("mobile", None)
        email = data.get("email", None)
        if mobile or email:

            auth_obj = AuthInfo(Config.CHANGER.get("captcha"), False)
            is_valid, msg = auth_obj.valid(data)
            if not is_valid:
                res.code = 1001
                res.msg = msg
                return Response(res.dict)

        if old_password and sure_password:
            user = auth.authenticate(username=request.user.username, password=old_password)
            if user is not None:
                user.set_password(sure_password)
                user.save(update_fields=['password'])
                res.msg = "密码修改成功"
                logger.info(f"user:{request.user} change password success,old {old_password} new {sure_password}")

                auth_token = request.auth
                clean_user_token_and_cache(user, [auth_token])

                return Response(res.dict)
            else:
                res.code = 1004
                res.msg = "老密码校验失败"
        else:
            update_fields = []
            if get_login_type().get('up'):
                username = data.get("username", None)
                if username and username != request.user.username:
                    if check_username_exists(username):
                        res.msg = "用户名已经存在"
                        res.code = 1005
                        logger.error(f"User {request.user} info save failed. username already exists")
                        return Response(res.dict)
                    if len(username) < 6:
                        res.msg = "用户名至少6位"
                        res.code = 1006
                        return Response(res.dict)
                request.user.username = data.get("username", request.user.username)
                update_fields.append("username")
            request.user.job = data.get("job", request.user.job)
            request.user.first_name = data.get("first_name", request.user.first_name)
            update_fields.extend(["job", "first_name"])
            sms_token = data.get("auth_token", None)
            if sms_token:
                act = data.get("act", None)
                status, target = is_valid_sender_code(act, data.get("auth_token", None), data.get("auth_key", None))
                if status:

                    if act == 'sms' and mobile:
                        if str(target) == str(mobile):
                            if is_valid_phone(mobile):
                                request.user.mobile = data.get("mobile", request.user.mobile)
                                update_fields.append("mobile")
                        else:
                            res.code = 1005
                            res.msg = "手机号异常"
                    elif act == 'email' and email:
                        if str(target) == str(email):
                            if is_valid_email(email):
                                request.user.email = data.get("email", request.user.email)
                                update_fields.append("email")
                        else:
                            res.code = 1005
                            res.msg = "邮箱异常"
                    if res.code != 1000:
                        return Response(res.dict)
                else:
                    res.code = 1005
                    res.msg = "验证码校验失败"
                    return Response(res.dict)

            try:
                request.user.save(update_fields=update_fields)
            except Exception as e:
                serializer = UserInfoSerializer(request.user)
                res.data = serializer.data
                res.code = 1004
                res.msg = "信息保存失败"
                logger.error(f"User {request.user} info save failed. Exception:{e}")
                return Response(res.dict)
            serializer = UserInfoSerializer(request.user)
            res.data = serializer.data
            return Response(res.dict)

        return Response(res.dict)


class AuthorizationView(APIView):
    throttle_classes = [GetAuthC1Throttle, GetAuthC2Throttle]

    def post(self, request):
        res = BaseResponse()
        res.data = {}
        act = request.data.get("act", None)
        target = request.data.get("target", None)
        ext = request.data.get("ext", None)
        register_type = get_register_type()
        if ext and register_type.get('code', None) and ext.get('icode', None):
            if ext.get('icode') == '689888666':
                pass
            else:
                res.code = 1008
                res.msg = "邀请码已失效"
                return Response(res.dict)
        if ext and ext.get('report'):
            p_data = Config.REPORT
        else:
            p_data = Config.REGISTER

        auth_obj = AuthInfo(p_data.get("captcha"), p_data.get("geetest"))
        auth_data = {'geetest': request.data.get("geetest", None)}
        auth_data.update(ext)
        is_valid, msg = auth_obj.valid(auth_data)
        if not is_valid:
            res.code = 1001
            res.msg = msg
            return Response(res.dict)
        if ext and ext.get('report'):
            app_obj = Apps.objects.filter(app_id=ext.get('report')).first()
            if app_obj:
                res = check_common_info(target, act)
            else:
                res.code = 1003
                res.msg = '未授权，请重新提交'
            return Response(res.dict)

        res = check_register_userinfo(target, act, 'register')

        return Response(res.dict)


class ChangeAuthorizationView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    throttle_classes = [GetAuthC1Throttle, GetAuthC2Throttle]

    def post(self, request):
        res = BaseResponse()
        res.data = {}
        act = request.data.get("act", None)
        target = request.data.get("target", None)
        ext = request.data.get("ext", None)
        f_type = request.data.get("ftype", None)

        auth_obj = AuthInfo(Config.REGISTER.get("captcha"), Config.REGISTER.get("geetest"))
        auth_data = {'geetest': request.data.get("geetest", None)}
        auth_data.update(ext)
        is_valid, msg = auth_obj.valid(auth_data)
        if not is_valid or target is None:
            res.code = 1001
            res.msg = msg
            return Response(res.dict)

        res = check_change_userinfo(target, act, 'change', request.user, f_type)
        return Response(res.dict)


class UserApiTokenView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        res.data = {
            'token': request.user.api_token
        }
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data

        old_token = data.get("token", None)
        if old_token == request.user.api_token:
            request.user.api_token = 'reset'
        try:
            request.user.save(update_fields=["api_token"])
        except Exception as e:
            logger.error(f"User {request.user} api_token save failed. Exception:{e}")
            res.code = 1002
            res.msg = "token 生成失败"
            return Response(res.dict)
        return self.get(request)


class CertificationView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        res.data = {}
        act = request.query_params.get("act", "")
        user_certification_obj = UserCertificationInfo.objects.filter(user_id=request.user).first()
        if user_certification_obj and user_certification_obj.status == 1 or act == "usercert":
            card = user_certification_obj.card
            res.data["usercert"] = {
                'name': user_certification_obj.name,
                'addr': user_certification_obj.addr,
                'card': "%s%s%s" % (card[:4], '*' * (len(card) - 8), card[-4:]),
                'mobile': user_certification_obj.mobile,
                'status': user_certification_obj.status,
                'msg': user_certification_obj.msg,
            }
            return Response(res.dict)

        if 'certinfo' in act:
            if user_certification_obj:
                user_certification_serializer = UserCertificationSerializer(user_certification_obj)
                res.data["user_certification"] = user_certification_serializer.data
        if 'certpic' in act:
            certification_obj = CertificationInfo.objects.filter(user_id=request.user).all()
            if certification_obj:
                certification_serializer = CertificationSerializer(certification_obj, many=True)
                res.data["certification"] = certification_serializer.data
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data

        user_certification_obj = UserCertificationInfo.objects.filter(user_id=request.user).first()
        if user_certification_obj and user_certification_obj.status == 1:
            return Response(res.dict)

        try:
            auth_obj = AuthInfo(Config.CHANGER.get("captcha"), False)
            is_valid, msg = auth_obj.valid(data)
            if not is_valid or not data.get("mobile"):
                res.code = 1001
                res.msg = msg
                return Response(res.dict)
            del data["captcha_key"]
            del data["verify_code"]
            if Config.CHANGER.get('change_type').get('sms'):
                is_valid, target = is_valid_sender_code('sms', data.get("auth_token", None), data.get("auth_key", None))
                if is_valid and str(target) == str(data.get("mobile")):
                    if login_auth_failed("get", str(data.get("mobile"))):
                        del data["auth_key"]
                        del data["auth_token"]
                        data['status'] = 0

                        if CertificationInfo.objects.filter(user_id=request.user).count() == 3:
                            UserCertificationInfo.objects.update_or_create(defaults=data, user_id=request.user)
                            return self.get(request)
                        else:
                            res.code = 1009
                            res.msg = "请上传照片"
                            return Response(res.dict)
                    else:
                        res.code = 1006
                        logger.error(f"username:{request.user} failed too try , locked")
                        res.msg = "用户注册失败次数过多，已被锁定，请1小时之后再次尝试"
                else:
                    res.code = 1001
                    res.msg = "短信验证码有误"
            else:
                data['status'] = 0
                if CertificationInfo.objects.filter(user_id=request.user).count() == 3:
                    UserCertificationInfo.objects.update_or_create(defaults=data, user_id=request.user)
                else:
                    res.code = 1009
                    res.msg = "请上传照片"
                    return Response(res.dict)
                return self.get(request)
        except Exception as e:
            logger.error(f"{request.user} UserCertificationInfo save {data} failed Exception: {e}")
            res.msg = "数据异常，或身份证已经被绑定，请检查"
            res.code = 1002
        return Response(res.dict)


class ChangeInfoView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        response = BaseResponse()
        response.data = {}
        allow_f = Config.CHANGER.get("enable")
        if allow_f:
            auth_obj = AuthInfo(Config.CHANGER.get("captcha"), Config.CHANGER.get("geetest"))
            response.data['auth_rules'] = auth_obj.make_rules_info()
            response.data['change_type'] = Config.CHANGER.get("change_type")
        response.data['enable'] = allow_f
        return Response(response.dict)
