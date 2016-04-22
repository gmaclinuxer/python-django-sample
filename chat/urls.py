from django.conf.urls import url, patterns, include

urlpatterns = patterns('chat.views',
    url(r'^$', 'home', name='home'),
    url(r'^celery/hello/$', 'celery_hello', name='celery_hello'),
    url(r'^celery/call/(?P<task_name>\w+)/$', 'task_caller', name='task_caller'),
)

# urlpatterns += patterns('chat.views',
#     url(r'^$', 'home', name='home'),
#     url(r'^celery/hello$', 'celery_hello', name='celery_hello'),
# )
