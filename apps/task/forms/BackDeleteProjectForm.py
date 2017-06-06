#coding:utf8

from django import  forms
from task.models import BackProject

class BackDeleteProjectForm(forms.Form):
	back_project=forms.CharField(widget=forms.Select(attrs={'class': "form-control"}))

	def __init__(self,*args,**kwargs):
		super(BackDeleteProjectForm,self).__init__(*args,**kwargs)
		self.fields['back_project'].widget.choices=BackProject.objects.all().values_list('id','project_name')
		
	
