from rest_framework.views import APIView
from api.utils.auth import ExpiringTokenAuthentication
from api.models import Token
from django.core.cache import cache
from rest_framework.response import Response

from api.utils.permission import LoginUserPermission


class LogoutView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [LoginUserPermission]

    def delete(self, request):
        user = request.user.pk
        auth_token = request.auth
        cache.delete(auth_token)
        Token.objects.filter(user=user,access_token=auth_token).delete()
        return Response({"code": 1000})
