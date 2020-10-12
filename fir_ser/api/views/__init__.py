#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 10月
# author: liuyu
# date: 2020/10/12
import logging
logger = logging.getLogger(__file__)

try:
    from api.utils.crontab import run
except Exception as e:
    logger.error("import crontab.run failed Exception:%s" % (e))