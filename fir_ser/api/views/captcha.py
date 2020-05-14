from rest_framework.views import APIView
from api.utils.geetest import GeeTestLib
from django.conf import settings
import json
from rest_framework.response import Response


class CaptchaView(APIView):
    def get(self, request):
        gt = GeeTestLib(settings.GEE_TEST["gee_test_access_id"], settings.GEE_TEST["gee_test_access_key"])
        gt.pre_process()
        # 设置 geetest session, 用于是否启用滑动验证码向 geetest 发起远程验证, 如果取不到的话只是对本地轨迹进行校验
        # self.request.session[gt.GT_STATUS_SESSION_KEY] = status
        # request.session["user_id"] = user_id
        response_str = gt.get_response_str()
        response_str = json.loads(response_str)

        return Response({"error_no": 0, "data": response_str})


from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
import json


class AjaxExampleForm(APIView):

    def get(self, request):
        to_json_response = dict()
        to_json_response['status'] = 0
        to_json_response['new_cptch_key'] = CaptchaStore.generate_key()
        to_json_response['new_cptch_image'] = captcha_image_url(to_json_response['new_cptch_key'])
        CaptchaStore.remove_expired()
        a = CaptchaStore.objects.filter(hashkey=to_json_response['new_cptch_key']).first()
        print(a)
        return Response(to_json_response)
