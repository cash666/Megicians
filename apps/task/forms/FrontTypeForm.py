#coding:utf8

from django import  forms
from task.models import FrontType

class FrontTypeForm(forms.ModelForm):
	class Meta:
		model=FrontType
		fields=['project_type']

