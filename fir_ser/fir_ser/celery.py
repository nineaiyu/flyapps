#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 5月 
# author: NinEveN
# date: 2021/5/27

import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fir_ser.settings')

app = Celery('fir_ser')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


'''
pip install  django-celery-beat==1.1.0
export PYTHONOPTIMIZE=1
celery -A DevOps beat -l info -S django --logfile=./celery.beat.log

celery multi start b1 -A DevOps beat -l info -S django 

export PYTHONOPTIMIZE=1
celery -O OPTIMIZATION -A DevOps worker -l debug

celery multi start w1 -O OPTIMIZATION -A DevOps worker -l info --logfile=./celery.worker.log

celery -A DevOps flower --port=5566
'''
