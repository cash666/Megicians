#coding:utf8

from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser,Group,Permission
from task.models import FrontTask,BackTask
# Create your models here.

class UserProfile(AbstractUser):
	nick_name=models.CharField(max_length=50,verbose_name=u"昵称",default="")
	head_image=models.ImageField(upload_to="image/",default=u"image/default.png",max_length=100,verbose_name=u'头像')

	class Meta:
		verbose_name="用户信息"
		verbose_name_plural=verbose_name

	def uncompleted_front_task(self):
		return FrontTask.objects.filter(complete_status=u'已创建',operator=self.username).count()

	def uncompleted_back_task(self):
                return BackTask.objects.filter(complete_status=u'已创建',operator=self.username).count()

	def unreviewed_front_task(self):
                return FrontTask.objects.filter(complete_status=u'已创建',review_status=u'未审核').count()

	def unreviewed_back_task(self):
                return BackTask.objects.filter(complete_status=u'已创建',review_status=u'未审核').count()

	def __unicode__(self):
		return self.username
