from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from .models import Item
from .utils import render_json
from redis import Redis
import os

# redis = Redis(host=os.environ['REDIS_PORT_6379_TCP_ADDR'],
#              port=os.environ['REDIS_PORT_6379_TCP_PORT'],
#              password=os.environ.get('REDIS_PASSWORD'))

redis = Redis(host='localhost',
              port=6379)


# password='redis')

def home(request):
    if request.method == 'POST':
        Item.objects.create(text=request.POST['item_text'])
        return redirect('/')
    items = Item.objects.all()
    counter = redis.incr('counter')
    return render(request, 'home.html', {'items': items, 'counter': counter})


def celery_hello(request):
    from .tasks import hello_world
    apply_info = hello_world.apply_async(args=['miya', 'hi'], kwargs={'user': 'miya', 'message': 'hi'})
    return render_json({
        'result': True,
        'task_id': apply_info.task_id,
        'task_name': apply_info.task_name
    })


def task_caller(request, task_name):
    apply_info = {}
    if task_name == 'task_A':
        from .tasks import task_A
        apply_info = task_A.delay(1, 2, kwarg1='a', kwarg2='b')
    if task_name == 'task_B':
        from .tasks import task_B
        apply_info = task_B.apply_async(args=[1, 2], kwargs={'kwarg1': 'a', 'kwarg2': 'b'})
        # apply_info = task_B.apply_async(args=[1, 2], kwargs={'kwarg1': 'a', 'kwarg2': 'b'}, countdown=10)
        # apply_info = task_B.apply_async(args=[1, 2], kwargs={'kwarg1': 'a', 'kwarg2': 'b'}, countdown=10, expires=1)
        # apply_info = task_B.apply_async(args=[1, 2], kwargs={'kwarg1': 'a', 'kwarg2': 'b'}, eta=datetime.now() + timedelta(seconds=10))
    if task_name == 'task_period':
        from .tasks import task_period
        apply_info = task_period.apply_async(args=[])
    if task_name == 'task_add':
        from .tasks import add
        apply_info = add.apply_async(args=[1,2])
    if task_name == 'task_retry':
        from .tasks import task_retry
        apply_info = task_retry.apply_async()
    if task_name == 'task_timeout':
        from .tasks import task_timeout
        apply_info = task_timeout.apply_async()
    if task_name == 'task_chain':
        from .tasks import task_chain
        apply_info = task_chain.apply_async()
    if task_name == 'task_immutable':
        from .tasks import task_immutable
        apply_info = task_immutable.apply_async()
    if task_name == 'task_group':
        from .tasks import task_group
        apply_info = task_group.apply_async()
    if task_name == 'task_chord':
        from .tasks import task_chord
        apply_info = task_chord.apply_async()
    if task_name == 'task_chunks':
        from .tasks import task_chunks
        apply_info = task_chunks.apply_async()
    if task_name == 'task_link':
        from .tasks import task_link
        apply_info = task_link.apply_async()
    if task_name == 'hello_world':
        from .tasks import hello_world
        apply_info = hello_world.apply_async()
    if task_name == 'debug':
        from config.celery import debug_task
        apply_info = debug_task.apply_async()

    print(apply_info)

    return render_json({
        'result': True,
        'task_id': apply_info.task_id,
        'task_name': apply_info.task_name
    })