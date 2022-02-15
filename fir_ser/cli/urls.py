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
from django.urls import re_path

from cli.views.apps import CliAppsView, CliAppInfoView, CliAppReleaseInfoView
from cli.views.login import CliUserInfoView
from cli.views.uploads import CliAppAnalyseView, CliUploadView

urlpatterns = [
    re_path("^apps$", CliAppsView.as_view()),
    re_path(r"^apps/(?P<app_id>\w+)", CliAppInfoView.as_view()),
    re_path(r"^appinfos/(?P<app_id>\w+)/(?P<act>\w+)", CliAppReleaseInfoView.as_view()),
    re_path("^upload$", CliUploadView.as_view()),
    re_path("^userinfo", CliUserInfoView.as_view()),
    re_path("^analyse$", CliAppAnalyseView.as_view()),
]
