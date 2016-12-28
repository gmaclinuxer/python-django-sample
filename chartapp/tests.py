from django.test import TestCase

# Create your tests here.


def hello():
    print os.path.join('/', 'tmp')
    import random
    random.shuffle([1, 2, 3])
