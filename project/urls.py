from django.conf.urls import include, url
from django.contrib import admin
from frontend import urls as frontend_urls
from backend import urls as backend_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include(backend_urls)),	
    url(r'^', include(frontend_urls)),	
]
