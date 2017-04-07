#__author__='abc'

from django.conf.urls import include, url,patterns,static
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('log.views',
    url(r'^$', 'index'),
    url(r'^1','index2'),
               )
