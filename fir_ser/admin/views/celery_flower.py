# -*- coding: utf-8 -*-
#
from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from proxy.views import proxy_view
from rest_framework.views import APIView

from api.utils.auth import AdminTokenAuthentication

flower_url = f'{settings.CELERY_FLOWER_HOST}:{settings.CELERY_FLOWER_PORT}'


class CeleryFlowerView(APIView):
    authentication_classes = [AdminTokenAuthentication, ]

    def get(self, request, path):
        remote_url = 'http://{}/flower/{}'.format(flower_url, path)
        try:
            response = proxy_view(request, remote_url)
        except Exception as e:
            msg = _("<h1>Flower service unavailable, check it</h1>") + \
                  '<br><br> <div>{}</div>'.format(e)
            response = HttpResponse(msg)
        return response

    def post(self, request, path):
        return self.get(request, path)
