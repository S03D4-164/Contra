from django.conf.urls import include, url
from django.contrib import admin
#from .apis import local_ghost, local_thug, \
from .apis import docker_ghost, docker_thug, \
                    dns_resolve, whois_domain, whois_ip

urlpatterns = [
    url(r'admin/', include(admin.site.urls)),
    #url(r'local/ghost/$', local_ghost.ghost_api),
    #url(r'local/thug/$', local_thug.thug_api),
    url(r'docker/ghost/$', docker_ghost.ghost_api),
    url(r'docker/thug/$', docker_thug.thug_api),
    url(r'dns_resolve/$', dns_resolve.dns_resolve),
    url(r'whois_domain/$', whois_domain.whois_domain),
    url(r'whois_ip/$', whois_ip.whois_ip),
]
