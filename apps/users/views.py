#coding:utf8
from django.shortcuts import render,redirect,render_to_response
from django.views.generic import View,TemplateView,ListView
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User,Group,Permission,ContentType
from utils.mixin_utils import LoginRequiredMixin
from models import UserProfile
from task.models import FrontTask,BackTask
from django.contrib.auth import  authenticate,login,logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import JsonResponse,HttpResponse,Http404,QueryDict
from forms import UserRegistrationFrom,UserModifyPasswd
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import get_user_model
from django.core import serializers
from django.conf import  settings
import datetime
import json

class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = UserProfile.objects.get(Q(username=username)|Q(email=username))
            if user.check_password(password):
                return  user
        except Exception as e:
            return None

def page_not_found(request):    
    return render_to_response('404.html')

def page_error(request):    
    return render_to_response('500.html')

def page_forbidden(request):    
    return render_to_response('403.html')

class LoginView(TemplateView):
    template_name = "login.html"
    def post(self,request):
        username = request.POST.get("username",None)
        password = request.POST.get("password",None)
        user = authenticate(username=username,password=password)
        if user is not None:
            if user.is_active:
                login(request,user)
                return redirect(request.GET.get('next') or "/")
            else:
                context="用户尚未被激活，请找管理员激活。"
                return render(request, "login.html", {'context':context})
        else:
            context="用户名或密码错误"
            return render(request, "login.html", {'context':context})

class LogoutView(LoginRequiredMixin,View):
    def get(self,request):
        logout(request)
        return redirect("users:login")

class IndexView(LoginRequiredMixin,View):
    def get(self,request):
	front_task_5=FrontTask.objects.filter(complete_status=u'已完成',operator=request.user.username).order_by('-create_time')[:5]
	back_task_5=BackTask.objects.filter(complete_status=u'已完成',operator=request.user.username).order_by('-create_time')[:5]
	today = datetime.date.today()
	series=[]
	date_list=[today - datetime.timedelta(days=6),today - datetime.timedelta(days=5),today - datetime.timedelta(days=4),today - datetime.timedelta(days=3),today - datetime.timedelta(days=2),today - datetime.timedelta(days=1),today]
	dic_name_1={}
	dic_name_1['name']=u'前端发布统计'
	dic_name_1['data']=[]
	for d in date_list:
		count=FrontTask.objects.filter(complete_status=u'已完成',create_time__startswith=d).count()
		dic_name_1['data'].append(count)
	series.append(dic_name_1)
	dic_name_2={}
	dic_name_2['name']=u'后端发布统计'
        dic_name_2['data']=[]
        for d in date_list:
                count=BackTask.objects.filter(complete_status=u'已完成',create_time__startswith=d).count()
                dic_name_2['data'].append(count)
	series.append(dic_name_2)
	json_series=json.dumps(series,separators=(',',':'))
        return render(request,"index.html",{'menu':'home_page','front_task_5':front_task_5,'back_task_5':back_task_5,'json_series':json_series})

    def post(self,request):
        head_image=request.FILES.get('head_image','')
	head_image_name=head_image.name
	import time
        import os.path
	extension=os.path.splitext('%s' % head_image_name)[1]
        head_image_name='%s%s' % (int(time.time()),extension)
	if head_image:
	    f=open('image/%s' % head_image_name,'wb')
            for line in head_image.chunks():
                f.write(line)
            f.close()
	    from megicians.settings import BASE_DIR
            u=UserProfile.objects.get(username=request.user.username)
	    u.head_image="image/%s" % head_image_name
	    u.save()
	    message=u'上传成功'
	    src='%s/image/%s' % (BASE_DIR,head_image_name)
	    dest='%s/media/image/%s' % (BASE_DIR,head_image_name)
	    os.symlink(src,dest)
	    return redirect('/?message=%s' % message)



class UsersListView(LoginRequiredMixin,ListView):
    template_name = "userlist.html"
    context_object_name = "userlist"
    paginate_by = 5
    model = UserProfile

    def get_context_data(self, **kwargs):
        context = super(UsersListView, self).get_context_data(**kwargs)
        context['menu'] = 'user-list'
        return context


class UserAddView(View):
    def post(self,request):
        ret = {'status': 0}
        form = UserRegistrationFrom(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                username=data.get('username')
                password=data.get('register_password')
                email=data.get('email')
                nickname=data.get('username')
		groupid=int(data.get('groupid'))
                users=UserProfile.objects.create_user(username=username,password=password,email=email,nick_name=nickname)
                group = Group.objects.get(pk=groupid)
		users.groups.add(group)
		users.save()
            except Exception as e:
                msg="用户 {} 注册失败：{}".format(request.user.username,e.args)
                ret['status']=1
                ret['errmsg']=msg
        else:
            myerror=""
            a=""
            for i,k in form.errors.items():
                for m in k:
                    a =  i+" "+ m
                myerror=myerror+" "+ a+"\n"
            msg=myerror
            ret['status'] = 1
            ret['errmsg'] = msg
        return JsonResponse(ret,safe=True)
    def get(self,request):
        return render(request,'usermodify.html')

class UserModifyPassword(LoginRequiredMixin,View):
    def post(self,request):
        ret = {'status': 0}
        form=UserModifyPasswd(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                username=data.get('username')
                password=data.get('register_password')
                user=UserProfile.objects.get(username=username)
                user.set_password(password)
                user.save()
            except Exception as e:
                msg="用户 {} 注册失败：{}".format(request.user.username,e.args)
                ret['status']=1
                ret['errmsg']=msg
        else:
            myerror=""
            a=""
            for i,k in form.errors.items():
                for m in k:
                    a =  i+" "+ m
                myerror=myerror+" "+ a+"\n"
            msg=myerror
            ret['status'] = 1
            ret['errmsg'] = msg
        return JsonResponse(ret,safe=True)

class UserModifyStatusView(LoginRequiredMixin,View):
    def post(self,request):
        ret={'status':0}
        username=request.POST.get('username',None)
        try:
            user = UserProfile.objects.get(username=username)
            if user.is_active:
                user.is_active = False
            else:
                user.is_active = True
            user.save()
        except User.DoesNotExist:
            ret['status']=1
            ret['errmsg']="用户不存在"
        return JsonResponse(ret,safe=True)

class UserDeleteView(LoginRequiredMixin,View):
    def post(self,request):
        ret={'status':0}
        username=request.POST.get('username',None)
        try:
            UserProfile.objects.filter(username=username).delete()
        except User.DoesNotExist:
            ret['status']=1
            ret['errmsg']="用户不存在"
        return JsonResponse(ret,safe=True)

class GroupListView(LoginRequiredMixin,ListView):
    template_name = "grouplist.html"
    context_object_name = "grouplist"
    model = Group
    
    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)
        context['menu'] = 'group-list'
        return context

    def post(self,request):
        ret={"status":0}
        name=request.POST.get("name",None)
        if name:
            try:
                group=Group()
                group.name=name
                group.save()
            except Exception as e:
                ret['status']=1
                ret['errmsg']=e.args
        return JsonResponse(ret,safe=True)

    def get(self,request, *args, **kwargs):
        self.request=request
        return super(GroupListView, self).get(request,*args,**kwargs)

class GroupView(LoginRequiredMixin,View):
    def get(self,request):
        uid = request.GET.get('uid','')
        if uid == '':
            all_groups = Group.objects.all()
            groups = [group for group in all_groups ]
            return  HttpResponse(serializers.serialize("json",groups),content_type="application/json")
        ret = {"status":0}
        
        try:
            user = UserProfile.objects.get(pk=uid)
        except User.DoesNotExist:
            ret['status'] =1
            ret['errmsg'] = "用户不存在"

        all_groups = Group.objects.all()
        user_groups = user.groups.all()
        groups = [group for group in all_groups if group not in user_groups]
        return  HttpResponse(serializers.serialize("json",groups),content_type="application/json")

    def post(self,request):
        ret = {"status":0}
        uid=request.POST.get('uid',None)
        gid=request.POST.get('gid',None)
        try:
            user = UserProfile.objects.get(pk=uid)
        except User.DoesNotExist:
            ret['status'] =1
            ret['errmsg'] = "用户不存在"
            return JsonResponse(ret,safe=True)
        try:
            group = Group.objects.get(pk=gid)
        except Group.DoesNotExist:
            ret['status'] =1
            ret['errmsg'] = "用户组不存在"
            return JsonResponse(ret,safe=True)
        user.groups.add(group)
        return JsonResponse(ret,safe=True)

class UserGroupView(LoginRequiredMixin,View):
    def get(self,request):
        gid = request.GET.get('gid',None)
        try:
            group = Group.objects.get(pk=gid)
        except:
            return JsonResponse([],safe=False)
        users = group.user_set.all()
        user_list = [{"username":user.username,"email":user.email,"name":user.nick_name,"id":user.id} for user in users]
        return JsonResponse(user_list,safe=False)
    def post(self,request):
        ret = {"status":0}
        #data = QueryDict(request.POST)
        uid = request.POST.get('userid',None)
        gid = request.POST.get('groupid',None)
        try:
            user = UserProfile.objects.get(pk=uid)
            group=Group.objects.get(pk=gid)
            group.user_set.remove(user)
        except User.DoesNotExist:
            ret['status'] =1
            ret['errmsg'] ="用户不存在"
        except Group.DoesNotExist:
            ret['status'] =1
            ret['errmsg'] ="用户组不存在"
        except Exception as e:
            ret['status'] =1
            ret['errmsg'] =e.args
        return JsonResponse(ret,safe=True)

class GroupPermissionListView(LoginRequiredMixin,TemplateView):
    template_name = "group_permission_list.html"
    def get_context_data(self, **kwargs):
        context = super(GroupPermissionListView,self).get_context_data(**kwargs)
        context['group']=self.request.GET.get('gid',None)
        context['group_permissions']=self.get_group_permission()
        context['content_type']=ContentType.objects.all()
        return context
    def get_group_permission(self):
        gid = self.request.GET.get('gid',None)
        try:
            group=Group.objects.get(pk=gid)
            return [per.id for per in group.permissions.all()]
        except Group.DoesNotExist:
            raise Http404

    def post(self,request):
        permission_id_list = request.POST.getlist('permission',[])
        groupid = request.POST.get('group',None)
        ret ={"status":0,"next_url": "/users/group/list/"}
        try:
            group =Group.objects.get(pk=groupid)
        except Group.DoesNotExist:
            ret['status']=1
            ret['errmsg']="用户组不存在"
        else:
            if permission_id_list:
                permission_objs = Permission.objects.filter(id__in=permission_id_list)
                group.permissions = permission_objs
        return render(request, settings.TEMPLATE_JUMP, ret)

class GroupPermission(LoginRequiredMixin,View):
    def get(self,request):
        gid = request.GET.get('gid',None)
        try:
            group = Group.objects.get(pk=gid)
            group_permission = group.permissions.all()
        except:
            raise Http404
        permission_list=[{"pname":permission.name,"pcontent_type_id":permission.content_type_id,"pcodename":permission.codename,"pid":permission.id} for permission in group_permission]
        return JsonResponse(permission_list,safe=False)
