#coding:utf8

from celery.decorators import task
from django.core.mail import send_mail
from  megicians.settings import EMAIL_FROM
import os

@task(name='Send email after releasing version')
def SendEmail(EMAIL_TITLE,EMAIL_BODY,EMAIL_TO):
	send_mail(EMAIL_TITLE,EMAIL_BODY,EMAIL_FROM,EMAIL_TO)
