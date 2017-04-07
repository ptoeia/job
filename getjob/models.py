# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.admin import User
from datetime import datetime
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from citys import city_choices


class ApplicantProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    username = models.CharField(max_length=32, verbose_name=u'真实姓名', blank=True, default=u'unknow')
    avatar = ProcessedImageField(verbose_name=u'头像', upload_to='images/avatar',
                                 default='images/avatar/dft.jpg',
                                 processors=[ResizeToFill(110,80)],
                                 format='jpeg',
                                 options={'quality': 60})

    birth = models.DateField(max_length=12,verbose_name=u'出生日期', blank=True, null=True)
    phone = models.CharField(max_length=12,verbose_name=u'手机号码', unique=True, null=True)
    address = models.CharField(max_length=120, verbose_name=u'住址', blank=True,null=True)
    degree = (
               (1, u'大专'),
               (2, u'本科'),
               (3, u'研究生'),
               (4, u'博士'),
             )
    education_degree = models.PositiveSmallIntegerField(choices=degree,verbose_name=u'学历', blank=True, null=True)
    gender = models.PositiveSmallIntegerField(choices=((1, u'男'),(2, u'女')), verbose_name=u'性别', blank=True, null=True)
    work_experiences = models.TextField(max_length=600, verbose_name=u'工作经验描述', blank=True, null=True)
    #date_joined = models.DateTimeField(verbose_name=u'加入时间')

    def __unicode__(self):
        return self.user_id

    class Meta:
        db_table = "applicant_profile"


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    contact = models.ForeignKey(User, related_name='fk_contact_user', on_delete=models.SET_NULL, blank=True, null=True)
    logo_thumbnail = ProcessedImageField(db_column="logo", upload_to='images/logos', default='images/logos/pic6.jpg',
                                         verbose_name=u'上传logo',
                                         processors=[ResizeToFill(110, 80)],
                                         format='JPEG',
                                         options={'quality': 60})

    name = models.CharField(max_length=60,verbose_name=u'公司名称', unique=True)
    telephone = models.CharField(max_length=50, verbose_name=u'公司座机', blank=True, null=True)
    address = models.CharField(max_length=30, verbose_name=u'详细地址', null=True, blank=True)
    contacts_name = models.CharField(max_length=32, verbose_name=u'联系人姓名',null=True, blank=True)
    website = models.URLField(verbose_name=u'公司网址', max_length=50, null=True,blank=True)
    #date_joined =models.DateTimeField(verbose_name=u'加入时间')
    industry_choices = (
        (1, u'互联网'), (2, u'广告'), (3, u'游戏'), (4, u'电子商务'), (5, u'新媒体'), (6, u'教育'),
        (7, u'金融'), (8, u'通信'), (9, u'健康医疗'), (10, u'硬件'), (11, u'IT/软件'),(12, u'其他'),
       )
    industry = models.PositiveSmallIntegerField(verbose_name=u'所属行业', choices=industry_choices, null=True, blank=True)
    character_choices = (
                        (1, u'私企'), (2, u'国企'),(3, u'欧美外企'), (4, u'日企'), (5, u'中外合资')
                      )
    nature = models.PositiveSmallIntegerField(verbose_name=u'公司性质', choices=character_choices, null=True, blank=True)
    scale_choices = (
                 (1, u'15人以下'), (2, u'15-50人'), (3, u'50-150人'),
                 (4, u'150-500人'), (5, u'500-2000人'), (6, u'2000人以上'),
                 )
    scale = models.PositiveSmallIntegerField(verbose_name=u'公司人数规模', choices=scale_choices, null=True, blank=True)
    advantages = models.CharField(verbose_name=u'一句话亮点', max_length=50, null=True, blank=True)
    introduction = models.CharField(verbose_name=u'公司简介', max_length=200, null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = "company"


class Area(models.Model):
    area_code = models.CharField(primary_key=True,max_length=20)
    grade = models.CharField(max_length=20)
    area_name = models.CharField(max_length=20)
    parent_code = models.CharField(max_length=20)

    def __unicode__(self):
        return self.area_name

    class Meta:
        db_table = 's_area'


class JobInformation(models.Model):
    id = models.AutoField(primary_key=True)
    publisher = models.ForeignKey(Company,related_name='fk_publisher_company', verbose_name=u'公司')
    date_created = models.DateTimeField(verbose_name=u'创建时间', default=datetime.now())
    #city = models.ForeignKey(Area,max_length=20, verbose_name=u'工作城市',related_name='city_area', on_delete=models.SET_NULL,blank=True,null=True,db_column='city',)
    city = models.CharField(verbose_name='工作城市', max_length=30)
    date_updated = models.DateTimeField(auto_now=True,verbose_name=u'更新时间')
    job_description = models.TextField(max_length=300, verbose_name=u'职位描述', help_text=u'职位描述')
    job_type = models.CharField(max_length=30, verbose_name=u'工作种类')

    salary = (
        (1, u'1500-5000/月'),
        (2, u'5000-1000/月'),
        (3, u'1000-15000/月'),
        (4, u'15000-2000/月'),
        (5, u'2000-25000/月'),
        (6, u'25000以上/月'),
              )
    salary = models.PositiveSmallIntegerField(choices=salary, verbose_name=u'工资')
    valid_period = models.CharField(max_length=20, verbose_name=u'有效期')

    def __unicode__(self):
        return u'self.job_type'

    class Meta:
        db_table = "job"
        ordering = ['-date_updated', '-date_created']


class Apply(models.Model):
    id = models.AutoField(primary_key=True, verbose_name=u'申请记录id')
    date_created = models.DateTimeField(verbose_name=u'申请时间', default=datetime.now)
    position = models.ForeignKey(JobInformation, verbose_name=u'职位id', blank=True, related_name='fk_apply',
                                 null=True, on_delete=models.SET_NULL)
    candidates = models.ForeignKey(User, related_name='fk_candidates_user_id', verbose_name=u'申请者')
    is_expired = models.PositiveSmallIntegerField(verbose_name=u'是否过期', default=0)

    def __unicode__(self):
        return self.candidates

    class Meta:
        db_table = "apply"


class JobFavourites(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, verbose_name=u'用户', related_name='fk_user_id', on_delete=models.SET_NULL,
                             blank=True, null=True)
    job = models.ForeignKey(JobInformation, verbose_name=u'岗位', related_name='fk_job_id', on_delete=models.SET_NULL,
                            blank=True, null=True)
    date_created = models.DateTimeField(verbose_name=u'收藏时间', default=datetime.now)

    def __unicode__(self):
        return self.id

    class Meta:
        db_table = "job_favourites"


class test(models.Model):
    title = models.CharField(max_length=20,blank=True,null=True)
    image = models.ImageField(upload_to='images/logos',blank=True,null=True)

    class Meta:
        db_table = "test"
