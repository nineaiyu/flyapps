#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 9月 
# author: NinEveN
# date: 2021/9/6

import time


class Msg(object):
    def __init__(self):
        pass

    def send(self):
        return "success"


class TextMsg(Msg):
    def __init__(self, to_user_name, from_user_name, content):
        super().__init__()
        self.__dict = dict()
        self.__dict['ToUserName'] = to_user_name
        self.__dict['FromUserName'] = from_user_name
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['Content'] = content

    def send(self):
        xml_form = """
            <xml>
                <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
                <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
                <CreateTime>{CreateTime}</CreateTime>
                <MsgType><![CDATA[text]]></MsgType>
                <Content><![CDATA[{Content}]]></Content>
            </xml>
            """
        return xml_form.format(**self.__dict)


class ImageMsg(Msg):
    def __init__(self, to_user_name, from_user_name, media_id):
        super().__init__()
        self.__dict = dict()
        self.__dict['ToUserName'] = to_user_name
        self.__dict['FromUserName'] = from_user_name
        self.__dict['CreateTime'] = int(time.time())
        self.__dict['MediaId'] = media_id

    def send(self):
        xml_form = """
            <xml>
                <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
                <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
                <CreateTime>{CreateTime}</CreateTime>
                <MsgType><![CDATA[image]]></MsgType>
                <Image>
                <MediaId><![CDATA[{MediaId}]]></MediaId>
                </Image>
            </xml>
            """
        return xml_form.format(**self.__dict)
