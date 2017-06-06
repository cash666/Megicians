#coding:utf8
from django import forms
from models import UserProfile
from django.core.exceptions import ValidationError

class UserRegistrationFrom(forms.Form):
    username = forms.CharField(required=True,min_length=2,max_length=15,
                                   error_messages={"required":"用户名不能为空","max_length":"长度必须小于15","min_length":"长度必须大于4"})
    register_password = forms.CharField(required=True,min_length=6,max_length=15,
                                        error_messages={"required":"密码不能为空","max_length":"长度必须小于15","min_length":"长度必须大于4"})
    register_password2 = forms.CharField(required=True,min_length=6,max_length=15,
                                         error_messages={"required":"确认密码不能为空","max_length":"长度必须小于15","min_length":"长度必须大于4"})
    email=forms.EmailField(required=True)
    groupid=forms.CharField(required=True)
    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        try:
            UserProfile.objects.get(username=username)
            raise ValidationError('用户已经存在')
        except UserProfile.DoesNotExist:
            return username
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            UserProfile.objects.get(email=email)
            raise ValidationError('该邮箱已经注册')
        except UserProfile.DoesNotExist:
            return email
    def _clean_new_password2(self):
        password1 = self.cleaned_data.get('register_password')
        password2 = self.cleaned_data.get('register_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次密码不一致！')
    def clean(self):
        self._clean_new_password2()

class UserModifyPasswd(forms.Form):
    username = forms.CharField(required=True,min_length=4,max_length=15,
                                   error_messages={"required":"用户名不能为空","max_length":"长度必须小于15","min_length":"长度必须大于4"})
    register_password = forms.CharField(required=True,min_length=6,max_length=15,
                                        error_messages={"required":"密码不能为空","max_length":"长度必须小于15","min_length":"长度必须大于4"})
    register_password2 = forms.CharField(required=True,min_length=6,max_length=15,
                                         error_messages={"required":"确认密码不能为空","max_length":"长度必须小于15","min_length":"长度必须大于4"})
    def clean_username(self):
        username = self.cleaned_data.get('username').lower()
        try:
            UserProfile.objects.get(username=username)
            return username
        except UserProfile.DoesNotExist:
            raise ValidationError('用户已经存在')

    def _clean_new_password2(self):
        password1 = self.cleaned_data.get('register_password')
        password2 = self.cleaned_data.get('register_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(u'两次密码不一致！')

    def clean(self):
        self._clean_new_password2()
