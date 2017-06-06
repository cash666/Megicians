#coding:utf8

from django.conf.urls import url,include
from views import FrontConfigView,BackConfigView,AddFrontTypeView,AddFrontHostView,ModifyProjectView,AddBackProjectView,ModifyBackGroupView,CreateFrontTaskView,CreateBackTaskView,ShowFrontTaskView,ModifyFrontTaskView,ShowBackTaskView,ModifyBackTaskView,DownloadView,CheckTaskView,DeleteBackProjectView,DeleteFrontTypeView,DeleteFrontHostView

urlpatterns = [
    url(r'^front_list/',FrontConfigView.as_view(),name="front_list"),
    url(r'^add_front_type/',AddFrontTypeView.as_view(),name="add_front_type"),
    url(r'^delete_front_type/',DeleteFrontTypeView.as_view(),name="delete_front_type"),
    url(r'^add_front_host/',AddFrontHostView.as_view(),name="add_front_host"),
    url(r'^delete_front_host/',DeleteFrontHostView.as_view(),name="delete_front_host"),
    url(r'^modify_project/(?P<project_id>\d+)/$',ModifyProjectView.as_view(),name="modify_project"),
    url(r'^back_list/',BackConfigView.as_view(),name="back_list"),
    url(r'^add_back_project/',AddBackProjectView.as_view(),name="add_back_project"),
    url(r'^delete_back_project/',DeleteBackProjectView.as_view(),name="delete_back_project"),
    url(r'^modify_back_group/(?P<group_id>\d+)/$',ModifyBackGroupView.as_view(),name="modify_back_group"),
    url(r'^create_front_task/$',CreateFrontTaskView.as_view(),name="create_front_task"),
    url(r'^create_back_task/$',CreateBackTaskView.as_view(),name="create_back_task"),
    url(r'^show_front_task/$',ShowFrontTaskView.as_view(),name="show_front_task"),
    url(r'^modify_front_task/(?P<task_id>\d+)/$',ModifyFrontTaskView.as_view(),name="modify_front_task"),
    url(r'^show_back_task/$',ShowBackTaskView.as_view(),name="show_back_task"),
    url(r'^modify_back_task/(?P<task_id>\d+)/$',ModifyBackTaskView.as_view(),name="modify_back_task"),
    url(r'^download/(?P<task_id>\d+)/$',DownloadView.as_view(),name="download"),
    url(r'^check_task/$',CheckTaskView.as_view(),name="check_task"),
]
