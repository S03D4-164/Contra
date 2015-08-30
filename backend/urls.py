from django.conf.urls import include, url
from django.contrib import admin
import dockerapi, views

urlpatterns = [
    url(r'admin/', include(admin.site.urls)),
    url(r'docker/$', dockerapi.api),
    url(r'ghosthug/$', views.api),
]
