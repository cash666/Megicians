#coding:utf8

from django import  forms
from task.models import BackProject

class BackProjectForm(forms.ModelForm):
	class Meta:
		model=BackProject
		fields=['project_name']

