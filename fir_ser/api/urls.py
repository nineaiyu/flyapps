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

from api.views.advert import UserAdInfoView
from api.views.apps import AppsView, AppInfoView, AppReleaseInfoView, AppsQrcodeShowView
from api.views.domain import DomainCnameView, DomainInfoView
from api.views.download import ShortDownloadView, InstallView, DownloadView
from api.views.getip import GetRemoteIp
from api.views.login import LoginView, UserInfoView, RegistView, AuthorizationView, ChangeAuthorizationView, \
    UserApiTokenView, CertificationView, ChangeInfoView
from api.views.login_wx import WeChatLoginView, WeChatLoginCheckView, WeChatBindView, WeChatWebLoginView, \
    WeChatWebSyncView
from api.views.logout import LogoutView
from api.views.notify import NotifyReceiverView, NotifyConfigView, NotifyInfoView
from api.views.order import PriceView, OrderView, PaySuccess, OrderSyncView
from api.views.report import ReportView
from api.views.storage import StorageView, CleanStorageView
from api.views.thirdlogin import ValidWxChatToken, ThirdWxAccount
from api.views.uploads import AppAnalyseView, UploadView

# router=DefaultRouter()
# router.register("apps", AppsView)

urlpatterns = [
    # path("",include(router.urls)),
    re_path("^rip", GetRemoteIp.as_view()),
    re_path("^login", LoginView.as_view()),
    re_path("^auth$", AuthorizationView.as_view()),
    re_path("^authc$", ChangeAuthorizationView.as_view()),
    re_path("^change$", ChangeInfoView.as_view()),
    re_path("^register", RegistView.as_view()),
    re_path("^logout", LogoutView.as_view()),
    re_path("^apps$", AppsView.as_view()),
    re_path("^storage$", StorageView.as_view()),
    re_path("^storage/clean$", CleanStorageView.as_view()),
    re_path(r"^apps/(?P<app_id>\w+)", AppInfoView.as_view()),
    re_path(r"^appinfos/(?P<app_id>\w+)/(?P<act>\w+)", AppReleaseInfoView.as_view()),
    re_path("^upload$", UploadView.as_view()),
    re_path("^userinfo", UserInfoView.as_view()),
    re_path("^token", UserApiTokenView.as_view()),
    re_path(r"^short/(?P<short>\w+)$", ShortDownloadView.as_view()),
    re_path("^analyse$", AppAnalyseView.as_view()),
    re_path("^advert$", UserAdInfoView.as_view()),
    re_path("^report$", ReportView.as_view()),
    re_path("^qrcode$", AppsQrcodeShowView.as_view()),
    re_path("^package_prices$", PriceView.as_view()),
    re_path("^orders$", OrderView.as_view()),
    re_path("^notify/receiver$", NotifyReceiverView.as_view()),
    re_path("^notify/config$", NotifyConfigView.as_view()),
    re_path("^notify/notify$", NotifyInfoView.as_view()),
    re_path("^orders.sync$", OrderSyncView.as_view()),
    re_path("^certification$", CertificationView.as_view()),
    re_path(r"^pay_success/(?P<name>\w+)$", PaySuccess.as_view()),
    re_path("^cname_domain$", DomainCnameView.as_view()),
    re_path("^domain_info$", DomainInfoView.as_view()),
    re_path("^mp.weixin$", ValidWxChatToken.as_view()),
    re_path("^mp.web.login$", WeChatWebLoginView.as_view(), name="mp.web.login"),
    re_path("^mp.web.sync$", WeChatWebSyncView.as_view(), name="mp.web.sync"),
    re_path("^third.wx.login$", WeChatLoginView.as_view()),
    re_path("^third.wx.bind$", WeChatBindView.as_view()),
    re_path("^third.wx.sync$", WeChatLoginCheckView.as_view()),
    re_path("^twx/info$", ThirdWxAccount.as_view()),
    re_path(r"^install/(?P<app_id>\w+)$", InstallView.as_view(), name="install"),
    re_path(r"^download/(?P<filename>\w+\.\w+)$", DownloadView.as_view(), name="download"),
]
