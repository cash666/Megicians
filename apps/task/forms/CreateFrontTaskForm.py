#coding:utf8

from django import  forms
from task.models import FrontProject,FrontType,FrontHost
from users.models import UserProfile

class CreateFrontTaskForm(forms.Form):
	task_name=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': "form-control"}))
	front_project=forms.CharField(widget=forms.Select(attrs={'class': "form-control"}))
	#front_type=forms.CharField(widget=forms.Select(attrs={'class': "form-control"}))
	#front_host=forms.CharField(widget=forms.Select(attrs={'class': "form-control"}))
	project_version=forms.IntegerField(widget=forms.NumberInput(attrs={'class': "form-control"}))
	project_md5=forms.CharField(max_length=64,widget=forms.TextInput(attrs={'class': "form-control"}))
	task_cc=forms.CharField(max_length=100,required=False,widget=forms.SelectMultiple(attrs={'class': "form-control"}))
	operator=forms.CharField(max_length=32,required=False,widget=forms.Select(attrs={'class': "form-control"}))
	description=forms.CharField(required=False,max_length=256,widget=forms.widgets.Textarea(attrs={'class':'form-control','placeholder':u'任务备注','rows':5}))	

	def __init__(self,*args,**kwargs):
		super(CreateFrontTaskForm,self).__init__(*args,**kwargs)
		self.fields['front_project'].widget.choices=FrontProject.objects.all().values_list('id','project_name')
		#self.fields['front_type'].widget.choices=FrontType.objects.all().values_list('id','project_type')
		#self.fields['front_host'].widget.choices=FrontHost.objects.all().values_list('id','project_host')
		self.fields['task_cc'].widget.choices=UserProfile.objects.all().values_list('username','username')
                self.fields['operator'].widget.choices=UserProfile.objects.all().values_list('id','username')
	
