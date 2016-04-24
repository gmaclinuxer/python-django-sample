# -*- coding: utf-8 -*-
from kombu.mixins import Consumer
from kombu import Connection
from kombu.log import get_logger
from kombu import Exchange, Queue

task_exchange = Exchange('tasks', type='direct')
task_queues = [Queue('hipri', task_exchange, routing_key='hipri'),
               Queue('midpri', task_exchange, routing_key='midpri'),
               Queue('lopri', task_exchange, routing_key='lopri')]

logger = get_logger(__name__)

def process_task(body, message):
    fun = body['fun']
    args = body['args']
    kwargs = body['kwargs']
    print('Got task: %s', (fun, args, kwargs))
    message.ack()


with Connection('amqp://guest:guest@localhost:5672//') as conn:
    consumer = Consumer(conn, queues=task_queues,
                        accept=['json'],
                        callbacks=[process_task])
    consumer.consume(no_ack=False)