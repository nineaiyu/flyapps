from django.core.cache import cache
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from api.models import Token, UserInfo
from fir_ser.settings import CACHE_KEY_TEMPLATE
import base64

class ExpiringTokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        if request.method == "OPTIONS":
            return None
        request_token = request.META.get("HTTP_AUTHORIZATION", request.query_params.get("token", None))
        try:
            format_token = base64.b64decode(request_token).decode()
            auth_token = format_token.split(":")[0]
            user_name = format_token.split(":")[1]

        except Exception:
            raise AuthenticationFailed({"code": 1001, "error": "token不合法"})

        if not auth_token:
            raise AuthenticationFailed({"code": 1001, "error": "缺少token"})

        auth_key = "_".join([CACHE_KEY_TEMPLATE.get('user_auth_token_key'), auth_token])

        cacheuserinfo = cache.get(auth_key)
        if not cacheuserinfo:
            raise AuthenticationFailed({"code": 1001, "error": "无效的token"})
        if user_name != cacheuserinfo.get('username',None):
            raise AuthenticationFailed({"code": 1001, "error": "token校验失败"})

        user_obj = UserInfo.objects.filter(uid=cacheuserinfo.get('uid',None),username=cacheuserinfo.get("username")).first()
        # token_obj = Token.objects.filter(access_token=auth_token).first()
        if not user_obj:
            raise AuthenticationFailed({"code": 1001, "error": "无效的token"})
        if user_obj.is_active:
            cache.set(auth_key, cacheuserinfo, 3600 * 24 * 7)
            return user_obj,auth_token
        else:
            raise AuthenticationFailed({"code": 1001, "error": "用户被禁用"})

