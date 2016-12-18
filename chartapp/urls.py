from django.conf.urls import include, patterns, url

urlpatterns = patterns('chartapp.views',
    url(r'^$', 'index', name='index'),
    url(r'^pie/(?P<top_n>\d+)/$', 'pie', name='pie'),
    url(r'^test/$', 'test', name='test'),
    url(r'^fail_state/(?P<top_n>\d+)/$', 'fail_state', name='fail_state'),
)
