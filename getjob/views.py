# -*- coding:utf-8 -*-
import os
import time
import json
import subprocess

from django.shortcuts import render, render_to_response, Http404, get_object_or_404, RequestContext
from django.forms.models import model_to_dict

from models import *
from form import JobPublishForm, applicantInformationForm, ApplicantRegisterForm, CompanyInformationForm

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound

from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.admin import User

from django.template import RequestContext

from django.db import connection,transaction
from django.db.models import Q, Count

from utils import pagination, job_render

from PIL import Image


def job_information(request):#首页index
    user = request.user.username
    session_key = request.session.get('sessionid')
    keyword = request.GET.get('q', '')
    if 'q' in request.GET:
        query = request.GET['q']
        qset = (
                 Q(job_type__icontains=query)|
                 Q(job_description__icontains=query)|
                 Q(publisher__name__icontains=query)
                )
        jobs = JobInformation.objects.filter(qset).order_by("-date_created")
        job_list, page_list = pagination(request, jobs)#分页函数
    else:
        try:
            jobs = JobInformation.objects.all().order_by("-date_created")
            job_list, page_list = pagination(request, jobs)
        except jobs.DoesNotExist:
            raise Http404("job dose not exist")
    return job_render(request, 'index.html', {'job_list': job_list,'page_list':page_list,
                                             'session_key':session_key,'keyword':keyword,})


def signin(request):
    error = False
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/getjob/')
        else:
            error=True
    error_message = u"用户名或密码不对"
    return render_to_response('logon.html', {'error_message': error_message,'error': error})


def logoff(request):
    logout(request)
    return HttpResponseRedirect('/getjob/')


@login_required
def applicant_home(request):  # 编辑用户信息
    login_user = request.user.username
    user_id = User.objects.only('id').get(username=login_user)
    applicant = ApplicantProfile.objects.get(user__username=login_user)
    if request.method == 'POST':
        form = applicantInformationForm(request.POST, request.FILES, instance=applicant)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/getjob/')
    p = get_object_or_404(ApplicantProfile,pk=user_id)
    form = applicantInformationForm(instance=p)
    return job_render(request,'applicant.html', {'form': form, 'login_user': login_user})


def applicant_register(request):  # 用户注册
    if request.method == 'POST':
        new_applicant_form = ApplicantRegisterForm(request.POST)
        if new_applicant_form.is_valid():
            username = new_applicant_form.cleaned_data['username']
            password = new_applicant_form.cleaned_data['password']
            email = new_applicant_form.cleaned_data['email']
            with transaction.atomic():
                User.objects.create_user(username=username, password=password, email=email)
                profile = ApplicantProfile(user = User.objects.get(username=username))
                profile.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return HttpResponseRedirect('/getjob/')
    else:
        new_applicant_form = ApplicantRegisterForm()
    return job_render(request, 'applicant_register.html', {'new_applicant': new_applicant_form})


@login_required
def applicant_basic(request):
    login_user = request.user.username
    user = get_object_or_404(User,username=login_user)
    basic_info_form = User(instance=user)
    if request.method == 'POST':
        if basic_info_form.is_valid():
            basic_info_form.save()
    return job_render(request, 'applicant_basic.html', {'form': basic_info_form,})


#  新建公司账号
@login_required
def company_register(request):
    login_user = request.user.username
    user = User.objects.get(username=login_user)
    try:
        Company.objects.get(contact=user.id)
        return HttpResponseRedirect('/getjob/e')
    except:
        if request.method == 'POST':
            #  新建公司账户信息
            new_company_form = CompanyInformationForm(request.POST,request.FILES)
            if new_company_form.is_valid():
                new_company = new_company_form.save(commit=False)
                new_company.contact = user
                new_company.save()
                return HttpResponseRedirect('/getjob/e')
        else:
            new_company_form = CompanyInformationForm
    return job_render(request,'company_register.html', {'new_company': new_company_form})


@login_required
def company_home(request):  # 查看修改公司信息
    login_user = request.user.username
    if request.method == 'POST':
        # 公司用户信息修改
        company = Company.objects.get(contact__username=login_user)
        new_company_form = CompanyInformationForm(request.POST, request.FILES, instance=company)
        if new_company_form.is_valid():
            new_company_form.save()
            return HttpResponseRedirect('/getjob/e')
    try:
        company = Company.objects.get(contact__username=login_user)
        new_company_form = CompanyInformationForm(instance=company)
    except company.DoesNotExist:
        return HttpResponse("未开通招聘功能")
        new_company_form = CompanyInformationForm()
    return job_render(request, 'company.html', {'new_company':new_company_form})


# 获取公司发布的职位
@login_required
def company_jobs(request):
    login_user = request.user.username
    published_jobs = JobInformation.objects.filter(
                                        publisher__contact__username=login_user
                                        ).annotate(num=Count('fk_apply')
                                        )
    job_list, page_list = pagination(request, published_jobs)
    return job_render(request,
                         'company_jobs.html', {
                         'job_list':job_list, 'page_list': page_list
                                })


# 公司简历管理
@login_required
def company_resume(request):
    return job_render(request, 'company_resume.html')


# 发布职位
@login_required
def job_publish(request):
    login_user = request.user.username
    company = Company.objects.get(contact__username=login_user)
    if request.method == 'POST':
        new_job_form = JobPublishForm(request.POST)
        if new_job_form.is_valid():
            new_job = new_job_form.save(commit=False)
            new_job.publisher = Company.objects.get(contact__username=login_user)
            new_job.save()
            return HttpResponseRedirect('e')
    else:
        new_job_form = JobPublishForm()
    return job_render(request,
                               'job_publish.html', {
                               'new_job_form': new_job_form, 'company': company
                                })


# 职位浏览
def job_browse(request, id):
    job = get_object_or_404(JobInformation, pk=int(id))
    company = get_object_or_404(Company, id=job.publisher.id)
    other_jobs = JobInformation.objects.filter(publisher=company).exclude(id=int(id))
    return job_render(request, 'job_browse.html', {
                               'job': job, 'company': company, 'job_id': job.id,
                               'other_jobs': other_jobs
                                })


#  职位收藏
def job_collect(request, result):
    result = u'<h4 class="notice">尚未登录！请先<a href="/getjob/signin/">登陆</a></h4>'
    if request.method == 'POST':
        login_user = request.user.username
        job_id = request.POST.get('job_id', '')
        if login_user:
            username = JobInformation.objects.filter(pk=job_id).\
                      values('publisher__contact__username')[0]['publisher__contact__username']
            if login_user == username:
                result = u'不能收藏自己发的职位'
            else:
                try:
                    user = get_object_or_404(User, username=request.user.username)
                    job = get_object_or_404(JobInformation, id=job_id)
                    JobFavourites.objects.get(user=user, job=job)
                    result = u'已收藏过'
                except JobFavourites.DoesNotExist:
                    JobFavourites.objects.create(user=user, job=job)
                    result = u'收藏成功'
    return HttpResponse(result)


# 职位申请
def job_apply(request, message):
    message = u'<h4 class="notice">尚未登录！请先<a href="/getjob/signin/">登陆</a></h4>'
    if request.method == 'POST':
        job_id = request.POST.get('job_id', '')
        login_user = request.user.username
        if login_user:
            username = JobInformation.objects.filter(pk=job_id).\
                      values('publisher__contact__username')[0]['publisher__contact__username']
            if login_user == username:
                message = u'不能收藏自己发的职位'
            else:
                user = get_object_or_404(User, username=login_user)
                job = get_object_or_404(JobInformation, pk=int(job_id))
                #  判断用户之前是否申请过该职位
                try:
                    message = u'之前已申请过'
                    apply = Apply.objects.get(candidates=user, position=job)
                    if apply.is_expired:
                        apply.is_expired = 0
                        apply.save()
                        message = u'申请成功'
                except:
                    Apply.objects.create(candidates=user, position=job)
                    message = u'申请成功'
    return HttpResponse(message)


# 编辑职位
@login_required
def job_edit(request, id):
    job = get_object_or_404(JobInformation, pk=int(id))
    job_candidates = Apply.objects.filter(position=int(id))
    if request.method == 'POST':
        job_edit_form = JobPublishForm(request.POST, instance=job)
        if job_edit_form.is_valid():
            job_edit_form.save()
            return HttpResponseRedirect('/getjob/e/job/%d/edit' % (int(id)))
    else:
        job_edit_form = JobPublishForm(instance=job)
    return job_render(request, 'job_edit.html', {
                                                  'edit_job': job_edit_form,
                                                  'id': id,
                                                  'candidates': job_candidates
                                                })


@login_required
def job_delete(request):
    if request.method == 'POST':
        job_id = request.POST.get('job_id', '')
        JobInformation.objects.filter(pk=job_id).delete()
    return HttpResponseRedirect('/getjob/e/jobs')


# 求职者的工作申请记录
@login_required
def applicant_apply_history(request):
    login_user = request.user.username
    apply_history = JobInformation.objects.filter(
                                                   fk_apply__candidates__username=login_user).values(
                                                   'id', 'job_type', 'publisher__id',
                                                   'publisher__name', 'fk_apply__date_created'
                                                   )
    job_list, page_list = pagination(request, apply_history)
    return job_render(request, 'applicant_apply.html', {
                                                         'job_list': job_list,
                                                         'page_list': page_list,
                                                          })


@login_required
def favourites_job(request):
    login_user = request.user.username
    favourites_jobs = JobInformation.objects.only('job_type','publisher').filter(fk_job_id__user__username=login_user)
    return job_render(request, 'applicant_favourites.html', {'favourites_jobs': favourites_jobs})


def username_validation(request):
    input_username = request.GET.get('input_username', None)
    error = u'此用户名已经注册'
    if not User.objects.filter(username=input_username):
        error = ''
    return HttpResponse(error)


def email_validation(request):
    input_email = request.GET.get('input_email',None)
    error = u'此邮箱已经注册'
    if not User.objects.filter(email=input_email):
        error = ''
    return HttpResponse(error)


# 获取省/直辖市数据
def prov(request):
    #prov = []
    provices_list = list(Area.objects.filter(parent_code__isnull=True).values('area_name','area_code'))
    #citys.py = Area.objects.filter.values('area_code','area_name')
    #prov.append(provices)
    #prov = list(provices)
    #serializers
    return HttpResponse(json.dumps(provices_list),content_type='application/json')


# 获取城市列表
def city(request):
    #prov = []
    province = request.POST.get('province')
    city_list = list(Area.objects.filter(parent_code=province).values('area_name','area_code'))
    #citys.py = Area.objects.filter.values('area_code','area_name')
    #prov.append(provices)
    #prov = list(provices)
    #serializers
    return HttpResponse(json.dumps(city_list),content_type='application/json')
    #return HttpResponse('were')


def prov_test(requet):
    #response_data=[{'area_code':100,'area_name':200},{'area_code':300,'area_name':400}]
    response_data = "{'area_code':100,'area_name':200}"
    #return HttpResponse(json.dumps(response_data), content_type='application/json')
    return HttpResponse(response_data)


def test(request):
    return job_render(request, 'test5.html')



def image(request):
    img_dest_path = '/Users/admin/PycharmProjects/parttimejob/job/getjob/upload/'
    if request.method == 'POST':
        if 'files' in request.FILES:
            origin_image = request.FILES['files']
            img_name = origin_image.name
            img_full_name = img_dest_path+img_name
            img_name = time.strftime('%Y%m%d%H%M%S')+img_name if os.path.exists(img_dest_path+img_name) else img_name
            try:
                img = Image.open(origin_image)
                if img.size[0] > 200 or img.size[1] > 160:
                    img.thumbnail((200,160),Image.ANTIALIAS)
                img.verify()
                img.save(img_dest_path+img_name)
                imgurl = '/getjob/media/images/logos/'+img_name
                return job_render('test5.html',{'imgname':img_name,'imgurl':imgurl})
                return(imgurl)
            except Exception,e:
                return HttpResponse("Error %s"%e)
                 #return("Error %s" %e)
        else:
            return HttpResponse(u"请选择文件")
            # return(u'请选择文件')
    return job_render(request, 'test5.html')





