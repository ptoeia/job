
from django.conf.urls import include, url,patterns,static
from django.contrib import admin
from django.conf import settings

urlpatterns = patterns('getjob.views',
    url(r'^$', 'job_information',name="index"),
    #url(r'^job/(?P<id>\d+)/$', 'job_edit'),
    url(r'^job/collect$', 'job_collect',),#ajax
    url(r'^job/(?P<id>\d+)/$','job_browse', name="job_browse"),
    url(r'^job/apply$','job_apply'),#ajax
    url(r'^logoff', 'logoff'),
    url(r'^signin', 'signin'),
    url(r'^copmpany', 'company_register', name="company"),
    url(r'^register', 'applicant_register', name="register"),
    url(r'^u/jobs/favourites', 'favourites_job', name="favourites"),
    url(r'^u/jobs', 'applicant_apply_history', name="applicant_jobs"),
    url(r'^u$', 'applicant_home', name='applicant'),
    url(r'^u/basic$', 'applicant_basic', name='u_basic'),
    url(r'^e/job/(?P<id>\d+)/edit$', 'job_edit', name="job_edit"),
    url(r'^e/job/delete$', 'job_delete', name="job_delete"),
    url(r'^e/jobs', 'company_jobs', name="company_jobs"),
    url(r'^e/resume', 'company_resume', name="resume"),
    url(r'^e$', 'company_home', name="company_home"),
    url(r'^username', 'username_validation'),
    url(r'^email', 'email_validation'),
    url(r'^city', 'city'),
    url(r'^joblist', 'job_publish', name="job_publish"),
    #test purpose
    url(r'^prov','prov'),
    url(r'^image','image'),
    url(r'^test','test'),
    #url(r'^media','logo'),
    #url(r'^accounts/login/$','django.contrib.auth.views.login', {'template_name': 'getjob/logon.html'})
               )
    #urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)