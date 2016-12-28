# -*- coding: utf-8 -*-
from __future__ import absolute_import

import json
import random
import time
from datetime import datetime, timedelta

from celery import Celery, chain, chord, chunks, group, shared_task, task
from celery.exceptions import SoftTimeLimitExceeded
from celery.schedules import crontab
from celery.task import periodic_task
from celery.utils.log import get_task_logger

from config import settings

# # app = Celery('chat.tasks', broker='amqp://guest:guest@localhost:5672//', backend='redis://localhost:6379/0')
# # app = Celery('chat.tasks', backend='rpc://', broker='amqp://')
# app = Celery('chat.tasks', backend='redis://localhost', broker='amqp://')
# app.conf.update(
#     CELERY_TASK_SERIALIZER='json',
#     CELERY_ACCEPT_CONTENT=['json', 'pickle'],  # Ignore other content
#     CELERY_RESULT_SERIALIZER='json',
#     # CELERY_TIMEZONE='Asia/Shanghai',
#     CELERY_ENABLE_UTC=False,
# )
logger = get_task_logger(__name__)


@shared_task
def add(x, y):
    logger.warning('Adding {0:,} + {1}'.format(x, y))
    return x + y


@shared_task
def mul(x, y):
    logger.warning('Muling {0:,} * {1}'.format(x, y))
    return x * y


@shared_task
def div(x, y):
    logger.warning('Muling {0:,} / {1}'.format(x, y))
    return x / y


@shared_task
def xsum(numbers):
    r = sum(numbers)
    msg = 'xsum {0} = {1}'.format(numbers, r)
    logger.warning(msg)
    if settings.CELERY_ALWAYS_EAGER:
        print (msg)
    return r


@task(bind=True, ignore_result=True)
def task_A(self, arg1, arg2, kwarg1='x', kwarg2='y'):
    logger.warning('start task_A')
    time.sleep(1)
    logger.warning('a=%s, b=%s; %s + %s = %s' % (arg1, arg2, kwarg1, kwarg2, arg1 + arg2))
    logger.warning('end task_A')
    return True


@task(bind=True, ignore_result=True)
def task_B(self, *args, **kwargs):
    logger.warning('start task_B')
    # time.sleep(3)
    logger.warning(
        'a=%s, b=%s; %s + %s = %s' % (args[0], args[1], kwargs['kwarg1'], kwargs['kwarg2'], args[0] + args[1]))
    logger.warning('end task_B')
    return self


@task
def hello_world(*args, **kwargs):
    time.sleep(1)
    logger.warning('%s, args=%s, kwargs=%s' % ('hello world!', args, json.dumps(kwargs)))
    logger.warning('hello world!')
    return args, kwargs

@task(ignore_result=True)
def hello_worldi(*args, **kwargs):
    time.sleep(1)
    logger.warning('%s, args=%s, kwargs=%s' % ('hello world!', args, json.dumps(kwargs)))
    logger.warning('hello world!')
    return args, kwargs

# celery -A config worker -B -l info
@periodic_task(run_every=(crontab(hour="*", minute="*/1", day_of_week="*", day_of_month="*", month_of_year="*")))
def task_period():
    now = datetime.now()
    logger.warning('task_period: %s' % str(now))
    return now


# Time limits do not currently work on Windows and other platforms that do not support the SIGUSR1 signal.
@task(bind=True, name='task_timeout', soft_time_limit=1)
def task_timeout(self):
    try:
        time.sleep(2)
        return True
    except SoftTimeLimitExceeded:
        logger.warning('%s: timeout after %ss' % (self.name, self.soft_time_limit))
        return False


# http://docs.celeryproject.org/en/latest/reference/celery.app.task.html
# def retry(self, args=None, kwargs=None, exc=None, throw=True,
#               eta=None, countdown=None, max_retries=None, **options):
@task(bind=True, name='task_retry', default_retry_delay=10)
def task_retry(self):
    try:
        logger.warning('task_retry')
        1 / 0
    except Exception as exc:
        MaxRetry = 3
        retries = self.request.retries
        retries += 1
        if (retries <= MaxRetry):
            # override default_retry_delay
            logger.warning('%s: %s' % (self.name, retries))
            raise self.retry(countdown=2 * (retries), exc=exc)
        else:
            err_msg = '%s: %s(max_retries=%s)' % (self.name, retries, MaxRetry)
            logger.error(err_msg)
            # raise exc


@task
def num_off(kwargs):
    src = kwargs.get('src')
    dst = kwargs.get('dst')
    dst += 1
    next = '{0}->{1}'.format(src, dst)
    logger.warning(next)
    return {'src': next, 'dst': dst}


@task
def task_chain():
    res = chain(num_off.s({'src': 'starter', 'dst': 0}), num_off.s(), num_off.s(), num_off.s(), num_off.s())
    # res = (num_off.s({'src': 'starter', 'dst': 0}) | num_off.s() | num_off.s() | num_off.s() | num_off.s())
    # run sync in current process
    if settings.CELERY_ALWAYS_EAGER:
        pipe = res()
        result = pipe.get()
        print('reslt is: %s, run: dot -Tpng graph.dot -o graph.png to get call graph' % result)
        with open('graph.dot', 'wt') as fh:
            pipe.parent.parent.parent.parent.graph.to_dot(fh)
            # dot -Tpng graph.dot -o graph.png

    # run async in celery worker
    res.apply_async()


@task
def task_immutable():
    # specify a callback that does not take additional arguments
    # si -> subtask(immutable=True)
    # add.subtask((2, 2), immutable=True)
    # add.si(2, 2)
    # res = chain(num_off.s(), num_off.subtask(args=[{'src': 'lisi', 'dst': 0}], immutable=True), num_off.s(), num_off.s())
    # res.apply_async(args=[{'src': 'starter', 'dst': 0}])
    res1 = chain(num_off.s(), num_off.si({'src': 'lisi', 'dst': 0}), num_off.s(), num_off.s())
    res1.apply_async(args=[{'src': 'zhangsan', 'dst': 0}])

@task(bind=True)
def error_handler(self, uuid):
    result = self.app.AsyncResult(uuid)
    print('error_handler: Task {0} raised exception: {1!r}\n{2!r}'.format(
        uuid, result.result, result.traceback))


@task
def task_link():
    add.apply_async((1, 1),
                    link_error=[error_handler.s()],
                    link=[add.s(100), add.s(100), add.s(100)])

    div.apply_async((1, 0),
                    link_error=[error_handler.s()],
                    link=[add.s(100), add.s(100), add.s(100)])


@task
def rand(m):
    return random.randint(0, m)


@task
def filter(data):
    flist = [d for d in data if d > 25]
    # flist = random.shuffle(flist)
    flist.sort()
    logger.warning('filterd list: %s', flist)
    if settings.CELERY_ALWAYS_EAGER:
        print ('filterd list: %s' % flist)
    return flist


@task
def task_group():
    # 100 random num(group) -> filter -> sum (chain)
    # execute several tasks in parallel.
    g = group(rand.s(x) for x in range(100))
    # chain a group together with another task will auto upgrade to be a chord
    gchain = chain(g, filter.s(), xsum.s())
    gchain.apply_async(countdown=1)
    # logger.warning(datetime.now() + timedelta(seconds=5))
    # gchain.apply_async(eta=datetime.now() + timedelta(seconds=5))
    # gchain.apply_async(countdown=5)

    job = group([
        add.s(1, 2),
        add.s(2, 3),
        add.s(3, 4),
        add.s(4, 5),
    ])
    chain(job, xsum.s()).apply_async()
    # chord(job, xsum.s()).apply_async()
    # sync call
    if settings.CELERY_ALWAYS_EAGER:
        res = job.delay()
        cnt = 0
        while not res.ready():
            print('wait job ready%s' % '.' * cnt)
        # async call will stucked here
        print('job result: %s' % sum(res.get(timeout=2)))


@task
def task_chord():
    '''
        Tasks used within a chord must not ignore their results.
        In practice this means that you must enable a CELERY_RESULT_BACKEND
        in order to use chords. Additionally, if CELERY_IGNORE_RESULT
        is set to True in your configuration, be sure that the individual tasks
        to be used within the chord are defined with ignore_result=False.
        This applies to both Task subclasses and decorated tasks.
        raised: "TimeoutError('Operation timed out (3.0)',)"
    :return:
    '''
    header = group(add.s(x, x) for x in range(100))
    # chain a group together with another task will auto upgrade to be a chord
    # c1 = chain(header, xsum.s())
    # c1.apply_async()
    callback = xsum.s()
    # callback can only be executed after all of the tasks in the header have returned
    c2 = chord(header)(callback)  # AsyncResult object
    if settings.CELERY_ALWAYS_EAGER:
        print('task_chord: %s' % c2.get())


@task
def task_chunks():
    # divide an iterable of work into pieces, so that if you have one million objects, you can create 10 tasks with hundred thousand objects each
    if settings.CELERY_ALWAYS_EAGER:
        res = add.chunks(zip(range(100), range(100)), 10)()
        print('task_chunks: %s' % res.get())
    add.chunks(zip(range(100), range(100)), 10).apply_async()
    # group = add.chunks(zip(range(100), range(100)), 10).group()
    # group.skew(start=1, stop=10)()


# http://docs.celeryproject.org/en/latest/userguide/tasks.html#tips-and-best-practices
'''
# If you don’t care about the results of a task, be sure to set the ignore_result option, as storing results wastes time and resources.
# Disabling rate limits altogether is recommended if you don’t have any tasks using them
# Avoid launching synchronous subtasks, Make your design asynchronous instead, for example by using callbacks.
# The task granularity is the amount of computation needed by each subtask. In general it is better to split the problem up into many small tasks rather than have a few long running tasks.
'''
