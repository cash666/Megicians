#coding:utf8

from __future__ import unicode_literals
from django.db.models import Q
from django.db import models
from django.http.request import HttpRequest

# Create your models here.
class FrontTask(models.Model):
	"""
	前端任务表
	"""
	task_name=models.CharField(max_length=64,verbose_name=u'任务名称')
	front_project=models.ForeignKey('FrontProject')
	front_type=models.ForeignKey('FrontType')
	front_host=models.ForeignKey('FrontHost')
	project_version=models.IntegerField(verbose_name=u'项目构建号')
	project_md5=models.CharField(max_length=64,verbose_name=u'项目md5值')
	creater=models.CharField(max_length=16,verbose_name=u'任务创建人')
	operator=models.CharField(max_length=16,verbose_name=u'任务操作人')
	cc=models.CharField(max_length=64,verbose_name=u'任务抄送人',default='')
	complete_status=models.CharField(max_length=32,verbose_name=u'完成状态')
	review_status=models.CharField(max_length=32,verbose_name=u'审核状态')
	reviewer=models.CharField(max_length=32,default='',verbose_name=u'审核人')
	create_time=models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')
	description=models.TextField(null=True,blank=True,verbose_name=u'备注')

	class Meta:
		verbose_name=u'前端任务'
		verbose_name_plural=verbose_name
		db_table='front_task'
		ordering=['-create_time']
		permissions = (
			('check_front_tasks','Can check all front tasks'),
		)

	def __unicode__(self):
		return '{0} {1}_{2} {3}'.format(self.task_name,self.project_version,self.project_md5,self.operator)

class BackTask(models.Model):
        """
        后端任务表
        """
        task_name=models.CharField(max_length=64,verbose_name=u'任务名称')
	back_project=models.ForeignKey('BackProject')
	back_group=models.ForeignKey('BackGroup')
        project_version=models.IntegerField(verbose_name=u'项目构建号')
        project_md5=models.CharField(max_length=64,verbose_name=u'项目md5值')
        creater=models.CharField(max_length=16,verbose_name=u'任务创建人')
        operator=models.CharField(max_length=16,verbose_name=u'任务操作人')
        cc=models.CharField(max_length=64,verbose_name=u'任务抄送人',default='')
	complete_status=models.CharField(max_length=32,verbose_name=u'完成状态')
        review_status=models.CharField(max_length=32,verbose_name=u'审核状态')
	reviewer=models.CharField(max_length=32,default='',verbose_name=u'审核人')
        attachment=models.FileField(upload_to='uploads',null=True,blank=True,verbose_name=u'任务附件')
        create_time=models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')
        description=models.TextField(null=True,blank=True,verbose_name=u'备注')

        class Meta:
                verbose_name=u'后端任务'
                verbose_name_plural=verbose_name
                db_table='back_task'
                ordering=['-create_time']
		permissions = (
                        ('check_back_tasks','Can check all back tasks'),
                )

        def __unicode__(self):
                return '{0} {1}_{2} {3}'.format(self.task_name,self.project_version,self.project_md5,self.operator)

class BackProject(models.Model):
	"""
	后端项目表
	"""
	project_name=models.CharField(max_length=64,verbose_name=u'项目名称')
	creater=models.CharField(max_length=16,verbose_name=u'项目创建人')
	create_time=models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')

	class Meta:
                verbose_name=u'后端项目'
                verbose_name_plural=verbose_name
                db_table='back_project'
                ordering=['-create_time']

	def __unicode__(self):
		return self.project_name,self.creater

class BackGroup(models.Model):
	"""
	后端项目组表
	"""
	project_group=models.CharField(max_length=64,verbose_name=u'项目组')
	back_project=models.ForeignKey(BackProject)
	hosts=models.CharField(max_length=128,verbose_name=u'项目组主机')
	creater=models.CharField(max_length=16,verbose_name=u'项目组创建人')
        create_time=models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')

	class Meta:
                verbose_name=u'后端项目组'
                verbose_name_plural=verbose_name
                db_table='back_group'
                ordering=['-create_time']

        def __unicode__(self):
                return self.project_group,self.hosts,self.creater

class FrontProject(models.Model):
	"""
	前端项目表
	"""
	project_name=models.CharField(max_length=64,verbose_name=u'项目名称')
	front_type=models.ForeignKey('FrontType')
	front_host=models.ForeignKey('FrontHost')
	creater=models.CharField(max_length=16,verbose_name=u'项目组创建人',default='')
        create_time=models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')
	
	class Meta:
		verbose_name=u'前端项目'
                verbose_name_plural=verbose_name
                db_table='front_project'

	def __unicode__(self):
		return self.project_name	

class FrontType(models.Model):
	"""
	前端项目类型
	"""
	project_type=models.CharField(max_length=64,verbose_name=u'项目类型')
	creater=models.CharField(max_length=16,verbose_name=u'项目类型创建人',default='')
        create_time=models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')

	class Meta:
                verbose_name=u'前端项目类型'
                verbose_name_plural=verbose_name
                db_table='front_type'
        
        def __unicode__(self):
                return self.project_type

class FrontHost(models.Model):
	"""
	前端项目主机
	"""
	project_host=models.CharField(max_length=64,verbose_name=u'项目主机')
	creater=models.CharField(max_length=16,verbose_name=u'项目主机创建人',default='')
        create_time=models.DateTimeField(auto_now_add=True,verbose_name=u'创建时间')
	
	class Meta:
                verbose_name=u'前端项目主机'
                verbose_name_plural=verbose_name
                db_table='front_host'

        def __unicode__(self):
                return self.project_host
