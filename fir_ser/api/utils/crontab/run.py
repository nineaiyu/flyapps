#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from fir_ser.settings import SYNC_CACHE_TO_DATABASE
from api.utils.crontab.sync_cache import sync_download_times

import atexit
import fcntl

# 主要是为了防止多进程出现的多个定时任务同时执行
f = open("scheduler.lock", "wb")
try:
    fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)

    # 开启定时工作
    try:
        # 实例化调度器
        scheduler = BackgroundScheduler()
        # 调度器使用DjangoJobStore()
        scheduler.add_jobstore(DjangoJobStore(), "default")


        # 设置定时任务，选择方式为interval，时间间隔为10s
        # 另一种方式为每天固定时间执行任务，对应代码为：
        # @register_job(scheduler, 'cron', day_of_week='mon-fri', hour='9', minute='30', second='10',id='task_time')
        @register_job(scheduler, "interval", seconds=SYNC_CACHE_TO_DATABASE.get("download_times"))
        def sync_download_times_job():
            # 这里写你要执行的任务
            sync_download_times()


        register_events(scheduler)
        scheduler.start()
    except Exception as e:
        print(e)
        # 有错误就停止定时器
        scheduler.shutdown()

except:
    pass


def unlock():
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()


atexit.register(unlock)
