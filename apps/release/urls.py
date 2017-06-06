#coding:utf8

from django.conf.urls import url,include
from views import ReleaseTaskView

urlpatterns = [
    url(r'^release_task/$',ReleaseTaskView.as_view(),name="release_task"),
]
