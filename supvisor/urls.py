from django.conf.urls import patterns, include, url
from django.views.generic import ListView, DetailView

urlpatterns = patterns('',
    url(r'^$', 'supvisor.views.supvisor'), 
    url(r'^json/$', 'supvisor.views.supvisor_json'),
    url(r'^(?P<name>.+)/start/$', 'supvisor.views.start_job'),
    url(r'^(?P<name>.+)/restart/$', 'supvisor.views.start_job'),
    url(r'^(?P<name>.+)/stop/$', 'supvisor.views.stop_job'),
    url(r'^add/$', 'supvisor.views.add_process'),
    url(r'^(?P<name>.+)/delete/$', 'supvisor.views.delete_process'),
    url(r'^document/$', 'supvisor.views.document'),
    #RTMP
    url(r'^rtmp/add/$', 'supvisor.views.rtmp_add_process'),
    url(r'^rtmp/add/json$', 'supvisor.views.rtmp_add_json'),
)

