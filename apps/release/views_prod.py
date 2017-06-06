#coding:utf8

from django.shortcuts import render,redirect,HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import View
from task.models import FrontTask,BackTask
from django.db.models import Q
from utils.mixin_utils import LoginRequiredMixin
from utils.ansible_api import MyRunner
from django.utils.safestring import mark_safe
import json
import os
import time
import tarfile
import pycurl
# Create your views here.


class ReleaseTaskView(LoginRequiredMixin,View):
	"""
	发布任务
	"""
	def get(self,request):
		front_task_list=FrontTask.objects.filter(operator=request.user.username,complete_status=u'已创建',review_status=u'已审核').order_by('create_time')
		back_task_list=BackTask.objects.filter(operator=request.user.username,complete_status=u'已创建',review_status=u'已审核').order_by('create_time')
		return render(request,'release-task.html',{'front_task_list':front_task_list,'back_task_list':back_task_list,'FrontTask':FrontTask,'BackTask':BackTask,'menu':'release-task'})

	def post(self,request):
		id=request.POST.get('id','')
		type=request.POST.get('type','')
		if id and type == 'back':
			back_task_obj=BackTask.objects.get(id=id)
			back_project=back_task_obj.back_project.project_name
			back_group=back_task_obj.back_group.project_group
			back_hosts=back_task_obj.back_group.hosts
			tomcatname=back_project
			tagname='%s_%s' % (back_task_obj.project_version,back_task_obj.project_md5)
			result={}
			content=''
			log="logs/back_release.log"
			if back_hosts.find(',')>0:
				back_host_list=back_hosts.split(',')
			else:
				back_host_list=[back_hosts]
			try:
				r=MyRunner(back_host_list)
				r.run_playbook('root',tomcatname,tagname,back_host_list)
				ret=r.get_result()
			except Exception,e:
				content=u'<h2 style="color:red">本次任务发布失败!</h2><br/>'
				content+='<hr/>'
				content+=u'<strong>报错信息:%s<strong>' % e
				result['status']='fail'
				result['content']=content
				return HttpResponse(json.dumps(result))
			if ret:
				if not ret['failed'] and not ret['unreachable']:
                                	content+=u'<h2 style="color:green">本次任务发布成功!</h2><br/>'
					content+='<hr/>'
					result['status']='ok'
					EMAIL_TITLE=u'本次任务发布成功!'
					EMAIL_BODY=u'您本次的任务:%s(项目:%s,项目主机:%s,构建号:%s,Revesion:%s)发布成功！' % (back_task_obj.task_name,back_project,back_hosts,back_task_obj.project_version,back_task_obj.project_md5)
					f=open(log,'a')
					log_content='%s %s %s success!\n' % (time.strftime('%Y-%m-%d %H:%M:%S'),tomcatname,tagname)
					f.write(log_content)
					f.close()
					BackTask.objects.filter(id=id).update(complete_status=u'已完成',operator=request.user.username)
                                if ret['failed'] or ret['unreachable']:
                                	content=u'<h2 style="color:red">本次任务发布失败!</h2><br/>'
					content+='<hr/>'
					result['status']='fail'
					EMAIL_TITLE=u'本次任务发布失败!'
					EMAIL_BODY=u'您本次的任务:%s(项目:%s,项目主机:%s,构建号:%s,Revesion:%s)发布失败！' % (back_task_obj.task_name,back_project,back_hosts,back_task_obj.project_version,back_task_obj.project_md5)
					f=open(log,'a')
                                        log_content='%s %s %s failed!\n' % (time.strftime('%Y-%m-%d %H:%M:%S'),tomcatname,tagname)
                                        f.write(log_content)
                                        f.close()
				for k,v in ret.items():
					if k == 'failed' and v:
						content+=u'<p>发布失败的IP有:<p><br/>'
						for k1,v1 in v.items():
							content+=u'<strong style="color:red">%s</strong><br/>' % k1
							content+=u'<strong>失败原因:%s<strong><br/>' % v1
							content+='-'*30
							content+='<br/>'
					elif k == 'success' and v:
						content+=u'<p>本次发布成功的IP有:</p><br/>'
						for k2,v2 in v.items():
							content+='<strong style="color:green">%s</strong><br/>' % k2
							content+='-'*30
							content+='<br/>'
					elif k == 'unreachable' and v:
						content+=u'<p>主机不通的IP有:</p><br/>'
						for k3,v3 in v.items():
							content+='<strong style="color:red">%s</strong><br/>' % k3
							content+=u'<strong>失败原因:%s<strong><br/>' % v3
							content+='-'*30
							content+='<br/>'
			result['content']=mark_safe(content)
			if request.user.email:
				EMAIL_TO=[request.user.email,]
			else:
				EMAIL_TO=['caoshuai@lifang.com',]
			try:
				#版本发布完成后邮件进行通知
				from .tasks import SendEmail
				SendEmail.delay(EMAIL_TITLE,EMAIL_BODY,EMAIL_TO)
			except Exception,e:
				pass	
			return HttpResponse(json.dumps(result))
		elif id and type == 'front':
			front_task_obj=FrontTask.objects.get(id=id)
			front_project=front_task_obj.front_project.project_name
			front_type=front_task_obj.front_type.project_type
			front_host=front_task_obj.front_host.project_host
			project_version=front_task_obj.project_version
			project_md5=front_task_obj.project_md5
			log="logs/front_release.log"
			content=''
			result={}
			package_tar_dir="/lf/code/packages/FE/%s.tar_%s_%s" % (front_project,project_version,project_md5)
			package_dir="/lf/code/version/%d_%s" % (project_version,project_md5)
			if os.path.exists(package_tar_dir):
				if os.path.isdir(package_dir):
					pass
				else:
					os.mkdir(package_dir)
    				t = tarfile.open(package_tar_dir,"r:")
				import sys
				reload(sys)
				sys.setdefaultencoding('utf-8')
    				t.extractall(path=package_dir)
    				t.close()
				if front_type == 'cdn':
					try:
						r=MyRunner([front_host,])
						date=time.strftime("%Y-%m-%d-%H-%M", time.localtime())
						r.run('shell','[ -d /usr/local/nginx/html/cdn/%s ] || mkdir /usr/local/nginx/html/cdn/%s' % (front_project.lower(),front_project.lower()))
						r.run('shell','/bin/cp -a /usr/local/nginx/html/cdn/%s /root/BackUp/cdn/%s.%s' % (front_project.lower(),front_project.lower(),date))
						r.run('synchronize','src=/lf/code/version/%d_%s/  dest=/usr/local/nginx/html/cdn/%s/ delete=yes rsync_opts=--exclude=config.js' % (project_version,project_md5,front_project.lower()))
						r.run('shell','chown -R zabbix. /usr/local/nginx/html/cdn/')
						ret=r.get_result()		
					except Exception,e:
						content=u'<h2 style="color:red">本次任务发布失败!</h2><br/>'
                                		content+='<hr/>'
                                		content+=u'<strong>报错信息:%s<strong>' % e
                                		result['status']='fail'
                                		result['content']=content
                                		return HttpResponse(json.dumps(result))
					else:
						if front_project.lower() == 'wkweb_fe':
							c = pycurl.Curl()
        						c.setopt(pycurl.URL, 'http://www.wkzf.com/resetFrontVersion.rest')
        						c.perform()
        						c.close()
						elif front_project.lower() == 'wkwap_fe':
							c = pycurl.Curl()
        						c.setopt(pycurl.URL, 'https://m.wkzf.com/resetFrontVersion.rest')
        						c.perform()
        						c.close()
				elif front_type == 'php':
					try:
                                                r=MyRunner([front_host,])
                                                date=time.strftime("%Y-%m-%d-%H-%M", time.localtime())
                                                r.run('shell','[ -d /usr/local/nginx/html/php/%s ] || mkdir /usr/local/nginx/html/php/%s' % (front_project.lower(),front_project.lower()))
                                                r.run('shell','/bin/cp -a /usr/local/nginx/html/php/%s /root/BackUp/cdn/%s.%s' % (front_project.lower(),front_project.lower(),date))
                                                r.run('synchronize','src=/lf/code/version/%d_%s/  dest=/usr/local/nginx/html/php/%s/ delete=yes rsync_opts=--exclude=config.js' % (project_version,project_md5,front_project.lower()))
                                                r.run('shell','chown -R zabbix. /usr/local/nginx/html/php/')
                                                ret=r.get_result()
                                        except Exception,e:
                                                content=u'<h2 style="color:red">本次任务发布失败!</h2><br/>'
                                                content+='<hr/>'
                                                content+=u'<strong>报错信息:%s<strong>' % e
                                                result['status']='fail'
                                                result['content']=content
                                                return HttpResponse(json.dumps(result))
				elif front_type == 'node':
                                        try:
                                                r=MyRunner([front_host,])
                                                date=time.strftime("%Y-%m-%d-%H-%M", time.localtime())
                                                r.run('shell','[ -d /usr/local/nginx/html/%s ] || mkdir /usr/local/nginx/html/%s' % (front_project.lower(),front_project.lower()))
                                                r.run('shell','/bin/cp -a /usr/local/nginx/html/%s /root/BackUp/cdn/%s.%s' % (front_project.lower(),front_project.lower(),date))
                                                r.run('synchronize','src=/lf/code/version/%d_%s/  dest=/usr/local/nginx/html/%s/ delete=yes recursive=yes' % (project_version,project_md5,front_project.lower()))
                                                r.run('shell','chown -R zabbix. /usr/local/nginx/html/')
                                                ret=r.get_result()
                                        except Exception,e:
                                                content=u'<h2 style="color:red">本次任务发布失败!</h2><br/>'
                                                content+='<hr/>'
                                                content+=u'<strong>报错信息:%s<strong>' % e
                                                result['status']='fail'
                                                result['content']=content
                                                return HttpResponse(json.dumps(result))
				if ret:
					if not ret['failed'] and not ret['unreachable']:
                                        	content+=u'<h2 style="color:green">本次任务发布成功!</h2><br/>'
                                        	content+='<hr/>'
                                        	result['status']='ok'
						EMAIL_TITLE=u'本次任务发布成功!'
                                        	EMAIL_BODY=u'您本次的任务:%s(项目:%s,项目类型:%s,项目主机:%s,构建号:%s,Revesion:%s)发布成功！' % (front_task_obj.task_name,front_project,front_type,front_host,project_version,project_md5)
                                        	FrontTask.objects.filter(id=id).update(complete_status=u'已完成',operator=request.user.username)
						f=open(log,'a')
                                        	log_content='%s %s %s_%s success!\n' % (time.strftime('%Y-%m-%d %H:%M:%S'),front_project,project_version,project_md5)
                                        	f.write(log_content)
                                        	f.close()
                                	if ret['failed'] or ret['unreachable']:
                                        	content=u'<h2 style="color:red">本次任务发布失败!</h2><br/>'
                                        	content+='<hr/>'
                                        	result['status']='fail'
						EMAIL_TITLE=u'本次任务发布失败!'
                                                EMAIL_BODY=u'您本次的任务:%s(项目:%s,项目类型:%s,项目主机:%s,构建号:%s,Revesion:%s)发布失败！' % (front_task_obj.task_name,front_project,front_type,front_host,project_version,project_md5)
						f=open(log,'a')
                                                log_content='%s %s %s_%s failed!\n' % (time.strftime('%Y-%m-%d %H:%M:%S'),front_project,project_version,project_md5)
                                                f.write(log_content)
                                                f.close()
                                	for k,v in ret.items():
                                        	if k == 'failed' and v:
                                                	for k1,v1 in v.items():
                                                        	content+=u'<p>发布失败的IP有:<p><br/>'
                                                        	content+=u'<strong color="color:red">%s</strong><br/>' % k1
                                                        	content+=u'<strong>失败原因:%s<strong><br/>' % v1
                                        	elif k == 'success' and v:
                                                	for k2,v2 in v.items():
                                                        	content+=u'<p>本次发布成功的IP有:</p><br/>'
                                                        	content+='<strong>%s</strong><br/>' % k2
                                        	elif k == 'unreachable' and v:
                                                	for k3,v3 in v.items():
                                                        	content+=u'<p>主机不通的IP有:</p><br/>'
                                                        	content+='<strong>%s</strong><br/>' % k3
                                                        	content+=u'<strong>失败原因:%s<strong><br/>' % v3
					result['content']=mark_safe(content)
					if request.user.email:
                                		EMAIL_TO=[request.user.email,]
                        		else:
                                		EMAIL_TO=['caoshuai@lifang.com',]
                        		try:
                               		 	#版本发布完成后邮件进行通知
                                		from .tasks import SendEmail
                                		SendEmail.delay(EMAIL_TITLE,EMAIL_BODY,EMAIL_TO)
                        		except Exception,e:
                                		pass
                        		return HttpResponse(json.dumps(result))
			else:
				result['status']='fail'
				result['content']=u'tar包不存在'
				return HttpResponse(json.dumps(result))
