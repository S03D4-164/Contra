from django.conf.urls import include, url
from django.contrib import admin
from views import *

urlpatterns = [
    #url(r'^admin/', include(admin.site.urls)),
    url(r'^$', index.view),
    url(r'^query/(?P<id>[0-9]+)$', query.view),
    url(r'^job/(?P<id>[0-9]+)$', job.view),
    url(r'^page/(?P<id>[0-9]+)$', page.view),
    url(r'^resource/(?P<id>[0-9]+)$', page.view),
    #url(r'^hostname/(?P<id>[0-9]+)$', hostname.view),
    url(r'^domain/(?P<id>[0-9]+)$', domain.view),
    #url(r'^domain_whois/(?P<id>[0-9]+)$', domain_whois.view),
    #url(r'^ip/(?P<id>[0-9]+)$', ip.view),
    #url(r'^ip_whois/(?P<id>[0-9]+)$', ip_whois.view),
    url(r'^progress/$', progress.view),
    url(r'^accounts/user/$', auth.user),
    url(r'^accounts/login/$', auth.log_in),
    url(r'^accounts/logout/$', auth.log_out),
]
