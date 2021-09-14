#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: NinEveN
# date: 2021/3/29
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import logging
import random
from rest_framework.views import APIView
from rest_framework_xml.parsers import XMLParser
from api.models import ThirdWeChatUserInfo, UserInfo
from api.utils.auth import ExpiringTokenAuthentication

from api.utils.mp.chat import reply, receive
from api.utils.mp.wechat import check_signature, WxMsgCrypt, get_userinfo_from_openid
from api.utils.response import BaseResponse
from api.utils.serializer import ThirdWxSerializer
from api.utils.storage.caches import set_wx_ticket_login_info_cache
from api.views.login import get_login_type

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
    if wx_user_obj:
        u_data_id = wx_user_obj.user_id.pk
        content = f'用户 {wx_user_obj.user_id.first_name} 登录成功'
    set_wx_ticket_login_info_cache(rec_msg.Ticket, u_data_id)
    reply_msg = reply.TextMsg(to_user, from_user, content)
    return reply_msg.send()


def update_or_create_wx_userinfo(to_user, user_obj):
    code, wx_user_info = get_userinfo_from_openid(to_user)
    logger.info(f"get openid:{to_user} info:{to_user} code:{code}")
    if code:
        wx_user_info = {
            'openid': wx_user_info.get('openid'),
            'nickname': wx_user_info.get('nickname'),
            'sex': wx_user_info.get('sex'),
            'subscribe_time': wx_user_info.get('subscribe_time'),
            'head_img_url': wx_user_info.get('headimgurl'),
            'address': f"{wx_user_info.get('country')}-{wx_user_info.get('province')}-{wx_user_info.get('city')}",
            'subscribe': wx_user_info.get('subscribe'),
        }
        ThirdWeChatUserInfo.objects.update_or_create(user_id=user_obj, openid=to_user, defaults=wx_user_info)


class ValidWxChatToken(APIView):
    parser_classes = (XMLParser, TextXMLParser)

    def get(self, request):
        params = request.query_params
        return Response(check_signature(params))

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

            elif isinstance(rec_msg, receive.EventMsg):
                to_user = rec_msg.FromUserName
                from_user = rec_msg.ToUserName
                if rec_msg.Event == 'CLICK':  # 公众号点击事件
                    if rec_msg.Eventkey == 'good':
                        content = random.choices(GOOD_XX)[0]
                        reply_msg = reply.TextMsg(to_user, from_user, content)
                        result = reply_msg.send()
                elif rec_msg.Event in ['subscribe', 'unsubscribe']:  # 订阅
                    reply_msg = reply.TextMsg(to_user, from_user, content)
                    result = reply_msg.send()
                    if rec_msg.Eventkey == 'qrscene_web.login':  # 首次关注，登录认证操作
                        if rec_msg.Event == 'subscribe':
                            result = reply_login_msg(rec_msg, to_user, from_user, )
                    if rec_msg.Event == 'unsubscribe':
                        ThirdWeChatUserInfo.objects.filter(openid=to_user).update(subscribe=False)

                elif rec_msg.Event == 'SCAN':
                    if rec_msg.Eventkey == 'web.login':  # 已经关注，然后再次扫码，登录认证操作
                        result = reply_login_msg(rec_msg, to_user, from_user, )
                    elif rec_msg.Eventkey.startswith('web.bind.'):
                        uid = rec_msg.Eventkey.split('.')[-1]
                        wx_user_obj = ThirdWeChatUserInfo.objects.filter(openid=to_user).first()
                        user_obj = UserInfo.objects.filter(uid=uid).first()
                        if wx_user_obj:
                            if user_obj and user_obj.uid == wx_user_obj.user_id.uid:
                                content = f'账户 {wx_user_obj.user_id.first_name} 已经绑定成功，感谢您的使用'
                                update_or_create_wx_userinfo(to_user, user_obj)
                            else:
                                content = f'账户已经被 {wx_user_obj.user_id.first_name} 绑定'
                        else:
                            update_or_create_wx_userinfo(to_user, user_obj)
                            content = f'账户绑定 {wx_user_obj.user_id.first_name} 成功'
                        set_wx_ticket_login_info_cache(rec_msg.Ticket, user_obj.pk)
                        reply_msg = reply.TextMsg(to_user, from_user, content)
                        result = reply_msg.send()

        else:
            logger.error('密文解密失败')

        return Response(result)


class PageNumber(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'size'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = None  # 最大页码数限制


class ThirdWxAccount(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get(self, request):
        res = BaseResponse()

        if get_login_type().get('third', '').get('wxp'):
            # wx_open_id = request.query_params.get("openid", None)
            wx_obj_lists = ThirdWeChatUserInfo.objects.filter(user_id=request.user)
            # if wx_open_id:
            #     wx_obj_lists = wx_obj_lists.filter(openid=wx_open_id)
            page_obj = PageNumber()
            info_serializer = page_obj.paginate_queryset(queryset=wx_obj_lists.order_by("-subscribe_time"),
                                                         request=request,
                                                         view=self)
            wx_user_info = ThirdWxSerializer(info_serializer, many=True, )
            res.data = wx_user_info.data
            res.count = wx_obj_lists.count()

        return Response(res.dict)

    def delete(self, request):
        openid = request.query_params.get("openid")
        user_id = request.query_params.get("user_id")
        if get_login_type().get('third', '').get('wxp') and openid and user_id:
            ThirdWeChatUserInfo.objects.filter(user_id_id=user_id, openid=openid).delete()
        return self.get(request)
