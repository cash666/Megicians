#coding:utf8

from django.shortcuts import render,redirect,HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import View
from forms.FrontTypeForm import FrontTypeForm
from forms.FrontHostForm import FrontHostForm
from forms.FrontProjectForm import FrontProjectForm
from forms.BackProjectForm import BackProjectForm
from forms.BackGroupForm import BackGroupForm
from forms.CreateFrontTaskForm import CreateFrontTaskForm
from forms.CreateBackTaskForm import CreateBackTaskForm
from forms.BackDeleteProjectForm import BackDeleteProjectForm
from models import FrontProject,FrontType,FrontHost,BackProject,BackGroup,FrontTask,BackTask
from django.db.models import Q
from megicians import settings
from django.http import StreamingHttpResponse
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from utils.mixin_utils import LoginRequiredMixin
from utils.ansible_api import MyRunner
from django.utils.safestring import mark_safe
from users.models import UserProfile
import json
import os
import time
# Create your views here.

class FrontConfigView(LoginRequiredMixin,View):
	"""
	前端项目配置页面
	"""
	def get(self,request):
		front_type_form=FrontTypeForm()
		front_host_form=FrontHostForm()
		front_project_form=FrontProjectForm()
		sort=request.GET.get('sort','')
		if sort:
			all_front_project=FrontProject.objects.all().order_by('create_time')
		else:
			all_front_project=FrontProject.objects.all().order_by('-create_time')
		try:
			page = request.GET.get('page', 1)
		except PageNotAnInteger:
			page = 1
		p = Paginator(all_front_project,5,request=request)
		all_front_project=p.page(page)
		return render(request,'front-config.html',{'all_front_project':all_front_project,'front_type_form':front_type_form,'front_host_form':front_host_form,'front_project_form':front_project_form,'page':int(page),'menu':'front-config'})

	def post(self,request):
		all_front_project=FrontProject.objects.all().order_by('-create_time')
		front_type_form=FrontTypeForm()
                front_host_form=FrontHostForm()
                front_project_form=FrontProjectForm()
		id=request.POST.get('id','')
		front_search=request.POST.get('front_search','')
		front_search=front_search.strip()
                if id:
                	FrontProject.objects.filter(id=id).delete()
                        return HttpResponse('ok')
		if front_search:
			all_front_project=all_front_project.filter(Q(project_name__icontains=front_search)|Q(creater__icontains=front_search)|Q(front_type__project_type__icontains=front_search)|Q(front_host__project_host__icontains=front_search))
			try:
                        	page = request.GET.get('page', 1)
                	except PageNotAnInteger:
                        	page = 1
                	p = Paginator(all_front_project,5,request=request)
                	all_front_project=p.page(page)
                	return render(request,'front-config.html',{'all_front_project':all_front_project,'front_type_form':front_type_form,'front_host_form':front_host_form,'front_project_form':front_project_form,'page':int(page)})
		front_project_form=FrontProjectForm(request.POST)
		if front_project_form.is_valid():
			data=front_project_form.clean()
			project_name=data['project_name']
			project_name=project_name.strip()
			if_exist=FrontProject.objects.filter(project_name=project_name)
			if if_exist:
				message=u'该项目名称已存在'
                                return redirect('/task/front_list/?message=%s' % message)
			else:	
				if_ok=FrontProject.objects.create(project_name=project_name,front_type_id=data['front_type'],front_host_id=data['front_host'],creater=request.user.username)
				if if_ok:
					message=u'添加成功'
                                	return redirect('/task/front_list/?message=%s' % message)
				else:
					message=u'添加失败'
                                        return redirect('/task/front_list/?message=%s' % message)

class AddFrontTypeView(LoginRequiredMixin,View):
	"""
	添加前端项目类型
	"""
	def post(self,request):
		front_type_form=FrontTypeForm(request.POST)
		if front_type_form.is_valid():
			data=front_type_form.clean()
			project_type=data['project_type'].lower()
			project_type=project_type.strip()
			if_exist=FrontType.objects.filter(project_type=project_type)
			if if_exist:
				message=u'该类型已存在'
                                return redirect('/task/front_list/?message=%s' % message)
			else:
				front_type=front_type_form.save(commit=False)
				front_type.creater=request.user.username
				front_type.save()
				message=u'添加成功'
				return redirect('/task/front_list/?message=%s' % message)

class DeleteFrontTypeView(LoginRequiredMixin,View):
	"""
	删除前端类型
	"""
	def post(self,request):
		front_project_form=FrontProjectForm(request.POST)
		if front_project_form.is_valid():
			data=front_project_form.clean()
			front_type_id=data['front_type']
			FrontType.objects.get(id=front_type_id).delete()
			message=u'删除成功'
			return redirect('/task/front_list/?message=%s' % message)

class AddFrontHostView(LoginRequiredMixin,View):
	"""
	添加前端项目主机
	"""
	def post(self,request):
		front_host_form=FrontHostForm(request.POST)
		if front_host_form.is_valid():
			data=front_host_form.clean()
			project_host=data['project_host'].lower()
			project_host=project_host.strip()
			if_exist=FrontHost.objects.filter(project_host=project_host)
			if if_exist:
				message=u'该主机已存在'
				return redirect('/task/front_list/?message=%s' % message)
			else:
				front_host=front_host_form.save(commit=False)
				front_host.creater=request.user.username
				front_host.save()
                                message=u'添加成功'
                                return redirect('/task/front_list/?message=%s' % message)

class DeleteFrontHostView(LoginRequiredMixin,View):
	"""
	删除前端主机
	"""
	def post(self,request):
                front_project_form=FrontProjectForm(request.POST)
                if front_project_form.is_valid():
                        data=front_project_form.clean()
                        front_host_id=data['front_host']
                        FrontHost.objects.get(id=front_host_id).delete()
                        message=u'删除成功'
                        return redirect('/task/front_list/?message=%s' % message)

class ModifyProjectView(LoginRequiredMixin,View):
	"""
	修改前端项目名称，类型或主机

	"""
	def get(self,request,project_id):
		if project_id:
			front_project_form=FrontProjectForm()	
			project_obj=FrontProject.objects.get(id=project_id)
			return render(request,'modify-project.html',{'project_obj':project_obj,'front_project_form':front_project_form})

	def post(self,request,project_id):
		if project_id:
			front_project_form=FrontProjectForm(request.POST)
			if front_project_form.is_valid():
				data=front_project_form.clean()
				project_name=data['project_name']
				project_name=project_name.strip()
				if_exist=FrontProject.objects.exclude(id=project_id).filter(project_name=project_name)
				if if_exist:
					message=u'项目名称已经存在'
					return redirect('/task/front_list/?message=%s' % message)
				else:
					front_type_id=data['front_type']
					front_host_id=data['front_host']
					project_obj=FrontProject.objects.get(id=project_id)
					project_obj.project_name=project_name
					project_obj.front_type_id=front_type_id
					project_obj.front_host_id=front_host_id
					project_obj.save()
					message=u'项目修改成功'
                                        return redirect('/task/front_list/?message=%s' % message)
			
class BackConfigView(LoginRequiredMixin,View):
	"""
	后端项目配置页面
	"""
	def get(self,request):
		back_project_form=BackProjectForm()
		back_group_form=BackGroupForm()
		back_delete_project_form=BackDeleteProjectForm()
		sort=request.GET.get('sort','')
		if sort:
			all_back_group=BackGroup.objects.all().order_by('create_time')
		else:
                	all_back_group=BackGroup.objects.all().order_by('-create_time')
		try:
                	page = request.GET.get('page', 1)
                except PageNotAnInteger:
                        page = 1
                p = Paginator(all_back_group,5,request=request)
                all_back_group=p.page(page)
                return render(request,'back-config.html',{'all_back_group':all_back_group,'back_project_form':back_project_form,'back_group_form':back_group_form,'back_delete_project_form':back_delete_project_form,'page':int(page),'menu':'back-config'})

	def post(self,request):
		back_project_form=BackProjectForm()
                back_group_form=BackGroupForm()
		id=request.POST.get('id','')
		back_search=request.POST.get('back_search','')
		back_search=back_search.strip()
		if back_search:
			all_back_group=BackGroup.objects.filter(Q(project_group__icontains=back_search)|Q(hosts__icontains=back_search)|Q(creater__icontains=back_search)|Q(back_project__project_name__icontains=back_search)).order_by('-create_time')
			try:
                        	page = request.GET.get('page', 1)
                	except PageNotAnInteger:
                        	page = 1
                	p = Paginator(all_back_group,5,request=request)
                	all_back_group=p.page(page)
                	return render(request,'back-config.html',{'all_back_group':all_back_group,'back_project_form':back_project_form,'back_group_form':back_group_form,'page':int(page)})
                if id:
                        BackGroup.objects.filter(id=id).delete()
                        return HttpResponse('ok')
		back_group_form=BackGroupForm(request.POST)
		if back_group_form.is_valid():
			data=back_group_form.clean()
			project_group=data['project_group'].lower()
			project_group=project_group.strip()
			hosts_data=data['hosts'].lower()
			if_exist=BackGroup.objects.filter(project_group=project_group)
			host_list=BackGroup.objects.values_list('hosts')
			all_host_list=[]
			if if_exist:
                                message=u'项目组已存在'
                                return redirect('/task/back_list/?message=%s' % message)
                        for hosts in host_list:
                                for host in hosts:
                                        host=host.encode('utf8')
					if host.find(','):
						list_host=host.split(',')
						all_host_list.extend(list_host)
					else:
                                        	all_host_list.append(host)
                        if hosts_data.find(',')>0:
                                hosts_list=hosts_data.split(',')
                        else:
                                hosts_list=[hosts_data]
                        for host in hosts_list:
                                host=host.strip()
                                host=host.encode('utf8')
                                if host in all_host_list:
					message=u'主机已存在'
					return redirect('/task/back_list/?message=%s' % message)
			back_group=BackGroup()
			back_group.project_group=project_group
			back_group.back_project_id=data['back_project']
			back_group.hosts=data['hosts'].strip()
			back_group.creater=request.user.username
			back_group.save()
			message=u'项目组添加成功'
                        return redirect('/task/back_list/?message=%s' % message)
			

class AddBackProjectView(LoginRequiredMixin,View):
	"""
	添加后端项目
	"""
	def post(self,request):
		back_project_form=BackProjectForm(request.POST)
		if back_project_form.is_valid():
			data=back_project_form.clean()
			project_name=data['project_name'].lower()
			project_name=project_name.strip()
			if_exist=BackProject.objects.filter(project_name=project_name)
			if if_exist:
				message=u'项目已存在'
                                return redirect('/task/back_list/?message=%s' % message)
			else:
				back_project=back_project_form.save(commit=False)
				back_project.creater=request.user.username
				back_project.save()
				message=u'添加成功'
                        	return redirect('/task/back_list/?message=%s' % message)

class DeleteBackProjectView(LoginRequiredMixin,View):
	"""
	删除后端项目
	"""
	def post(self,request):
		back_delete_project_form=BackDeleteProjectForm(request.POST)
		if back_delete_project_form.is_valid():
			data=back_delete_project_form.clean()
			back_project_id=data['back_project']
			BackProject.objects.get(id=back_project_id).delete()
			message=u'删除成功'
			return redirect("/task/back_list/?message=%s" % message)
	
class ModifyBackGroupView(LoginRequiredMixin,View):
	"""
	修改后端项目组
	"""
	def get(self,request,group_id):
		back_group_form=BackGroupForm()
		group_obj=BackGroup.objects.get(id=group_id)
		return render(request,'modify-group.html',{'back_group_form':back_group_form,'group_obj':group_obj})

	def post(self,request,group_id):
		back_group_form=BackGroupForm(request.POST)
		if back_group_form.is_valid():
			data=back_group_form.clean()
			project_group=data['project_group'].lower()
			project_group=project_group.strip()
			hosts_data=data['hosts'].strip()
			if_exist=BackGroup.objects.exclude(id=group_id).filter(project_group=project_group)
			host_list=BackGroup.objects.exclude(id=group_id).values_list('hosts')
			all_host_list=[]
			for hosts in host_list:
				for host in hosts:
					host=host.encode('utf8')
					if host.find(','):
						list_host=host.split(',')
						all_host_list.extend(list_host)
					else:
						all_host_list.append(host)
			if hosts_data.find(',')>0:
				hosts_list=hosts_data.split(',')
			else:
				hosts_list=[hosts_data]
			for host in hosts_list:
				host=host.strip()
				host=host.encode('utf8')
				if host in all_host_list and if_exist:
					message=u'该项目组已经存在且主机也已存在'
					break
				elif host not in hosts and if_exist:
					message=u'项目组已经存在'
					break
				elif host in all_host_list and not if_exist:
					message=u'主机已经存在'
					break
				else:
					back_project_id=data['back_project']
					if_ok=BackGroup.objects.filter(id=group_id).update(back_project_id=back_project_id,project_group=project_group,hosts=hosts_data)
					if if_ok:
						message=u'修改成功'
			return redirect("/task/back_list/?message=%s" % message)

class CreateFrontTaskView(LoginRequiredMixin,View):
	"""
	创建前端任务
	"""
	def get(self,request):
		front_task_form=CreateFrontTaskForm()
		sort=request.GET.get('sort','')
		if sort:
			all_front_task=FrontTask.objects.filter(Q(creater=request.user.username)|Q(operator=request.user.username)|Q(cc__icontains=request.user.username)).order_by('create_time')
		else:
			all_front_task=FrontTask.objects.filter(Q(creater=request.user.username)|Q(operator=request.user.username)|Q(cc__icontains=request.user.username)).order_by('-create_time')
		try:
                	page = request.GET.get('page', 1)
                except PageNotAnInteger:
                        page = 1
		p = Paginator(all_front_task,5,request=request)
                all_front_task=p.page(page)
		return render(request,'create-front-task.html',{'front_task_form':front_task_form,'all_front_task':all_front_task,'page':int(page),'menu':'front-task'})

	def post(self,request):
		front_task_search=request.POST.get('front_task_search','')
		id=request.POST.get('id','')
		if id:
			FrontTask.objects.filter(id=id).delete()
			return HttpResponse('ok')
		if front_task_search:
			front_task_search=front_task_search.strip()
			try:
				front_task_search=int(front_task_search)
				all_front_task=FrontTask.objects.filter(Q(project_version=front_task_search)).order_by('-create_time')
			except ValueError:
				all_front_task=FrontTask.objects.filter(Q(task_name__icontains=front_task_search)|Q(front_project__project_name__icontains=front_task_search)|Q(front_type__project_type__icontains=front_task_search)|Q(front_host__project_host__icontains=front_task_search)|Q(project_md5__icontains=front_task_search)|Q(complete_status__icontains=front_task_search)|Q(review_status__icontains=front_task_search)|Q(creater__icontains=front_task_search)|Q(operator__icontains=front_task_search)).order_by('-create_time')
			try:
                        	page = request.GET.get('page', 1)
                	except PageNotAnInteger:
                        	page = 1
                	p = Paginator(all_front_task,5,request=request)
                	all_front_task=p.page(page)
			front_task_form=CreateFrontTaskForm()
			return render(request,'create-front-task.html',{'front_task_form':front_task_form,'all_front_task':all_front_task,'page':int(page)})
		front_task_form=CreateFrontTaskForm(request.POST)
		if front_task_form.is_valid():
			data=front_task_form.cleaned_data
			if data.get('task_cc',''):
                        	cc=data.get('task_cc').encode('utf8').strip('[')
                        	cc=cc.strip(']')
                        	cc_list=cc.split(',')
                        	cc_new_list=[]
                        	for cc in cc_list:
                                	cc=cc.strip()
                                	cc=cc.strip('u')
                                	cc_new_list.append(cc)
                        	task_cc=','.join(cc_new_list)
			else:
				task_cc=''
			project_md5=data['project_md5'].strip()
			project_version=data['project_version']
			if project_version <= 0:
				message=u'任务构建号不能小于等于0'
                                return redirect('/task/create_front_task/?message=%s' % message)
			if_exist=FrontTask.objects.filter(project_md5=project_md5)
			if if_exist:
				message=u'该任务版本号已存在'
				return redirect('/task/create_front_task/?message=%s' % message)
			else:
				operator_obj=UserProfile.objects.get(pk=data['operator'])
                                operator=operator_obj.username
				front_project_obj=FrontProject.objects.get(pk=data['front_project'].strip())
				front_type_id=front_project_obj.front_type_id
				front_host_id=front_project_obj.front_host_id
				print front_host_id
				front_task={
					'task_name':data['task_name'].strip(),
					'front_project_id':data['front_project'].strip(),
					'front_type_id':front_type_id,
					'front_host_id':front_host_id,
					'project_version':data['project_version'],
					'project_md5':data['project_md5'].strip(),
					'creater':request.user.username,
					'operator':operator,
					'cc':task_cc,
					'complete_status':u'已创建',
					'review_status':u'未审核',
					'description':data.get('description','').strip(),
				}
				if_ok=FrontTask.objects.create(**front_task)
				if if_ok:
					message=u'前端任务创建成功'
					return redirect('/task/create_front_task/?message=%s' % message)

class CreateBackTaskView(LoginRequiredMixin,View):
	"""
	创建后端任务
	"""
	def get(self,request):
                back_task_form=CreateBackTaskForm()
		sort=request.GET.get('sort','')
		if sort:
                	all_back_task=BackTask.objects.filter(Q(creater=request.user.username)|Q(operator=request.user.username)|Q(cc__icontains=request.user.username)).order_by('create_time')
		else:
                	all_back_task=BackTask.objects.filter(Q(creater=request.user.username)|Q(operator=request.user.username)|Q(cc__icontains=request.user.username)).order_by('-create_time')
                try:
                        page = request.GET.get('page', 1)
                except PageNotAnInteger:
                        page = 1
                p = Paginator(all_back_task,5,request=request)
                all_back_task=p.page(page)
                return render(request,'create-back-task.html',{'back_task_form':back_task_form,'all_back_task':all_back_task,'page':int(page),'menu':'back-task'})

	def post(self,request):
                back_task_form=CreateBackTaskForm(request.POST,request.FILES)
		back_task_search=request.POST.get('back_task_search','')
		id=request.POST.get('id','')
                if id:
                        BackTask.objects.filter(id=id).delete()
                        return HttpResponse('ok')
		if back_task_search:
                        back_task_search=back_task_search.strip()
                        try:
                                back_task_search=int(back_task_search)
                                all_back_task=BackTask.objects.filter(Q(project_version=back_task_search)).order_by('-create_time')
                        except ValueError:
                                all_back_task=BackTask.objects.filter(Q(task_name__icontains=back_task_search)|Q(back_project__project_name__icontains=back_task_search)|Q(back_group__project_group__icontains=back_task_search)|Q(project_md5__icontains=back_task_search)|Q(complete_status__icontains=back_task_search)|Q(review_status__icontains=back_task_search)|Q(creater__icontains=back_task_search)|Q(operator__icontains=back_task_search)).order_by('-create_time')
                        try:
                                page = request.GET.get('page', 1)
                        except PageNotAnInteger:
                                page = 1
                        p = Paginator(all_back_task,5,request=request)
                        all_back_task=p.page(page)
                        back_task_form=CreateBackTaskForm()
                        return render(request,'create-back-task.html',{'back_task_form':back_task_form,'all_back_task':all_back_task,'page':int(page)})
                if back_task_form.is_valid():
                        data=back_task_form.cleaned_data
			cc=data.get('task_cc').encode('utf8').strip('[')
			cc=cc.strip(']')
			cc_list=cc.split(',')
			cc_new_list=[]
			for cc in cc_list:
				cc=cc.strip()
				cc=cc.strip('u')
				cc_new_list.append(cc)
			task_cc=','.join(cc_new_list)
                        project_md5=data['project_md5'].strip()
                        project_version=data['project_version']
                        if project_version <= 0:
                                message=u'任务构建号不能小于等于0'
                                return redirect('/task/create_back_task/?message=%s' % message)
                        if_exist=BackTask.objects.filter(project_md5=project_md5)
                        if if_exist:
                                message=u'该任务版本号已存在'
                                return redirect('/task/create_back_task/?message=%s' % message)
                        else:
				if data['attachment']:
					file_obj=data['attachment']
					file_name=file_obj.name
					f=open('uploads/%s' % file_name,'wb')
					for line in file_obj.chunks():
						f.write(line)
					f.close()
					attachment="uploads/%s" % file_name
				else:
					attachment=None
                                operator_obj=UserProfile.objects.get(pk=data['operator'])
				operator=operator_obj.username
                                back_task={
                                	'task_name':data['task_name'].strip(),
                                        'back_project_id':data['back_project'].strip(),
                                       	'back_group_id':data['back_group'].strip(),
                                       	'project_version':data['project_version'],
                                       	'project_md5':data['project_md5'].strip(),
                                       	'creater':request.user.username,
                                       	'operator':operator,
                                       	'cc':task_cc,
				       	'attachment':attachment,
                                       	'complete_status':u'已创建',
                                       	'review_status':u'未审核',
                                       	'description':data.get('description','').strip(),
                                }
                                if_ok=BackTask.objects.create(**back_task)
                                if if_ok:
                                        message=u'后端任务创建成功'
                                        return redirect('/task/create_back_task/?message=%s' % message)

class ShowFrontTaskView(LoginRequiredMixin,View):
	"""
	查看前端任务详情页
	"""
	def get(self,request):
		id=request.GET.get('id','')
		if id:
			front_task=FrontTask.objects.get(id=id)
			return render(request,'show-front-task.html',{'front_task':front_task})

class ModifyFrontTaskView(LoginRequiredMixin,View):
	"""
	修改前端任务
	"""
	def get(self,request,task_id):
		front_task_form=CreateFrontTaskForm()
		if task_id:
			front_task=FrontTask.objects.get(id=task_id)
			return render(request,'modify-front-task.html',{'front_task_form':front_task_form,'front_task':front_task})

	def post(self,request,task_id):
		front_task_form=CreateFrontTaskForm(request.POST)
		if task_id:
			if front_task_form.is_valid():
				data=front_task_form.clean()
				task_name=data['task_name'].strip()
				front_project_id=data['front_project']
				front_type_id=data['front_type']
				front_host_id=data['front_host']
				project_version=data['project_version']
				project_md5=data['project_md5'].strip()
				operator=data['operator'].strip()
				user_obj=UserProfile.objects.get(pk=int(operator))
				operator=user_obj.username
				description=data['description'].strip()
				if int(project_version)<=0:
					message=u'构建号不能小于等于0'
					return redirect('/task/create_front_task/?message=%s' % message)
				if_exist=FrontTask.objects.exclude(id=task_id).filter(project_md5=project_md5)
				if if_exist:
					message=u'任务版本号已经存在'
                                        return redirect('/task/create_front_task/?message=%s' % message)
				if_ok=FrontTask.objects.filter(id=task_id).update(task_name=task_name,front_project_id=front_project_id,front_type_id=front_type_id,front_host_id=front_host_id,project_version=project_version,project_md5=project_md5,operator=operator,description=description)
				if if_ok:
					message=u'修改成功'
					return redirect('/task/create_front_task/?message=%s' % message)

class ShowBackTaskView(LoginRequiredMixin,View):
        """
        查看后端任务详情页
        """
        def get(self,request):
                id=request.GET.get('id','')
                if id:
                        back_task=BackTask.objects.get(id=id)
                        return render(request,'show-back-task.html',{'back_task':back_task})

class ModifyBackTaskView(LoginRequiredMixin,View):
        """
        修改后端任务
        """
        def get(self,request,task_id):
                back_task_form=CreateBackTaskForm()
                if task_id:
                        back_task=BackTask.objects.get(id=task_id)
                        return render(request,'modify-back-task.html',{'back_task_form':back_task_form,'back_task':back_task,'task_id':task_id})

        def post(self,request,task_id):
                back_task_form=CreateBackTaskForm(request.POST,request.FILES)
                if task_id:
                        if back_task_form.is_valid():
                                data=back_task_form.clean()
                                task_name=data['task_name'].strip()
                                back_project_id=data['back_project']
                                back_group_id=data['back_group']
                                project_version=data['project_version']
                                project_md5=data['project_md5'].strip()
                                operator=data['operator'].strip()
				user_obj=UserProfile.objects.get(pk=int(operator))
                                operator=user_obj.username
                                description=data['description'].strip()
                                if int(project_version)<=0:
                                        message=u'构建号不能小于等于0'
                                        return redirect('/task/create_back_task/?message=%s' % message)
                                if_exist=BackTask.objects.exclude(id=task_id).filter(project_md5=project_md5)
                                if if_exist:
                                        message=u'任务版本号已经存在'
                                        return redirect('/task/create_back_task/?message=%s' % message)
				if data['attachment']:
                                        file_obj=data['attachment']
                                        file_name=file_obj.name.strip()
					task_obj=BackTask.objects.get(id=task_id)
					if task_obj.attachment.name != file_name:
                                        	f=open('uploads/%s' % file_name,'wb')
                                        	for line in file_obj.chunks():
                                                	f.write(line)
                                        	f.close()
						attachment="uploads/%s" % file_name
                                		if_ok=BackTask.objects.filter(id=task_id).update(task_name=task_name,back_project_id=back_project_id,back_group_id=back_group_id,project_version=project_version,project_md5=project_md5,operator=operator,attachment=attachment,description=description)
				else:	
                                	if_ok=BackTask.objects.filter(id=task_id).update(task_name=task_name,back_project_id=back_project_id,back_group_id=back_group_id,project_version=project_version,project_md5=project_md5,operator=operator,description=description)
                                if if_ok:
                                	message=u'修改成功'
                                        return redirect('/task/create_back_task/?message=%s' % message)

class DownloadView(LoginRequiredMixin,View):
	"""
	下载附件
	"""
	def get(self,request,task_id):
		def file_iterator(file_name, chunk_size=512): 
			with open(file_name) as f: 
				while True:
					c = f.read(chunk_size)
					if c:                    			
						yield c                		
					else:                    			
						break
		task_obj=BackTask.objects.get(id=task_id)
		download_name=task_obj.attachment.name
		full_download_name=u"%s/%s" % (settings.BASE_DIR,download_name)
		response = StreamingHttpResponse(file_iterator(full_download_name))
		response['Content-Type'] = 'application/octet-stream'
		response['Content-Disposition'] = 'attachment;filename="{0}"'.format(os.path.basename(download_name).encode('utf8'))
		return response

class CheckTaskView(LoginRequiredMixin,View):
	"""
	审核任务
	"""
	def get(self,request):
		all_unchecked_tasks=[]
		all_unchecked_front_tasks=FrontTask.objects.filter(complete_status=u'已创建',review_status=u'未审核').order_by('-create_time')
		all_unchecked_back_tasks=BackTask.objects.filter(complete_status=u'已创建',review_status=u'未审核').order_by('-create_time')
		all_unchecked_tasks.append(all_unchecked_front_tasks)
		all_unchecked_tasks.append(all_unchecked_back_tasks)
		return render(request,'check-task.html',{'all_unchecked_tasks':all_unchecked_tasks,'menu':'check-task'})
	
	def post(self,request):
		id=request.POST.get('id','')
		text=request.POST.get('text','')
		tag=request.POST.get('tag','')
		if id and text and tag == 'agree':
			if_ok=FrontTask.objects.filter(front_type__project_type=text.strip())
			if if_ok:
				FrontTask.objects.filter(id=id).update(review_status=u'已审核',reviewer=request.user.username)
				return HttpResponse('ok')
			else:
				BackTask.objects.filter(id=id).update(review_status=u'已审核',reviewer=request.user.username)
                                return HttpResponse('ok')
		elif id and text and tag == 'disagree':
			if_ok=FrontTask.objects.filter(front_type__project_type=text.strip())
                        if if_ok:
                                FrontTask.objects.filter(id=id).update(complete_status=u'已取消',review_status=u'已拒绝',reviewer=request.user.username)
                                return HttpResponse('ok')
                        else:
                                BackTask.objects.filter(id=id).update(complete_status=u'已取消',review_status=u'已拒绝',reviewer=request.user.username)
                                return HttpResponse('ok')
