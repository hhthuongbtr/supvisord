from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    # auth
    url(r'^login/$', 'accounts.views.login'),
    url(r'^logout', 'accounts.views.logout'),
    url(r'^auth/$', 'accounts.views.auth_view'),
    url(r'^invalid/$', 'accounts.views.invalid_login'),  
)

