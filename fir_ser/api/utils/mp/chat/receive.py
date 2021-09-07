#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 9月 
# author: NinEveN
# date: 2021/9/6

import xml.etree.ElementTree as ET


def parse_xml(web_data):
    if len(web_data) == 0:
        return None
    xml_data = ET.fromstring(web_data)
    msg_type = xml_data.find('MsgType').text

    if msg_type == 'event':
        event_type = xml_data.find('Event').text
        if event_type == 'CLICK':
            return Click(xml_data)
        elif event_type in ('subscribe', 'unsubscribe'):
            return Subscribe(xml_data)
        # elif event_type == 'VIEW':
        # return View(xml_data)
        # elif event_type == 'LOCATION':
        # return LocationEvent(xml_data)
        elif event_type == 'SCAN':
            return Scan(xml_data)

    elif msg_type == 'text':
        return TextMsg(xml_data)
    elif msg_type == 'image':
        return ImageMsg(xml_data)


class Msg(object):
    def __init__(self, xml_data):
        self.ToUserName = xml_data.find('ToUserName').text
        self.FromUserName = xml_data.find('FromUserName').text
        self.CreateTime = xml_data.find('CreateTime').text
        self.MsgType = xml_data.find('MsgType').text
        self.MsgId = xml_data.find('MsgId').text


class TextMsg(Msg):
    def __init__(self, xml_data):
        Msg.__init__(self, xml_data)
        self.Content = xml_data.find('Content').text.encode("utf-8")


class ImageMsg(Msg):
    def __init__(self, xml_data):
        Msg.__init__(self, xml_data)
        self.PicUrl = xml_data.find('PicUrl').text
        self.MediaId = xml_data.find('MediaId').text


class EventMsg(object):
    def __init__(self, xml_data):
        self.ToUserName = xml_data.find('ToUserName').text
        self.FromUserName = xml_data.find('FromUserName').text
        self.CreateTime = xml_data.find('CreateTime').text
        self.MsgType = xml_data.find('MsgType').text
        self.Event = xml_data.find('Event').text
        self.Eventkey = xml_data.find('EventKey').text
        self.Ticket = ''


class Click(EventMsg):
    def __init__(self, xml_data):
        EventMsg.__init__(self, xml_data)


class Scan(EventMsg):
    def __init__(self, xml_data):
        EventMsg.__init__(self, xml_data)
        self.Ticket = xml_data.find('Ticket').text


class Subscribe(EventMsg):
    def __init__(self, xml_data):
        EventMsg.__init__(self, xml_data)
        tick = xml_data.find('Ticket')
        if tick is None:
            self.Ticket = ''
        else:
            self.Ticket = tick.text
