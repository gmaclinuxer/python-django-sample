from __future__ import absolute_import

# this will make sure the app is always imported when django start so that share_task will use this app
from .celery import app as celery_app
