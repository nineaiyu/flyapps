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
from django.urls import path, re_path, include

from api.views.login import LoginView, UserInfoView
from api.views.logout import LogoutView
from api.views.captcha import AjaxExampleForm
from api.views.apps import AppsView, AppInfoView, AppReleaseinfoView
from api.views.download import ShortDownloadView
from api.views.uploads import AppAnalyseView, UploadView
from api.views.storage import StorageView
from api.views.receiveudids import IosUDIDView

from api.views.supersign import DeveloperView, SuperSignUsedView, AppUDIDUsedView

# router=DefaultRouter()
# router.register("apps", AppsView)

urlpatterns = [
    # path("",include(router.urls)),
    re_path("^login", LoginView.as_view()),
    re_path("^logout", LogoutView.as_view()),
    re_path("^captcha_check/", AjaxExampleForm.as_view()),
    re_path("^apps$", AppsView.as_view()),
    re_path("^storage$", StorageView.as_view()),
    re_path("^apps/(?P<app_id>\w+)", AppInfoView.as_view()),
    re_path("^appinfos/(?P<app_id>\w+)/(?P<act>\w+)", AppReleaseinfoView.as_view()),
    re_path("^upload$", UploadView.as_view()),
    re_path("^userinfo", UserInfoView.as_view()),
    re_path("^short/(?P<short>\w+)$", ShortDownloadView.as_view()),
    re_path("^udid/(?P<short>\w+)$", IosUDIDView.as_view()),
    re_path("^analyse$", AppAnalyseView.as_view()),
    re_path("^supersign/developer$", DeveloperView.as_view()),
    re_path("^supersign/devices$", SuperSignUsedView.as_view()),
    re_path("^supersign/udid$", AppUDIDUsedView.as_view()),

]
