"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
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
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views

import logging
logger = logging.getLogger(__name__)
#from reviews.views import create_review, add_questions, view_review, reply
from forms.views import create_form, view_form, reply, view_replies, resend_form
from users.views import student_registration, teacher_registration, profile, activate, view_set, create_set, delete_from_class, add_students, confirm_teacher
#from users import models as user_models

urlpatterns = [

    url(r'^$', TemplateView.as_view(template_name='home/home.html')),  

    #AUTH
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, {'template_name': 'users/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),

    #FORMS
    url(r'^form/create/$', create_form.as_view(), name = 'create_form'),
    url(r'^form/(?P<form_id>\d+)/$', view_form, name = 'view_form'),
    url(r'^form/(?P<form_id>\d+)/reply/$', reply.as_view(), name = 'reply'),
    url(r'^form/(?P<form_id>\d+)/view_replies/$', view_replies, name = 'view_replies'),

    #USERS
    url(r'^signup/$', TemplateView.as_view(template_name='users/signup.html')),
    url(r'^signup/student/$', student_registration, name = 'student_signup'),
    url(r'^signup/teacher/$', teacher_registration, name = 'teacher_signup'),
    url(r'^profile/$', profile, name = 'profile'),
    url(r'^class/create/$', create_set.as_view(), name = 'create_set'),
    url(r'^class/(?P<set_id>\d+)/$', view_set, name = 'view_set'),
    
    #EMAIL ACTIVATE
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),

    #AJAX
    url(r'^ajax/resend/$', resend_form, name = 'resend_form'),
    url(r'^ajax/delete_from_class/$', delete_from_class, name = 'delete_from_class'),
    url(r'^ajax/add_students/$', add_students, name = 'add_students'),
    url(r'^ajax/confirm/$', confirm_teacher, name = 'add_students'),
]
