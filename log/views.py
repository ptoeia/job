# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.shortcuts import render,render_to_response
# Create your views here.
def index(request):
    return render_to_response('logindex.html',)

def index2(request):
    return render_to_response('index2.html',)
