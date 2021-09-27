import os
import sys
import logging
from django.conf import settings

from config import BASECONF

try:
    from apps.jumpserver import const

    __version__ = const.VERSION
except ImportError as e:
    print("Not found __version__: {}".format(e))
    print("Python is: ")
    logging.info(sys.executable)
    __version__ = 'Unknown'

SOCKET_HOST = BASECONF.SERVER_BIND_HOST or '127.0.0.1'
SOCKET_PORT = BASECONF.SERVER_LISTEN_PORT or 8080

CELERY_FLOWER_HOST = BASECONF.CELERY_FLOWER_HOST or '127.0.0.1'
CELERY_FLOWER_PORT = BASECONF.CELERY_FLOWER_PORT or 5555

DEBUG = BASECONF.DEBUG or False
BASE_DIR = settings.BASE_DIR
APPS_DIR = BASE_DIR
LOG_DIR = os.path.join(BASE_DIR, 'logs')
TMP_DIR = os.path.join(BASE_DIR, 'tmp')
