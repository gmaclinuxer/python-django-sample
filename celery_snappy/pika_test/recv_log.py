#!/usr/bin/env python

# Python client recommended by the RabbitMQ team
import pika
import time

# Distributing tasks among workers

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange="logs", exchange_type="fanout")

# once we disconnect the consumer the queue should be deleted.
result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue
channel.queue_bind(exchange="logs", queue=queue_name)

def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

channel.basic_consume(callback, queue=queue_name, no_ack=True)

print(' [*] Waiting for logs. To exit press CTRL+C')
channel.start_consuming()
