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
from django.urls import path,re_path,include

from api.views.login import LoginView,UserInfoView
from api.views.logout import LogoutView
from api.views.captcha import CaptchaView
from api.views.apps import AppsView,AppinfoView,AppReleaseinfoView
from api.views.localuploads import UploadView,UploadImgView
from api.views.download import DownloadTokenView
from api.views.qiniuuploads import QiNiuUploadView


# router=DefaultRouter()
# router.register("apps", AppsView)

urlpatterns = [
    # path("",include(router.urls)),
    re_path("^login",LoginView.as_view()),
    re_path("^logout",LogoutView.as_view()),
    re_path("^captcha_check/",CaptchaView.as_view()),
    re_path("^apps$", AppsView.as_view()),
    re_path("^apps/(?P<app_id>\w+)", AppinfoView.as_view()),
    re_path("^appinfos/(?P<app_id>\w+)/(?P<act>\w+)", AppReleaseinfoView.as_view()),
    re_path("^upload$",UploadView.as_view()),
    re_path("^img/upload$",UploadImgView.as_view()),
    re_path("^userinfo",UserInfoView.as_view()),
    re_path("^download_token/(?P<short>\w+)$", DownloadTokenView.as_view()),
    re_path("^qiniuupload$", QiNiuUploadView.as_view()),
]
