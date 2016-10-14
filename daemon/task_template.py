#!/usr/bin/env python
import os
import sys
import time
import logging
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

# auto config django environment
cur_dir, script_name = os.path.split(os.path.abspath(__file__))

# manage.py must be put in django project root
while 'manage.py' not in os.listdir(cur_dir):
    print 'current dir: %s' % cur_dir
    cur_dir, _ = os.path.split(cur_dir)
else:
    print 'root of django project: %s' % cur_dir
    sys.path.append(cur_dir)
    for root, dirs, files in os.walk(cur_dir):
        if 'settings.py' in files:
            print 'root of the settings.py: %s' % root
            settings_url = root.replace(cur_dir, '').replace(os.path.sep, '.')

            # convert .config.settings to config.settings
            if settings_url.startswith('.'):
                settings_url = settings_url[1:]

            # avoid overwrite DJANGO_SETTINGS_MODULE
            if os.getenv('DJANGO_SETTINGS_MODULE') is None:
                os.environ["DJANGO_SETTINGS_MODULE"] = "%s.settings" % settings_url
            break

# test import and orm
from chat import models
print models.Item.objects.all()


def logto(filename, name=__name__, level=DEBUG):
    '''
    log config
    '''

    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter(
        '%(levelname)-.3s [%(asctime)s.%(msecs)03d] %(threadName)-10s %(name)s:%(lineno)03d: %(message)s',
        '%Y%m%d-%H:%M:%S')
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if level == DEBUG:
        stream_handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(stream_handler)
    return logger


# create logger
name = os.path.splitext(os.path.basename(__file__))[0]
logger = logto('./%s.log' % name, level=INFO)

if __name__ == '__main__':
    i = 0
    while True:
        logger.info('while: i = %s' % i)
        i += 1
        time.sleep(3)
