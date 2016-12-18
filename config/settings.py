"""
Django settings for docker_django project.

Generated by 'django-admin startproject' using Django 1.8.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from __future__ import absolute_import

import os
from datetime import timedelta

# schedules task config
from celery.schedules import crontab

TIME_ZONE = 'Asia/Shanghai'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "5(15ds+i2+%ik6z&!yer+ga9m=e%jcqiz_5wszg)r-z!2--b2d"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gunicorn',
    'chat',
    'chartapp',
    'chartit',
    'fabric_master',
)

# ===============================================================
# # celery configuration
INSTALLED_APPS += ("djcelery",)
INSTALLED_APPS += ("kombu.transport.django",)
CELERY_ALWAYS_EAGER = False  # if set True, all tasks will be executed locally by blocking until the task returns
# CELERY_IMPORTS = ('chat.tasks', )
# CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = TIME_ZONE
CELERYBEAT_SCHEDULER = "djcelery.schedulers.DatabaseScheduler"
CELERYD_CONCURRENCY = 8
CELERYD_MAX_TASKS_PER_CHILD = 100
CELERY_DISABLE_RATE_LIMITS = True
# CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
# CELERY_ACCEPT_CONTENT = ['json', 'yaml']
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
# import djcelery
# djcelery.setup_loader()
# ===============================================================

# # broker settings
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# # list of modules to import when celery starts.
# # store schedule in the db
# CELERY_ANNOTATIONS = {'chat.tasks.hello_world': {'rate_limit': '1/s'}}
# http://blog.csdn.net/woshiaotian/article/details/36422781

# CELERY_IGNORE_RESULT = False
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

# Using the database to store task state and results.
# CELERY_RESULT_BACKEND = 'db+scheme://root:root@locahost:3306/django_docker'
# CELERY_RESULT_BACKEND = 'amqp://guest:guest@localhost:5672//'

# redis+socket:///path/to/redis.sock?virtual_host=db_number
# redis://:password@hostname:port/db_number
# CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# chord used but no CELERY_RESULT_BACKEND config
# [2016-04-22 19:17:39,536: INFO/MainProcess] Task celery.chord_unlock[c4a7ad4f-54f2-43e2-b684-0e81cc0ebb6c] retry: Retry in 1s: AttributeError("'DisabledBackend' object has no attribute '_get_task_meta_for'",)


CELERYBEAT_SCHEDULE = {
    'first_task': {
        'task': 'chat.tasks.hello_world',
        'args': [1, 2, 3],
        'kwargs': {},
        'schedule': timedelta(seconds=90)
    },
    'second_task': {
        'task': 'chat.tasks.add',
        'args': [1, 2],
        'schedule': crontab(hour=0, minute=1)
    }
}

# # queue config
# from kombu import Queue, Exchange
#
# default_exchange = Exchange(name='default', type='direct')
# direct_exchange = Exchange(name='Xdirect', type='direct')
# topic_exchange = Exchange(name='Xtopic', type='topic')
# CELERY_DEFAULT_QUEUE = 'default'  # celery -> default
# # define exchange, queue and binding
# CELERY_QUEUES = (
#     Queue('default', default_exchange, routing_key='default'),
#     Queue('QueueA', direct_exchange, routing_key='keyA'),
#     Queue('QueueB', direct_exchange, routing_key='keyB'),
# )
# # define task router, put task_A(B) to QueueA(B)
# CELERY_ROUTES = {
#     'chat.tasks.task_A': {
#         'queue': 'QueueA',
#         'routing_key': 'keyA',
#     },
#     'chat.tasks.task_B': {
#         'queue': 'QueueB',
#         'routing_key': 'keyB',
#     },
# }

CELERY_QUEUES = {
    "default_queue": {
        "exchange": "default_exchange",
        "exchange_type": "direct",
        "routing_key": "default_change"
    },
    "QueueA": {
        "exchange": "direct_exchange",
        "exchange_type": "direct",
        "routing_key": "keyA"
    },
    "QueueB": {
        "exchange": "direct_exchange",
        "exchange_type": "direct",
        "routing_key": "keyB"
    },
    # "topic_queue": {
    #     "exchange": "topic_exchange",
    #     "exchange_type": "topic",
    #     "routing_key": "topictest.#",
    # },
    # "fanout_queuea": {
    #     "exchange": "fanout_exchange",
    #     "exchange_type": "fanout",
    #     "binding_key": "fanout_bkeya",
    # },
    # "fanout_queueb": {
    #     "exchange": "fanout_exchange",
    #     "exchange_type": "fanout",
    #     "binding_key": "fanout_bkeyb",
    # },
}


class TaskRouter(object):
    def route_for_task(self, task, args=None, kwargs=None):
        if task.startswith('chat.tasks.task_A'):
            return {
                'queue': 'QueueA',
            }
        elif task.startswith('chat.tasks.task_B'):
            return {
                'queue': 'QueueB',
            }
        # elif task.startswith('chat.tasks.hello_world'):
        #     return {
        #         "exchange": "fanout_exchange",
        #     }
        #     return {'exchange': 'video',
        #             'exchange_type': 'topic',
        #             'routing_key': 'video.compress'}
        else:
            return {
                'queue': 'default_queue',
            }
        # else:
        #     return None

CELERY_ROUTES = (TaskRouter(),)
# ===============================================================
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'config.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.request",

)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    # 'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(BASE_DIR, "templates"),
)

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DAO_TEST = bool(os.environ.get('DAO_TEST'))

# DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': os.environ['MYSQL_INSTANCE_NAME'],
#        'USER': os.environ['MYSQL_USERNAME'],
#        'PASSWORD': os.environ['MYSQL_PASSWORD'],
#        'HOST': os.environ['MYSQL_PORT_3306_TCP_ADDR'],
#        'PORT': os.environ['MYSQL_PORT_3306_TCP_PORT']
#    }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'django_docker',
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': 'localhost',
        'PORT': 3306
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

TIME_ZONE = 'Asia/Shanghai'

LANGUAGE_CODE = 'zh-hans'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'django_cache_table',
#         'TIMEOUT': 120,
#         'OPTIONS': {
#             'MAX_ENTRIES': 1000
#         }
#     }
# }
# python manage.py createcachetable

# sudo apt-get install memcache
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': 'localhost:11211',
#         # 'LOCATION': 'unix:/tmp/memcached.sock',
#         # 'LOCATION': [
#         #     '172.19.26.240:11211',
#         #     '172.19.26.242:11211',
#         # ]
#     }
# }
# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': '/var/tmp/django_cache',
#     }
# }
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
try:
    from .local_settings import *
except ImportError:
    pass
