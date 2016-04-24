from kombu import Connection, Exchange, Queue

media_exchange = Exchange('media', 'direct', durable=True)
# Consume from several queues on the same channel:
image_queue = Queue('image', exchange=media_exchange, key='image')


def process_media(body, message):
    print(body)
    message.ack()


# connections
with Connection('amqp://guest:guest@localhost//') as conn:
    # consume
    with conn.Consumer([image_queue], callbacks=[process_media]) as consumer:
        # Process messages and handle events on all channels
        while True:
            conn.drain_events()
