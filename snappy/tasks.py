# -*- coding: utf-8 -*-
from celery import Celery, task
from celery.utils.log import get_task_logger

app = Celery('tasks', broker='amqp://', backend='rpc://')

logger = get_task_logger(__name__)


@task
def hello_world(*args, **kwargs):
    logger.warning('hello world!')
    return 'hello world'
