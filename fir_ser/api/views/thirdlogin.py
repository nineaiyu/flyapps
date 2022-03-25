#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/29
import logging
import random

from django.http.response import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_xml.parsers import XMLParser

from api.models import ThirdWeChatUserInfo, UserInfo, UserCertificationInfo
from api.utils.modelutils import PageNumber
from api.utils.response import BaseResponse
from api.utils.serializer import ThirdWxSerializer
from api.views.login import get_login_type
from common.core.auth import ExpiringTokenAuthentication
from common.libs.mp.chat import reply, receive
from common.libs.mp.wechat import check_signature, WxMsgCrypt, get_userinfo_from_openid, WxTemplateMsg
from common.utils.caches import set_wx_ticket_login_info_cache, get_wx_ticket_login_info_cache
from config import WEB_DOMAIN

logger = logging.getLogger(__name__)

GOOD_XX = [
    '您是一位有恒心有毅力的人，我很佩服您！',
    '越有内涵的人越虚怀若谷，像您这样有内涵的人我十分敬佩！',
    '你像天上的月亮，也像那闪烁的星星，可惜我不是诗人，否则，当写一万首诗来形容你的美丽！',
    '据考证，你是世界上最大的宝藏，里面藏满了金子、钻石和名画！',
    '虽然你没有一簇樱唇两排贝齿，但你的谈吐高雅脱俗，机智过人，令我折服！',
    '您是一位有恒心有毅力的人，我很佩服您！',
    '我很荣幸，认识你这样有内涵的漂亮朋友！',
    '春花秋月，是诗人们歌颂的情景，可是我对于它，却感到十分平凡。只有你嵌着梨涡的笑容，才是我眼中最美的景象！',
    '你像一片轻柔的云在我眼前飘来飘去，你清丽秀雅的脸上荡漾着春天般美丽的笑容。在你那双又大又亮的眼睛里，我总能捕捉到你的宁静，你的热烈，你的聪颖，你的敏感！',
    '人生旅程上，您丰富我的心灵，开发我得智力，为我点燃了希望的光芒，谢谢您！',
]


class TextXMLParser(XMLParser):
    media_type = 'text/xml'  # 微信解析的是 text/xml


def reply_login_msg(rec_msg, to_user, from_user, ):
    content = f'还未绑定用户，请通过手机或者邮箱登录账户之后进行绑定'
    u_data_id = -1
    wx_user_obj = ThirdWeChatUserInfo.objects.filter(openid=to_user).first()

    wx_ticket_info = get_wx_ticket_login_info_cache(rec_msg.Ticket)

    if wx_user_obj:
        u_data_id = wx_user_obj.user_id.pk
        content = f'用户 {wx_user_obj.user_id.first_name} 登录成功'
        WxTemplateMsg(to_user, wx_user_obj.nickname).login_success_msg(wx_user_obj.user_id.first_name)
    else:
        wx_user_info = update_or_create_wx_userinfo(to_user, None, False)
        WxTemplateMsg(to_user, wx_user_info.get('nickname', '')).login_failed_msg()

    if wx_ticket_info and wx_ticket_info.get('ip_addr'):
        ip_addr = wx_ticket_info.get('ip_addr')
        logger.info(f"{content} ip:{ip_addr}")

    set_wx_ticket_login_info_cache(rec_msg.Ticket, {'pk': u_data_id})
    reply_msg = reply.TextMsg(to_user, from_user, content)
    return reply_msg.send()


def update_or_create_wx_userinfo(to_user, user_obj, create=True):
    code, wx_user_info = get_userinfo_from_openid(to_user)
    logger.info(f"get openid:{to_user} info:{to_user} code:{code}")
    if code:
        wx_user_info = {
            'openid': wx_user_info.get('openid'),
            'nickname': wx_user_info.get('nickname'),  # 最新微信接口已经取消该字段
            'sex': wx_user_info.get('sex'),  # 最新微信接口已经取消该字段
            'subscribe_time': wx_user_info.get('subscribe_time'),
            'head_img_url': wx_user_info.get('headimgurl'),  # 最新微信接口已经取消该字段
            'address': f"{wx_user_info.get('country')}-{wx_user_info.get('province')}-{wx_user_info.get('city')}",
            'subscribe': wx_user_info.get('subscribe'),
        }
    if create:
        ThirdWeChatUserInfo.objects.update_or_create(user_id=user_obj, openid=to_user, defaults=wx_user_info)
    return wx_user_info


def wx_bind_utils(rec_msg, to_user, from_user, content):
    uid = rec_msg.Eventkey.split('.')[-1]
    wx_user_obj = ThirdWeChatUserInfo.objects.filter(openid=to_user).first()
    user_obj = UserInfo.objects.filter(uid=uid).first()
    if wx_user_obj:
        wx_template_msg_obj = WxTemplateMsg(to_user, wx_user_obj.nickname)
        if user_obj and user_obj.uid == wx_user_obj.user_id.uid:
            content = f'账户 {wx_user_obj.user_id.first_name} 已经绑定成功，感谢您的使用'
            update_or_create_wx_userinfo(to_user, user_obj)
            wx_template_msg_obj.bind_success_msg(user_obj.first_name)
        else:
            content = f'账户已经被 {wx_user_obj.user_id.first_name} 绑定'
            wx_template_msg_obj.bind_failed_msg(content)
    else:
        if user_obj:
            wx_user_info = update_or_create_wx_userinfo(to_user, user_obj)
            content = f'账户绑定 {user_obj.first_name} 成功'
            WxTemplateMsg(to_user, wx_user_info.get('nickname', '')).bind_success_msg(user_obj.first_name)
    if user_obj:
        set_wx_ticket_login_info_cache(rec_msg.Ticket, {'pk': user_obj.pk})
    reply_msg = reply.TextMsg(to_user, from_user, content)
    return reply_msg.send()


class ValidWxChatToken(APIView):
    parser_classes = (XMLParser, TextXMLParser)

    def get(self, request):
        params = request.query_params
        return HttpResponse(check_signature(params))

    def post(self, request):
        params = request.query_params
        data = request.data
        encrypt_obj = WxMsgCrypt()
        ret, encrypt_xml = encrypt_obj.decrypt_msg(data, params.get("msg_signature"), params.get("timestamp"),
                                                   params.get("nonce"))
        logger.info(f"code:{ret}, result {encrypt_xml}")
        result = "success"
        if ret == 0:
            content = '欢迎使用fly应用分发平台，感谢您的关注'
            rec_msg = receive.parse_xml(encrypt_xml)
            if isinstance(rec_msg, receive.Msg):
                to_user = rec_msg.FromUserName
                from_user = rec_msg.ToUserName

                if rec_msg.MsgType == 'text':
                    content = random.choices([*GOOD_XX, content, rec_msg.Content.decode('utf-8')])[0]
                    reply_msg = reply.TextMsg(to_user, from_user, content)
                    result = reply_msg.send()

                elif rec_msg.MsgType == 'image':
                    media_id = rec_msg.MediaId
                    reply_msg = reply.ImageMsg(to_user, from_user, media_id)
                    result = reply_msg.send()
                else:
                    result = reply.Msg().send()
                logger.info(f"replay msg: {result}")
                return HttpResponse(result)
            elif isinstance(rec_msg, receive.EventMsg):
                to_user = rec_msg.FromUserName
                from_user = rec_msg.ToUserName
                if rec_msg.Event == 'CLICK':  # 公众号点击事件
                    if rec_msg.Eventkey == 'good':
                        content = random.choices(GOOD_XX)[0]
                        reply_msg = reply.TextMsg(to_user, from_user, content)
                        result = reply_msg.send()
                        logger.info(f"replay msg: {result}")
                        return HttpResponse(result)
                    elif rec_msg.Eventkey == 'flyapps':
                        reply_msg = reply.TextMsg(to_user, from_user, WEB_DOMAIN)
                        result = reply_msg.send()
                        logger.info(f"replay msg: {result}")
                        return HttpResponse(result)
                    elif rec_msg.Eventkey in ['query_bind', 'unbind']:
                        wx_user_obj = ThirdWeChatUserInfo.objects.filter(openid=to_user).first()
                        if rec_msg.Eventkey == 'query_bind':
                            if wx_user_obj:
                                user_obj = wx_user_obj.user_id
                                content = f'绑定用户 {user_obj.first_name} '
                                if user_obj.email:
                                    content += f' 登录邮箱：{user_obj.email} '
                                if user_obj.mobile:
                                    content += f' 登录手机：{user_obj.mobile}'
                                user_cert_obj = UserCertificationInfo.objects.filter(user_id=user_obj,
                                                                                     status=1).first()
                                if user_cert_obj:
                                    name = user_cert_obj.name
                                else:
                                    name = user_obj.first_name
                                WxTemplateMsg(to_user, wx_user_obj.nickname).bind_query_success_msg(user_obj.first_name,
                                                                                                    name,
                                                                                                    user_obj.mobile,
                                                                                                    user_obj.email)
                            else:
                                content = '暂无登录绑定信息'
                                wx_user_info = update_or_create_wx_userinfo(to_user, None, False)
                                WxTemplateMsg(to_user, wx_user_info.get('nickname')).query_bind_info_failed_msg(
                                    "查询登录绑定", content)

                        elif rec_msg.Eventkey == 'unbind':
                            if wx_user_obj:
                                content = f'解绑用户 {wx_user_obj.user_id.first_name} 成功'
                                WxTemplateMsg(to_user, wx_user_obj.nickname).unbind_success_msg(
                                    wx_user_obj.user_id.first_name)
                                ThirdWeChatUserInfo.objects.filter(openid=to_user).delete()
                            else:
                                content = f'暂无登录绑定信息'
                                wx_user_info = update_or_create_wx_userinfo(to_user, None, False)
                                WxTemplateMsg(to_user, wx_user_info.get('nickname')).query_bind_info_failed_msg(
                                    "解除登录绑定", content)

                        logger.info(f"to_user:{to_user} from_user:{from_user} reply msg: {content}")
                        reply_msg = reply.TextMsg(to_user, from_user, content)
                        result = reply_msg.send()

                elif rec_msg.Event in ['subscribe', 'unsubscribe']:  # 订阅
                    reply_msg = reply.TextMsg(to_user, from_user, content)
                    result = reply_msg.send()
                    if rec_msg.Event == 'subscribe':
                        if rec_msg.Eventkey == 'qrscene_web.login':  # 首次关注，登录认证操作
                            result = reply_login_msg(rec_msg, to_user, from_user)
                        elif rec_msg.Eventkey.startswith('qrscene_web.bind.'):
                            result = wx_bind_utils(rec_msg, to_user, from_user, content)
                    if rec_msg.Event == 'unsubscribe':
                        ThirdWeChatUserInfo.objects.filter(openid=to_user).update(subscribe=False)

                elif rec_msg.Event == 'SCAN':
                    if rec_msg.Eventkey == 'web.login':  # 已经关注，然后再次扫码，登录认证操作
                        result = reply_login_msg(rec_msg, to_user, from_user, )
                    elif rec_msg.Eventkey.startswith('web.bind.'):
                        result = wx_bind_utils(rec_msg, to_user, from_user, content)
        else:
            logger.error('密文解密失败')
        logger.info(f"replay msg: {result}")
        return HttpResponse("success")


class ThirdWxAccount(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()
        if get_login_type().get('third', '').get('wxp'):
            wx_obj_lists = ThirdWeChatUserInfo.objects.filter(user_id=request.user)
            page_obj = PageNumber()
            info_serializer = page_obj.paginate_queryset(queryset=wx_obj_lists.order_by("-subscribe_time"),
                                                         request=request,
                                                         view=self)
            wx_user_info = ThirdWxSerializer(info_serializer, many=True, )
            res.data = wx_user_info.data
            res.count = wx_obj_lists.count()
        return Response(res.dict)

    def post(self, request):
        data = request.data
        openid = data.get("openid")
        if get_login_type().get('third', '').get('wxp') and openid:
            if request.user.check_password(data.get('confirm_pwd', '')):
                ThirdWeChatUserInfo.objects.filter(user_id=request.user, openid=openid).delete()
            else:
                res = BaseResponse()
                res.code = 1001
                res.msg = "密码有误，请检查"
                return Response(res.dict)
        return self.get(request)
