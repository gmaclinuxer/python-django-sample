#!/usr/bin/env python

# Python client recommended by the RabbitMQ team
import pika
import sys

# Distributing tasks among workers

connection = pika.BlockingConnection(pika.ConnectionParameters(
    host='localhost'))
channel = connection.channel()
channel.exchange_declare(exchange="logs", exchange_type="fanout")

message = ' '.join(sys.argv[1:]) or "info:Hello World!"


channel.basic_publish(exchange='logs',
                      routing_key='',
                      body=message)
print(" [x] Sent %r" % message)
connection.close()
