from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('chat.urls')),
    url(r'^chart/', include('chartapp.urls')),
    url(r'^fabric/', include('fabric_master.urls')),
]
