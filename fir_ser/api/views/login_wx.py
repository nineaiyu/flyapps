import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import UserInfo, ThirdWeChatUserInfo
from api.utils.response import BaseResponse
from api.utils.serializer import UserInfoSerializer
from api.utils.utils import set_user_token
from common.base.baseutils import get_real_ip_address
from common.cache.storage import WxLoginBindCache
from common.core.auth import ExpiringTokenAuthentication
from common.core.sysconfig import Config
from common.core.throttle import VisitRegister1Throttle, VisitRegister2Throttle
from common.libs.mp.wechat import make_wx_login_qrcode, show_qrcode_url, WxWebLogin
from common.utils.caches import set_wx_ticket_login_info_cache, get_wx_ticket_login_info_cache
from common.utils.pending import get_pending_result

logger = logging.getLogger(__name__)


def wx_qr_code_response(ret, code, qr_info, ip_addr):
    if code:
        logger.info(f"微信登录码获取成功， {qr_info}")
        errmsg = qr_info.get('errmsg')
        if errmsg:
            ret.code = 1003
            ret.msg = "微信登录码获取失败，请稍后"
        else:
            ticket = qr_info.get('ticket')
            if ticket:
                set_wx_ticket_login_info_cache(ticket, {'ip_addr': ip_addr})
                ret.data = {'qr': show_qrcode_url(ticket), 'ticket': ticket}
    else:
        ret.code = 1003
        ret.msg = "微信登录码获取失败，请稍后"
    return Response(ret.dict)


class WeChatLoginView(APIView):
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]

    def get(self, request):
        ret = BaseResponse()
        if Config.LOGIN.get("login_type").get('third', '').get('wxp'):
            unique_key = request.query_params.get('unique_key')
            if unique_key:
                cache_obj = WxLoginBindCache(unique_key)
                cache_data = cache_obj.get_storage_cache()
                if cache_data:
                    code, qr_info = cache_data
                else:
                    code, qr_info = cache_data = make_wx_login_qrcode()
                    cache_obj.set_storage_cache(cache_data, qr_info.get('expire_seconds', 600))
                return wx_qr_code_response(ret, code, qr_info, get_real_ip_address(request))
        return Response(ret.dict)


class WeChatBindView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]

    def post(self, request):
        ret = BaseResponse()
        uid = request.user.uid
        unique_key = request.data.get('unique_key')
        if unique_key:
            cache_obj = WxLoginBindCache(unique_key)
            cache_data = cache_obj.get_storage_cache()
            if cache_data:
                code, qr_info = cache_data
            else:
                code, qr_info = cache_data = make_wx_login_qrcode(f"web.bind.{uid}")
                cache_obj.set_storage_cache(cache_data, qr_info.get('expire_seconds', 600))
            return wx_qr_code_response(ret, code, qr_info, get_real_ip_address(request))
        return Response(ret.dict)


def expect_func(result, *args, **kwargs):
    return result and result.get('pk')


class WeChatLoginCheckView(APIView):
    def post(self, request):
        ret = BaseResponse()
        if not Config.LOGIN.get("login_type").get('third', '').get('wxp'):
            return Response(ret.dict)
        ticket = request.data.get("ticket")
        unique_key = request.data.get("unique_key", ticket)
        if ticket and unique_key:
            status, result = get_pending_result(get_wx_ticket_login_info_cache, expect_func, ticket=ticket,
                                                locker_key=ticket, unique_key=unique_key, run_func_count=1)
            if status:
                if result.get('err_msg'):
                    ret.msg = result.get('err_msg')
                    ret.code = 1004
                    return Response(ret.dict)
                wx_ticket_data = result.get('data', {})
                if wx_ticket_data.get('pk', -1) == -1:
                    ret.msg = "还未绑定用户，请通过手机或者邮箱登录账户之后进行绑定"
                    ret.code = 1005
                else:
                    user = UserInfo.objects.filter(pk=wx_ticket_data['pk']).first()
                    if user.is_active:
                        key, user_info = set_user_token(user, request)
                        serializer = UserInfoSerializer(user_info)
                        data = serializer.data
                        ret.msg = "验证成功!"
                        ret.userinfo = data
                        ret.token = key
                    else:
                        ret.msg = "用户被禁用"
                        ret.code = 1005
            else:
                ret.code = 1006
        else:
            ret.code = 1006
        return Response(ret.dict)


class WeChatWebLoginView(APIView):
    throttle_classes = [VisitRegister1Throttle, VisitRegister2Throttle]

    def get(self, request):
        logger.error(request.query_params)
        wx_login_obj = WxWebLogin()
        ret = BaseResponse()
        code = request.query_params.get('code')
        if code:
            wx_login_obj.get_wx_token(code)
            wx_user_info = wx_login_obj.get_user_info()
            logger.info(f'{wx_user_info}')
            wx_user_info = {
                'openid': wx_user_info.get('openid'),
                'nickname': wx_user_info.get('nickname'),
                'sex': wx_user_info.get('sex'),
                'subscribe_time': wx_user_info.get('subscribe_time', 0),
                'head_img_url': wx_user_info.get('headimgurl', ''),
                'address': f"{wx_user_info.get('country')}-{wx_user_info.get('province')}-{wx_user_info.get('city')}",
                'subscribe': wx_user_info.get('subscribe', 0),
            }
            logger.info(f'{wx_user_info}')
            ThirdWeChatUserInfo.objects.filter(openid=wx_user_info.get('openid')).update(**wx_user_info)
            return Response('更新成功')
        ret.data = wx_login_obj.make_auth_uri()
        return Response(ret.dict)
