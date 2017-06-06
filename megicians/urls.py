"""megicians URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url,include
from django.contrib import admin
from django.views.static import serve
from megicians.settings import MEDIA_ROOT,MEDIA_URL
from users.views import IndexView,LoginView
from users import views
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url('^$',IndexView.as_view(),name='index'),
    #url(r'^media/(?P<path>.*)$',serve,{"document_root":MEDIA_ROOT}),
    url(r'^task/',include('task.urls',namespace="task")),   
    url(r'^users/', include('users.urls', namespace="users")),
    url(r'^release/', include('release.urls', namespace="release")),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
handler404 = views.page_not_found
handler500 = views.page_error
handler403 = views.page_forbidden
