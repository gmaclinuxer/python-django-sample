from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('chat.urls')),
    url(r'^chart/', include('chartapp.urls')),
    url(r'^fabric/', include('fabric_master.urls')),
    url(r'^explore/', include('explore.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]