# -*- coding:utf-8 -*-
from django.core.urlresolvers import reverse
from django.djangorestframework.views import View
from django.djangorestframework.resources import ModelResource
from models import *

class jobresources(ModelResource):
    model = JobInformation
    fields = ('job_id', 'job_type', 'job_description' , 'salary', 'city', 'valid_period')
