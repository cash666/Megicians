#coding:utf8

from django import  forms
from task.models import FrontHost

class FrontHostForm(forms.ModelForm):
	class Meta:
		model=FrontHost
		fields=['project_host']

