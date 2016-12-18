#!/usr/bin/env python

import os
import sys
import time
from logging import INFO

from utils import logto

# create logger
name = os.path.splitext(os.path.basename(__file__))[0]
logger = logto('./%s.log' % name, level=INFO)

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


def subscribe_cc():
    '''
    subscribe redis of cc for ip info sync
    '''

    # item data change type
    MIGRATE = 0
    DELETE = -1

    # test import and orm
    from chat import models
    print models.Item.objects.all()

    import redis
    rc = redis.Redis(host='10.142.22.18', port=11311, db=0, password='qcloud_cc_cache')
    ps = rc.pubsub()
    ps.subscribe(['JOB-QCLOUD-HOST-MODULE', 'JOB-QCLOUD-HOST-SOURCE'])
    for item in ps.listen():
        # skip type of 'subscribe'
        if item['type'] != 'message':
            continue
        chan, data = item.get('channel'), item.get('data')
        logger.info('[%s]: %s' % (chan, item))

        biz_id, inner_ip, outer_ip, plat_id, opt_type = data.get('ApplicationID'), \
                                                        data.get('InnerIP'), \
                                                        data.get('OuterIP'), \
                                                        data.get('Source'), \
                                                        data.get('Type')
        try:
            ip = models.IP.objects.get(biz_id=biz_id, inner_ip=inner_ip, outer_ip=outer_ip, plat_id=plat_id)
            if opt_type == DELETE:
                pass
            elif opt_type == MIGRATE:
                pass
            else:
                logger.warning(u'unknown opt_type: %s' % opt_type)
        except models.IP.DoesNotExist:
            # not care IP
            pass


if __name__ == '__main__':
    i = 0
    while True:
        logger.info('while: i = %s' % i)
        i += 1
        time.sleep(3)
    # subscribe_cc()
