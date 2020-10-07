"""iwenedu URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
import os

from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.views.static import serve

import xadmin

from apps.users.views import LoginView, LogoutView, SendSmsView, RegisterView
from apps.organizations.views import OrgView
from iwenedu.settings import MEDIA_ROOT, BASE_DIR
from apps.operations.views import IndexView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ueditor/', include('DjangoUeditor.urls')),
    path('xadmin/', xadmin.site.urls),
    path('', IndexView.as_view(), name="index"),
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('logout/', LogoutView.as_view(), name="logout"),
    url(r'^captcha/', include('captcha.urls')),

    # 发送验证码
    url(r'^send_sms/', csrf_exempt(SendSmsView.as_view()), name="send_sms"),

    # 配置上传文件的访问url
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # url(r'^static/(?P<path>.*)$', serve, {"document_root": os.path.join(BASE_DIR, 'static')}),

    # 机构相关页面
    url(r'^org/', include(('apps.organizations.urls', "organizations"), namespace="org")),

    # 用户相关操作页面
    url(r'^op/', include(('apps.operations.urls', "operations"), namespace="op")),

    # 公开课相关页面
    url(r'^course/', include(('apps.courses.urls', "courses"), namespace="course")),

    # 个人中心相关页面
    url(r'^users/', include(('apps.users.urls', "users"), namespace="users")),

    # 富文本编辑器
    url(r'^ueditor/',include('DjangoUeditor.urls')),
]
