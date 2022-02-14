import logging

from django.contrib import auth
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Token
from common.cache.storage import RedisCacheBase
from common.core.auth import ExpiringTokenAuthentication

logger = logging.getLogger(__name__)


class LogoutView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]

    def delete(self, request):
        logger.info(f"user:{request.user} logout")
        user = request.user.pk
        auth_token = request.auth
        RedisCacheBase(auth_token).del_storage_cache()
        Token.objects.filter(user=user, access_token=auth_token).delete()
        auth.logout(request)
        return Response({"code": 1000})
