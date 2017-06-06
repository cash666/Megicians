#coding:utf8

from django import  forms
from task.models import BackProject,BackGroup

class BackGroupForm(forms.Form):
	#id=forms.CharField(widget=forms.HiddenInput(),required=False)
	project_group=forms.CharField(max_length=32,widget=forms.TextInput(attrs={'class': "form-control"}))
	hosts=forms.CharField(max_length=128,widget=forms.TextInput(attrs={'class': "form-control"}))
	back_project=forms.CharField(widget=forms.Select(attrs={'class': "form-control"}))

	def __init__(self,*args,**kwargs):
		super(BackGroupForm,self).__init__(*args,**kwargs)
		self.fields['back_project'].widget.choices=BackProject.objects.all().values_list('id','project_name')
		
	
