from django.conf.urls import patterns, include, url
from django.contrib import admin
from supvisor.views import supvisor
admin.autodiscover()



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'supervisor.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'supvisor.views.supvisor'), 
    url(r'^accounts/', include('accounts.urls')),
    url(r'^supvisor/', include('supvisor.urls')),
    url(r'^log/', include('log.urls')),
)