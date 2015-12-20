from django.conf.urls import include, url
from django.contrib import admin
from .views import index, query, job, page, \
            search, domain, dns, whois_domain, whois_ip, \
            progress, auth

from .tables import DomainWhoisData, IPWhoisData, HostInfoData, \
                    QueryData, JobData, UAData, DNSData

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
    url(r'^progress/$', progress.view),
    url(r'^ua/data$', UAData.as_view(), name='ua_data'),
    url(r'^dns/data$', DNSData.as_view(), name='dns_data'),
    url(r'^whois_domain/data$', DomainWhoisData.as_view(), name='whois_domain_data'),
    url(r'^whois_ip/data$', IPWhoisData.as_view(), name='whois_ip_data'),
    url(r'^host_info/data$', HostInfoData.as_view(), name='host_info_data'),
    url(r'^query/data$', QueryData.as_view(), name='query_data'),
    url(r'^job/data$', JobData.as_view(), name='job_data'),
    url(r'^accounts/user/$', auth.user),
    url(r'^accounts/login/$', auth.log_in),
    url(r'^accounts/logout/$', auth.log_out),
]
