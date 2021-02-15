#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job
from fir_ser.settings import SYNC_CACHE_TO_DATABASE
from api.utils.crontab.ctasks import sync_download_times, auto_clean_upload_tmp_file, auto_delete_job_log, \
    auto_delete_tmp_file, auto_check_ios_developer_active
import logging

logger = logging.getLogger(__file__)

import atexit
import fcntl

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.ERROR)

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


        # 另一种方式为每天固定时间执行任务，对应代码为：
        # @register_job(scheduler, 'cron', day_of_week='mon-fri', hour='9', minute='30', second='10',id='task_time')

        @register_job(scheduler, "interval", seconds=SYNC_CACHE_TO_DATABASE.get("download_times"))
        def sync_download_times_job():
            # 这里写你要执行的任务
            sync_download_times()


        @register_job(scheduler, "interval", seconds=SYNC_CACHE_TO_DATABASE.get("auto_clean_tmp_file_times"))
        def auto_clean_upload_tmp_file_job():
            auto_clean_upload_tmp_file()
            auto_delete_job_log()


        @register_job(scheduler, "interval", seconds=SYNC_CACHE_TO_DATABASE.get("auto_clean_local_tmp_file_times"))
        def auto_delete_tmp_file_job():
            auto_delete_tmp_file()


        @register_job(scheduler, "interval",
                      seconds=SYNC_CACHE_TO_DATABASE.get("auto_check_ios_developer_active_times"))
        def auto_check_ios_developer_active_job():
            auto_check_ios_developer_active()


        register_events(scheduler)
        scheduler.start()
    except Exception as e:
        logger.error("scheduler failed,so shutdown it Exception:%s" % (e))
        # 有错误就停止定时器
        scheduler.shutdown()


except:
    pass


def unlock():
    fcntl.flock(f, fcntl.LOCK_UN)
    f.close()


atexit.register(unlock)
