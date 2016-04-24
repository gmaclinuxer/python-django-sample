from kombu import Connection, Exchange, Queue

media_exchange = Exchange('media', 'direct', durable=True)

# Consume from several queues on the same channel:
image_queue = Queue('image', exchange=media_exchange, key='image')
video_queue = Queue('video', exchange=media_exchange, key='video')

# connections
with Connection('amqp://guest:guest@localhost//') as conn:

    # produce
    producer = conn.Producer(serializer='json')
    producer.publish({'name': '/tmp/lolcat1.avi', 'size': 1301013},
                      exchange=media_exchange, routing_key='video',
                      declare=[video_queue, image_queue])
    producer.publish({'name': '/tmp/lolcat1.png', 'size': 1013},
                      exchange=media_exchange, routing_key='image',
                      declare=[image_queue, video_queue])