# -*- coding: utf-8 -*-

import logging
import sys
from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING


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
