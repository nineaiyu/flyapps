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

from xsign.views.appinfo import AppCanSignView, AppSignInfoView
from xsign.views.receiveudids import IosUDIDView, TaskView
from xsign.views.supersign import DeveloperView, SuperSignUsedView, AppUDIDUsedView, SuperSignCertView, \
    DeviceUsedBillView, DeveloperDeviceView, DeviceUsedRankInfoView, AppleDeveloperBindAppsView, DeviceTransferBillView

urlpatterns = [
    re_path(r"^udid/(?P<short>\w+)$", IosUDIDView.as_view()),
    re_path(r"^task/(?P<short>\w+)$", TaskView.as_view()),
    re_path(r"^developer$", DeveloperView.as_view()),
    re_path(r"^devices$", SuperSignUsedView.as_view()),
    re_path(r"^udid$", AppUDIDUsedView.as_view()),
    re_path(r"^udevices$", DeveloperDeviceView.as_view()),
    re_path(r"^cert$", SuperSignCertView.as_view()),
    re_path(r"^bill$", DeviceUsedBillView.as_view()),
    re_path(r"^devicebill$", DeviceTransferBillView.as_view()),
    re_path(r"^rank$", DeviceUsedRankInfoView.as_view()),
    re_path(r"^bind$", AppleDeveloperBindAppsView.as_view()),
    re_path(r"^cansign$", AppCanSignView.as_view()),
    re_path(r"^signinfo/(?P<app_id>\w+)$", AppSignInfoView.as_view()),
]
