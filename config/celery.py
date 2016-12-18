# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' command-line program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')


app = Celery('config')

# app.conf.update(CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend', )

# using a string here means the worker will not have to pickle the object when using Windows
app.config_from_object('django.conf:settings')  # config celery with settings.py
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, related_name='tasks')

# app.conf.update(
#     CELERY_RESULT_BACKEND='djcelery.backends.database:DatabaseBackend',
# )

# app.conf.update(
#     CELERY_RESULT_BACKEND='djcelery.backends.cache:CacheBackend',
# )

# With the line above Celery will automatically discover tasks in reusable apps if you follow the tasks.py convention:
#
# - app1/
#     - app1/tasks.py   # define by related_name
#     - app1/models.py
# - app2/
#     - app2/tasks.py
#     - app2/models.py
# This way you do not have to manually add the individual modules to the CELERY_IMPORTS setting.

# bind to easily refer to the current task instance
@app.task(bind=True)
def debug_task(self):
    print('############################################')
    print('Request: {0!r}'.format(self.request))

 # worker -A config -l info -E -B -n WorkerA -Q QueueA
 # worker -A config -l info -E -B -n WorkerB -Q QueueB
 # worker -A config -l info -E -B -n WorkerX -Q QueueA,QueueB,default
 # worker -A config -l info -E -B --logfile=celery.log
