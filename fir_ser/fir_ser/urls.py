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

from admin.views.celery_flower import CeleryFlowerView

# from django.views.static import serve
# from fir_ser import settings

urlpatterns = [
    re_path('fly.admin/', admin.site.urls),
    # web api 请求地址
    re_path("api/v1/fir/server/", include('api.urls')),
    # client 脚本请求地址
    re_path("api/v2/fir/server/", include('cli.urls')),
    # 管理后台请求地址
    re_path("api/v3/fir/server/", include('admin.urls')),
    # 图片验证码
    re_path('^captcha/', include('captcha.urls')),

    # 该配置暂时无用
    # media路径配置 如果未开启token 授权，可以启动下面配置，直接让nginx读取资源，无需 uwsgi 进行转发
    # re_path('^files/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),

    # 任务监控
    re_path(r'flower/(?P<path>.*)', CeleryFlowerView.as_view()),

    # 超级签名
    re_path("api/v1/fir/xsign/", include('xsign.urls')),
]
