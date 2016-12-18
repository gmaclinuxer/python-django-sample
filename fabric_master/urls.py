# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

urlpatterns = patterns('fabric_master.views',
    url(r'^$', 'home', name='home'),
)
