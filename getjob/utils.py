# -*- coding:utf-8 -*-
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response,  RequestContext


# 分页函数
def pagination(request, jobs):
    paginator = Paginator(jobs, 7)  # show 7 job per page
    page_range = paginator.page_range  # page list
    try:
        leaf = int(request.GET.get('page', '1'))
    except ValueError:
        leaf = 1
    try:
        job_list = paginator.page(leaf)
    except(EmptyPage, InvalidPage):
        job_list = paginator.page(paginator.num_pages)
    return job_list, page_range


# 在模板中注入全局变量user
def job_render(request, template, context={}):
    context['user'] = request.user
    if not request.user.is_authenticated():
        context['user'] = ''
    return render_to_response(template, context)