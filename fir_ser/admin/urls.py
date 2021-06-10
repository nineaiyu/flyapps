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
from admin.views.login import LoginView, LoginUserView
from admin.views.user import UserInfoView, UserCertificationInfoView
from admin.views.app import AppInfoView, AppReleaseInfoView
from admin.views.storage import StorageInfoView, StorageChangeView
from admin.views.order import OrderPayView, OrderInfoView
from admin.views.supersign import DeveloperInfoView,DevicesInfoView

urlpatterns = [
    # path("",include(router.urls)),
    # re_path("^users$", CertificationView.as_view()),
    # re_path("^apps$", CertificationView.as_view()),
    re_path("^login", LoginView.as_view()),
    re_path("^user/info", LoginUserView.as_view()),
    re_path("^userinfo", UserInfoView.as_view()),
    re_path("^app/info", AppInfoView.as_view()),
    re_path("^app/release/info", AppReleaseInfoView.as_view()),
    re_path("^certification/info", UserCertificationInfoView.as_view()),
    re_path("^storage/info", StorageInfoView.as_view()),
    re_path("^storage/change", StorageChangeView.as_view()),
    re_path("^order/info", OrderInfoView.as_view()),
    re_path("^developer/info", DeveloperInfoView.as_view()),
    re_path("^devices/info", DevicesInfoView.as_view()),

]
