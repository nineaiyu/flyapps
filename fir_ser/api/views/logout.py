from rest_framework.views import APIView
from api.utils.auth import ExpiringTokenAuthentication
from api.models import Token
from rest_framework.response import Response

from api.utils.permission import LoginUserPermission


class LogoutView(APIView):
    authentication_classes = [ExpiringTokenAuthentication]
    permission_classes = [LoginUserPermission]

    def delete(self, request):
        user = request.user.pk
        Token.objects.filter(user=user).delete()
        return Response({"code": 1000})
