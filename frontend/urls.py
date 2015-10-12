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
    url(r'^progress/$', progress.view),
    url(r'^accounts/user/$', auth.user),
    url(r'^accounts/login/$', auth.log_in),
    url(r'^accounts/logout/$', auth.log_out),
]
