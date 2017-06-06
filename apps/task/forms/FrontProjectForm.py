#coding:utf8

from django import  forms
from task.models import FrontType,FrontHost

class FrontProjectForm(forms.Form):
	project_name=forms.CharField(required=False,max_length=30,widget=forms.TextInput(attrs={'class': "form-control"}))
	front_type=forms.CharField(required=False,widget=forms.Select(attrs={'class': "form-control"}))
	front_host=forms.CharField(required=False,widget=forms.Select(attrs={'class': "form-control"}))

	def __init__(self,*args,**kwargs):
		super(FrontProjectForm,self).__init__(*args,**kwargs)
		self.fields['front_type'].widget.choices=FrontType.objects.all().values_list('id','project_type')
		self.fields['front_host'].widget.choices=FrontHost.objects.all().values_list('id','project_host')
		
	
