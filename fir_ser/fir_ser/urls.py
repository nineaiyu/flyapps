"""fir_ser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path, include
from django.views.static import serve

from admin.views.celery_flower import CeleryFlowerView
from api.views.download import DownloadView, InstallView
from fir_ser import settings
from xsign.views.download import XsignDownloadView
from xsign.views.receiveudids import IosUDIDView, ShowUdidView

urlpatterns = [
    re_path('fly.admin/', admin.site.urls),
    re_path("api/v1/fir/server/", include('api.urls')),
    re_path("api/v1/fir/xsign/", include('xsign.urls')),
    re_path(r"xdownload/(?P<filename>\w+\.\w+)$", XsignDownloadView.as_view(), name="xdownload"),
    re_path("api/v2/fir/server/", include('cli.urls')),
    re_path("api/v3/fir/server/", include('admin.urls')),
    re_path('^captcha/', include('captcha.urls')),
    # media路径配置
    re_path('files/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r"download/(?P<filename>\w+\.\w+)$", DownloadView.as_view(), name="download"),
    re_path(r"install/(?P<app_id>\w+)$", InstallView.as_view(), name="install"),
    re_path(r"^udid/(?P<short>\w+)$", IosUDIDView.as_view()),
    re_path("^show_udid$", ShowUdidView.as_view()),
    re_path(r'flower/(?P<path>.*)', CeleryFlowerView.as_view()),
]
