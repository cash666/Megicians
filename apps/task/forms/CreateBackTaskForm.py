#coding:utf8

from django import  forms
from task.models import BackProject,BackGroup
from users.models import UserProfile

class CreateBackTaskForm(forms.Form):
	task_name=forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class': "form-control"}))
	back_project=forms.CharField(widget=forms.Select(attrs={'class': "form-control"}))
	back_group=forms.CharField(widget=forms.Select(attrs={'class': "form-control"}))
	project_version=forms.IntegerField(widget=forms.NumberInput(attrs={'class': "form-control"}))
	project_md5=forms.CharField(max_length=64,widget=forms.TextInput(attrs={'class': "form-control"}))
	attachment=forms.FileField(required=False)
	task_cc=forms.CharField(max_length=100,required=False,widget=forms.SelectMultiple(attrs={'class': "form-control"}))
	operator=forms.CharField(max_length=32,widget=forms.Select(attrs={'class': "form-control"}))
	description=forms.CharField(required=False,max_length=256,widget=forms.widgets.Textarea(attrs={'class':'form-control','placeholder':u'任务备注','rows':5}))	

	def __init__(self,*args,**kwargs):
		super(CreateBackTaskForm,self).__init__(*args,**kwargs)
		self.fields['back_project'].widget.choices=BackProject.objects.all().values_list('id','project_name')
		self.fields['back_group'].widget.choices=BackGroup.objects.all().values_list('id','project_group')
		self.fields['task_cc'].widget.choices=UserProfile.objects.all().values_list('username','username')
		self.fields['operator'].widget.choices=UserProfile.objects.all().values_list('id','username')
		
	
