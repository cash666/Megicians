from django.conf.urls import url,include
from views import LoginView,LogoutView,UsersListView,UserAddView,UserModifyPassword,UserModifyStatusView,UserDeleteView,GroupListView,GroupView,UserGroupView,GroupPermissionListView,GroupPermission

urlpatterns = [
    url('^login',LoginView.as_view(),name='login'),
    url('^logout/$',LogoutView.as_view(),name='logout'),
    url('^list/$',UsersListView.as_view(),name='userslist'),
    url('^add/$',UserAddView.as_view(),name='adduser'),
    url('^modifypasswd/$',UserModifyPassword.as_view(),name='modifyuserpasswd'),
    url('^modifystatus/$',UserModifyStatusView.as_view(),name='modifyuserstatus'),
    url('^deleteuser/$',UserDeleteView.as_view(),name='deleteuser'),
    url(r'group/',include([
        url(r'^user_to_group',GroupView.as_view(),name='group'),
        url(r'^list/$',GroupListView.as_view(),name='grouplist'),
        url(r'^user_group_list/$',UserGroupView.as_view(),name='usergrouplist'),
        url(r'^permissionlist/$',GroupPermissionListView.as_view(),name='grouppermissionlist'),
        url(r'^grouppermission/$',GroupPermission.as_view(),name='grouppermission'),
    ]))
]
