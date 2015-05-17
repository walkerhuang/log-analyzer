from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    # Examples:
    # url(r'^$', 'mysite2.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'viewer.views.index', name='index'),
    url(r'^(?P<pk>[0-9]+)/$', 'viewer.views.detail', name='detail'),
    url(r'^add/$', 'viewer.views.add', name='add'),
    
]