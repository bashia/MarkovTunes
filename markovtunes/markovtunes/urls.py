from django.conf.urls import patterns, static, include, url
from  django.conf import settings
from django.contrib import admin
from frontend import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'markovtunes.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url('input',views.input),
    url('',views.uploadpage, name='start'),
    url('upload',views.uploadhandler)
)
