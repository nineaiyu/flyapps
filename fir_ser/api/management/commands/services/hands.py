import logging
import os
import subprocess
import sys
import time

import psutil
from django.conf import settings

from config import BASECONF
from config import BASE_DIR

try:
    __version__ = BASECONF.VERSION
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


def check_database_connection():
    os.chdir(BASE_DIR)
    for i in range(60):
        logging.info("Check database connection ...")
        _code = subprocess.call("python manage.py showmigrations api ", shell=True)
        if _code == 0:
            logging.info("Database connect success")
            return
        time.sleep(1)
    logging.error("Connection database failed, exit")
    sys.exit(10)


def check_migrations():
    _cmd = "python manage.py showmigrations | grep '\[.\]' | grep -v '\[X\]'"
    _code = subprocess.call(_cmd, shell=True, cwd=BASE_DIR)

    if _code == 1:
        return


def perform_db_migrate():
    logging.info("Check database structure change ...")
    os.chdir(BASE_DIR)
    logging.info("Migrate model change to database ...")
    _code = subprocess.call('python3 manage.py migrate', shell=True)
    if _code == 0:
        return
    logging.error('Perform migrate failed, exit')
    sys.exit(11)


def prepare():
    check_database_connection()
    check_migrations()
    perform_db_migrate()


def get_sys_thread_num():
    return psutil.cpu_count(False) if psutil.cpu_count(False) else 2


def get_sys_process_num():
    return psutil.cpu_count(True) if psutil.cpu_count(True) else 4
