from django.conf.urls import include, url
from django.contrib import admin
from apis import *

urlpatterns = [
    url(r'admin/', include(admin.site.urls)),
    url(r'local/ghost/$', local_ghost.ghost_api),
    url(r'local/thug/$', local_thug.thug_api),
    url(r'docker/ghost/$', docker_ghost.ghost_api),
    url(r'docker/thug/$', docker_thug.thug_api),
]
