
from django.conf import settings
from django.conf.urls.static import static

"""job URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^getjob/', include('getjob.urls')),
    url(r'^log/',include('log.urls')),
    #url(r'^accounts/login/$','django.contrib.auth.views.login', {'template_name': 'getjob/logon.html'})
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)