# -*- coding: utf-8 -*-

# import from apps here


# import from lib
from django.conf.urls import patterns, include

urlpatterns = patterns('explore.views',
    # 首页--your index
    (r'^$', 'home'),
)
