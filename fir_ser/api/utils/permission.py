

from django.core.cache import cache

import datetime

from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from api.models import Token

from rest_framework.permissions import BasePermission

class LoginUserPermission(BaseAuthentication):

    def has_permission(self,request,view):

        if request.user:
            return True
        else:
            return False

