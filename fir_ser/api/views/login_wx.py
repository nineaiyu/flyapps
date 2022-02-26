import logging

from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import UserInfo, ThirdWeChatUserInfo
from api.utils.response import BaseResponse
from api.utils.serializer import UserInfoSerializer
from api.utils.utils import set_user_token
from common.base.baseutils import get_real_ip_address
from common.base.magic import get_pending_result
from common.core.auth import ExpiringTokenAuthentication
from common.core.sysconfig import Config
from common.core.throttle import VisitRegister1Throttle, VisitRegister2Throttle
from common.libs.mp.wechat import make_wx_login_qrcode, show_qrcode_url, WxWebLogin
from common.utils.caches import set_wx_ticket_login_info_cache, get_wx_ticket_login_info_cache

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
            code, qr_info = make_wx_login_qrcode()
            return wx_qr_code_response(ret, code, qr_info, get_real_ip_address(request))
        return Response(ret.dict)


class WeChatBindView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def post(self, request):
        ret = BaseResponse()
        uid = request.user.uid
        code, qr_info = make_wx_login_qrcode(f"web.bind.{uid}")
        return wx_qr_code_response(ret, code, qr_info, get_real_ip_address(request))


def expect_func(result, *args, **kwargs):
    return result and result.get('pk')


class WeChatLoginCheckView(APIView):
    def post(self, request):
        ret = BaseResponse()
        if not Config.LOGIN.get("login_type").get('third', '').get('wxp'):
            return Response(ret.dict)
        ticket = request.data.get("ticket")
        if ticket:
            status, wx_ticket_data = get_pending_result(get_wx_ticket_login_info_cache, expect_func, ticket=ticket,
                                                        locker_key=ticket)
            if status:
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
