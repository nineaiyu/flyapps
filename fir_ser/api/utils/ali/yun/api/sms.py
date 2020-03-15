#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/9/18

"""
    短信服务
"""

from .base import BaseAliYunAPI


class AliYunSms(BaseAliYunAPI):

    VERSION = "2017-05-25"

    API_BASE_URL = "http://dysmsapi.aliyuncs.com/"

    def send(self, phone_numbers, sign_name, template_code, template_param, **kwargs):
        """发送短信

        详情参见：
        https://help.aliyun.com/document_detail/55284.html?spm=5176.8195934.1001856.3.a36a4183xdfqaD

        Parameters
        ----------
        phone_numbers : string
            短信接收号码,支持以逗号分隔的形式进行批量调用，批量上限为1000个手机号码.
            发送国际/港澳台消息时，接收号码格式为00+国际区号+号码，如“0085200000000”

        sign_name: string
            短信签名

        template_code: string
            短信模板ID，发送国际/港澳台消息时，请使用国际/港澳台短信模版

        template_param: json
            短信模板变量替换JSON串,友情提示:如果JSON中需要带换行符,请参照标准的JSON协议

        kwargs: dict
            可选字段：

                SmsUpExtendCode
                    上行短信扩展码,无特殊需要此字段的用户请忽略此字段

                OutId
                    外部流水扩展字段

        Returns
        -------
        dict
        """

        data = {
            "PhoneNumbers": phone_numbers,
            "SignName": sign_name,
            "TemplateCode": template_code,
            "TemplateParam": template_param
        }

        data.update(**kwargs)

        return self._get(action="SendSms", data=data)

    def send_batch(
        self,
        phone_number_json,
        sign_name_json,
        template_code,
        template_param_json,
        sms_upextend_code_json=None,
    ):
        """短信批量发送

        详情参见：
        https://help.aliyun.com/document_detail/66041.html?spm=a2c4g.11186623.6.565.290415e8yJ7E0N

        Parameters
        ----------
        phone_number_json : string
            短信接收号码,JSON格式,批量上限为100个手机号码,
            批量调用相对于单条调用及时性稍有延迟,验证码类型的短信推荐使用单条调用的方式

        sign_name_json: string
            短信签名,JSON格式

        template_code: int
            短信模板ID

        template_param_json: int
            短信模板变量替换JSON串,友情提示:如果JSON中需要带换行符,请参照标准的JSON协议。

        sms_upextend_code_json: string
            上行短信扩展码,JSON格式，无特殊需要此字段的用户请忽略此字段

        """
        data = {
            "PhoneNumberJson": phone_number_json,
            "SignNameJson": sign_name_json,
            "TemplateCode": template_code,
            "TemplateParamJson": template_param_json
        }

        if sms_upextend_code_json is not None:
            data["SmsUpExtendCodeJson"] = sms_upextend_code_json

        return self._get(action="SendBatchSms", data=data)

    def query(self, phone_number, send_date, page_size, current_page, biz_id=None):
        """短信查询

        详情参见：
        https://help.aliyun.com/document_detail/55289.html?spm=a2c4g.11186623.6.563.56d7577756pHT4

        Parameters
        ----------
        phone_number : string
            短信接收号码,如果需要查询国际短信,号码前需要带上对应国家的区号,区号的获取详见国际短信支持国家信息查询API接口

        send_date: string
            短信发送日期格式yyyyMMdd,支持最近30天记录查询

        page_size: int
            页大小Max=50

        current_page: int
            当前页码

        biz_id: string OR None
            可选, 发送流水号,从调用发送接口返回值中获取

        Returns
        -------
        dict
        """
        data = {
            "PhoneNumber": phone_number,
            "SendDate": send_date,
            "PageSize": page_size,
            "CurrentPage": current_page
        }

        if biz_id is not None:
            data["BizId"] = biz_id

        return self._get(action="QuerySendDetails", data=data)
