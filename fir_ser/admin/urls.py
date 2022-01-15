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
from django.urls import re_path, include
from rest_framework.routers import SimpleRouter

from admin.views.app import AppInfoView, AppReleaseInfoView
from admin.views.domain import DomainNameInfoView
from admin.views.login import LoginView, LoginUserView
from admin.views.order import OrderInfoView
from admin.views.report import AdminReportView
from admin.views.storage import StorageInfoView, StorageChangeView
from admin.views.supersign import DeveloperInfoView, DevicesInfoView, SuperSignBillView, SuperSignBillUserInfoView
from admin.views.user import UserInfoView, UserCertificationInfoView, ThirdWxAccountView

router = SimpleRouter(False)
router.register('app/info', AppInfoView)
router.register('app/release/info', AppReleaseInfoView)
router.register('domain/info', DomainNameInfoView)
router.register('order/info', OrderInfoView)
router.register('report/info', AdminReportView)
router.register('storage/info', StorageInfoView)
router.register('developer/info', DeveloperInfoView)
router.register('devices/info', DevicesInfoView)
router.register('bill/info', SuperSignBillView)
router.register('wxbind/info', ThirdWxAccountView)
urlpatterns = [
    re_path("^login", LoginView.as_view()),
    re_path("^user/info", LoginUserView.as_view()),
    re_path("^userinfo", UserInfoView.as_view()),
    re_path("^certification/info", UserCertificationInfoView.as_view()),
    re_path("^storage/change", StorageChangeView.as_view()),
    re_path("^bill/userinfo", SuperSignBillUserInfoView.as_view()),
    re_path('', include(router.urls))
]
