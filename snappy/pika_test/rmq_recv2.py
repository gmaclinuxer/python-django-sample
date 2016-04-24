#!/usr/bin/env python

# Python client recommended by the RabbitMQ team
import pika
import time

# Distributing tasks among workers

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue_durable', durable=True)


# def callback(ch, method, properties, body):
#     print(" [x] Received %r" % body)


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    # time.sleep(body.count(b'.'))
    time.sleep(int(body))
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)
# Fair dispatch
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue_durable')

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
