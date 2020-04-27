#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/6

from api.utils.app.supersignutils import udid_bytes_to_dict,get_redirect_server_domain,IosUtils
from api.models import Apps,AppUDID
from django.views import View
from django.http import HttpResponsePermanentRedirect,Http404

class IosUDIDView(View):

    def post(self,request,short):
        stream_f = str(request.body)
        format_udid_info = udid_bytes_to_dict(stream_f)
        try:
            app_info=Apps.objects.filter(short=short).first()

            if app_info :
                if app_info.issupersign:
                    AppUDID.objects.update_or_create(app_id=app_info,**format_udid_info,defaults={'udid':format_udid_info.get('udid')})
                    ios_obj = IosUtils(format_udid_info,app_info.user_id,app_info)
                    ios_obj.resign()
                else:
                    return Http404
            else:
                return Http404

        except Exception as e:
            print(e)
        server_domain = get_redirect_server_domain(request)
        return HttpResponsePermanentRedirect("%s/%s?udid=%s"%(server_domain,short,format_udid_info.get("udid")))


