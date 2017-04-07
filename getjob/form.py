# -*- coding:utf-8 -*-
from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget

from django.contrib.auth.admin import User
from django.core.exceptions import ValidationError

from models import ApplicantProfile, Company, JobInformation, Apply, test
from customclass import SelectCityWidget, ImageFileInput, CustomImageField

from datetime import date,timedelta
from imagekit.forms import ProcessedImageField
from imagekit.processors import ResizeToFill
import time,re,string
from citys import city_choices


class ApplicantRegisterForm(ModelForm):
    username = forms.CharField(widget=forms.TextInput(
                               attrs={'placeholder': u"用户名",}),
                               error_messages={'required': u'必填', 'invalid': u'格式不对'},
                               label=u'用户名'
                                )
    email = forms.EmailField(widget=forms.TextInput(
                                attrs={'placeholder': u"电子邮箱"}),
                                       error_messages={'required': u'必填'},
                                        label=u'电子邮箱')

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':u'密码'}),
                               help_text='不少于6位',
                               error_messages={'required':u'密码不能为空'},
                               label=u'密码')
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':u'重复密码'}),
                                error_messages={'required':u'密码不能为空', 'invalid': u'格式不对'},
                                label=u'重复密码')

    def clean_password(self):
        password = self.cleaned_data['password']
        if len(password) < 6:
            raise ValidationError(u'密码长度不小于6位')
        return password

    def clean(self):
        cleaned_data = super(ApplicantRegisterForm,self).clean()
        password_confirm = cleaned_data.get('password_confirm')
        password = cleaned_data.get('password')
        if password_confirm != password:
             self._errors['password_confirm'] = self.error_class([u'两次密码输入不相同'])
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email=email)
            raise ValidationError(u'邮箱已注册')
        except:
            return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            User.objects.get(username=username)
            raise ValidationError(u'用户已存在')
        except:
            return username

    class Meta:
        model = User
        fields =['username', 'email', 'password']


class CompanyRegisterForm(ModelForm):
    username = forms.CharField(
                               widget=forms.TextInput(
                               attrs={'placeholder': u"公司名称", 'title': '公司名称'}),
                               error_messages={'required': u'必填', 'invalid': u"格式不符合"},
                               label=u'公司名称'
                                )
    email = forms.EmailField(widget=forms.TextInput(
                                        attrs={'placeholder': u"电子邮箱"}),
                                        error_messages={'required': u'不能为空'},
                                        label=u'电子邮箱')

    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': u'密码'}),
                                  help_text='不少于6位', error_messages={'required': u'不能为空'},
                                  label='密码')
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': u'重复密码'}),
                                error_messages={'required': u'不能为空'},
                                label='重复密码')

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class applicantInformationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(
                                attrs={'placeholder':u"姓名"}),
                                error_messages={'required':u'必填'},
                                label=u'用户姓名')
    avatar = forms.ImageField(widget=ImageFileInput,label=u'头像')

    phone = forms.CharField(widget=forms.TextInput(
                                        attrs={'placeholder': u"手机号"}),
                                        error_messages={'required': u'必填'},
                                        label=u'手机号码')
    work_experiences = forms.CharField(widget=forms.Textarea(
                                        attrs={'placeholder': u"工作经历"}),
                                        error_messages={'required': u'必填'},
                                        label=u'工作经历')

    #  create date options for birth
    year_started = date.today().year
    year_list = range(year_started-35, year_started-16) #ages between 16-35
    month_dict = {i : i for i in range(1, 13)}
    birth = forms.DateField(widget=SelectDateWidget(years=year_list,
                                                      months=month_dict),
                                                      label=u'出生日期',
                                                      localize=True)

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if not phone.isdigit() or len(phone) != 11:
            raise forms.ValidationError(u"请输入有效的手机号码")
            raise forms.FieldError()
        return phone

    class Meta:
        model = ApplicantProfile
        exclude = ['user']


class CompanyInformationForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput(
                                        attrs={'placeholder': u"公司全称"}),
                                        error_messages={'required': u'必填'},
                                        label=u'公司全称',
                                        )
    address = forms.CharField(widget=forms.TextInput(
                                        attrs={'placeholder': u"详细地址"}),
                                        error_messages={'required': u'必填'},
                                        label=u'公司地址'
                                     )

    telephone = forms.CharField(widget=forms.TextInput(
                                        attrs={'placeholder': u"公司座机号"}),
                                        error_messages={'required': u'必填'},
                                        label=u'公司座机号'
                                               )
    contacts_name = forms.CharField(widget=forms.TextInput(
                                        attrs={'placeholder': u"联系人姓名"}),
                                        error_messages={'required': u'必填'},
                                        label=u'联系人姓名'
                                   )
    logo_thumbnail = forms.ImageField(widget=ImageFileInput,label=u'logo')
    advantages = forms.CharField(widget=forms.TextInput(
                                     attrs={'style': 'width:400',
                                         'placeholder':  u"一句话点亮"}),
                                         label=u'一句话点亮')

    #logo = ProcessedImageField(spec_id='2',
    #                                       processors=[ResizeToFill(100, 50)],
    #                                       format='JPEG',
    #                                       options={'quality': 60})
    class Meta:
        model = Company
        exclude = ['id','contact']


class JobPublishForm(forms.ModelForm):
    job_type = forms.CharField(widget=forms.TextInput(
                                  attrs={'placeholder': u'职位类型'}),
                                  error_messages={'required': u'必填'},
                                  label =u'职位类型',
                                   )

    job_description = forms.CharField(widget=forms.Textarea(
                                         attrs={'class':'form-control',
                                             'placeholder':  u'工作描述'}),
                                         error_messages={'required':u'必填'},
                                         label=u'工作描述',
                                        )
    salary = (
                (1, u'1500-5000/月'),
                (2, u'5000-1000/月'),
                (3, u'1000-15000/月'),
                (4, u'15000-2000/月'),
                (5, u'2000-25000/月'),
                (6, u'25000以上/月'),
              )
    salary = forms.ChoiceField(choices=salary,
                                         error_messages={'required':u'必填'},
                                         label=u'工资',
                                        )
    citys = (
              (1, u'北京'), (2, u'上海'), (3, u'深圳'), (4, u'广州'), (5,u'杭州'),(6,u'宁波'),(7,u'苏州'),(8,u'成都'),(9,u'天津'),
              (10,u'重庆'),(11,u'厦门'),(12,u'福州'),(13,u'西安'),
            )

    city = forms.ChoiceField(choices=citys, error_messages={'required': u'必填'}, label=u'城市',)

    valid_period = forms.CharField(widget=forms.TextInput(
                                    attrs={'placeholder':u'有效期'}),
                                    error_messages={'required': u'必填'},
                                    label=u'有效期',
                                     )

    class Meta:
        model = JobInformation
        exclude = ['id', 'publisher', 'date_created', 'date_updated']


class tform(forms.ModelForm):
    class Meta:
        model = test
        fields = ['title','image']