#coding:utf8

from django import template

register = template.Library()

@register.simple_tag
def page_start(num):
	return 5*num-5

@register.simple_tag
def add(num):
        return num+1

@register.simple_tag
def split_str(str):
	if str:		
		new_str=str.split('/')[1]		
		return new_str

@register.simple_tag
def get_len(list):
	return len(list)

@register.simple_tag
def remaining(num1,num2):
	return num1%num2
