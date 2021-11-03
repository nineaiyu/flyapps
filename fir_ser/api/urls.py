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
from api.views.apps import AppsView, AppInfoView, AppReleaseInfoView
from api.views.domain import DomainCnameView, DomainInfoView
from api.views.download import ShortDownloadView
from api.views.login import LoginView, UserInfoView, RegistView, AuthorizationView, ChangeAuthorizationView, \
    UserApiTokenView, CertificationView, ChangeInfoView, WeChatLoginView, WeChatLoginCheckView
from api.views.logout import LogoutView
from api.views.order import PriceView, OrderView, PaySuccess
from api.views.receiveudids import IosUDIDView, TaskView
from api.views.storage import StorageView
from api.views.supersign import DeveloperView, SuperSignUsedView, AppUDIDUsedView, SuperSignCertView, DeviceUsedBillView
from api.views.thirdlogin import ValidWxChatToken, ThirdWxAccount
from api.views.uploads import AppAnalyseView, UploadView

# router=DefaultRouter()
# router.register("apps", AppsView)

urlpatterns = [
    # path("",include(router.urls)),
    re_path("^login", LoginView.as_view()),
    re_path("^auth$", AuthorizationView.as_view()),
    re_path("^authc$", ChangeAuthorizationView.as_view()),
    re_path("^change$", ChangeInfoView.as_view()),
    re_path("^register", RegistView.as_view()),
    re_path("^logout", LogoutView.as_view()),
    re_path("^apps$", AppsView.as_view()),
    re_path("^storage$", StorageView.as_view()),
    re_path(r"^apps/(?P<app_id>\w+)", AppInfoView.as_view()),
    re_path(r"^appinfos/(?P<app_id>\w+)/(?P<act>\w+)", AppReleaseInfoView.as_view()),
    re_path("^upload$", UploadView.as_view()),
    re_path("^userinfo", UserInfoView.as_view()),
    re_path("^token", UserApiTokenView.as_view()),
    re_path(r"^short/(?P<short>\w+)$", ShortDownloadView.as_view()),
    re_path(r"^udid/(?P<short>\w+)$", IosUDIDView.as_view()),
    re_path(r"^task/(?P<short>\w+)$", TaskView.as_view()),
    re_path("^analyse$", AppAnalyseView.as_view()),
    re_path("^advert$", UserAdInfoView.as_view()),
    re_path("^supersign/developer$", DeveloperView.as_view()),
    re_path("^supersign/devices$", SuperSignUsedView.as_view()),
    re_path("^supersign/udid$", AppUDIDUsedView.as_view()),
    re_path("^supersign/cert$", SuperSignCertView.as_view()),
    re_path("^supersign/bill$", DeviceUsedBillView.as_view()),
    re_path("^package_prices$", PriceView.as_view()),
    re_path("^orders$", OrderView.as_view()),
    re_path("^certification$", CertificationView.as_view()),
    re_path(r"^pay_success/(?P<name>\w+)$", PaySuccess.as_view()),
    re_path("^cname_domain$", DomainCnameView.as_view()),
    re_path("^domain_info$", DomainInfoView.as_view()),
    re_path("^mp.weixin$", ValidWxChatToken.as_view()),
    re_path("^third.wx.login$", WeChatLoginView.as_view()),
    re_path("^third.wx.sync$", WeChatLoginCheckView.as_view()),
    re_path("^twx/info$", ThirdWxAccount.as_view()),

]
