from django.conf.urls import url, patterns, include
from django.views.decorators.cache import cache_page
from .views import celery_hello

urlpatterns = patterns('chat.views',
    url(r'^$', 'home', name='home'),
    url(r'^celery/hello/$', cache_page(60 * 2)(celery_hello)),  #, 'celery_hello', name='celery_hello'),
    url(r'^celery/hello1/$', 'celery_hello', name='celery_hello'),
    url(r'^celery/call/(?P<task_name>\w+)/$', 'task_caller', name='task_caller'),
)

# urlpatterns += patterns('chat.views',
#     url(r'^$', 'home', name='home'),
#     url(r'^celery/hello$', 'celery_hello', name='celery_hello'),
# )
