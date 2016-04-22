#miya.py

from celery import Celery

broker = "amqp://guest:guest@localhost:5672//"
# redis://:password@hostname:port/db_number
backend = "redis://localhost:6379/0"

miya = Celery('miya', broker=broker, backend=backend)

@miya.task
def add(x, y):
    print ('%s + %s' % (x, y))
    return x + y

# celery -A celery_snappy.miya worker -l info -c 4
# from celery_snappy.miya import add
x = add.delay(2, 3)
print (x.ready())
print (x.result)
add.apply_async(args=[20, 30])