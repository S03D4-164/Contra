from django.conf.urls import include, url
from django.contrib import admin
from .views import index, query, job, page, \
            search, domain, dns, whois_domain, whois_ip, \
            progress, auth

urlpatterns = [
    url(r'^$', index.view),
    url(r'^query/(?P<id>[0-9]+)$', query.view),
    url(r'^job/(?P<id>[0-9]+)$', job.view),
    url(r'^page/(?P<id>[0-9]+)$', page.view),
    url(r'^resource/(?P<id>[0-9]+)$', page.view),
    url(r'^search/$', search.view),
    url(r'^domain/(?P<id>[0-9]+)$', domain.view),
    url(r'^dns/(?P<id>[0-9]+)$', dns.view),
    url(r'^whois_domain/(?P<id>[0-9]+)$', whois_domain.view),
    url(r'^whois_ip/(?P<id>[0-9]+)$', whois_ip.view),
    #url(r'^hostname/(?P<id>[0-9]+)$', hostname.view),
    #url(r'^ip/(?P<id>[0-9]+)$', ip.view),
    url(r'^progress/$', progress.view),
    url(r'^accounts/user/$', auth.user),
    url(r'^accounts/login/$', auth.log_in),
    url(r'^accounts/logout/$', auth.log_out),
]
