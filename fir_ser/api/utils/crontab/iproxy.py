#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 12月 
# author: NinEveN
# date: 2021/12/10
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from django.core.cache import cache

from fir_ser.settings import CACHE_KEY_TEMPLATE, APPLE_DEVELOPER_API_PROXY_LIST, APPLE_DEVELOPER_API_PROXY

logger = logging.getLogger(__name__)


def get_best_proxy_ips(url='https://api.appstoreconnect.apple.com/agreement'):
    active_proxy_ips = [proxy_info['proxy'] for proxy_info in APPLE_DEVELOPER_API_PROXY_LIST if
                        proxy_info.get('active')]
    access_ip_info = []
    if not active_proxy_ips:
        return

    def task(proxies):
        start_time = time.time()
        try:
            r = requests.get(url, proxies={'http': proxies, 'https': proxies}, timeout=30)
            access_ip_info.append({'ip': proxies, 'time': time.time() - start_time})
            logger.info(f"ip:{proxies} code:{r.status_code} time: {time.time() - start_time}")
        except Exception as e:
            logger.warning(f"ip {proxies} check failed Exception:{e}")

    pools = ThreadPoolExecutor(50)

    for proxy_ip in active_proxy_ips:
        pools.submit(task, proxy_ip)
    pools.shutdown()
    best_sorted_ips = sorted(access_ip_info, key=lambda x: x.get('time'))[:8]
    ip_proxy_store_key = CACHE_KEY_TEMPLATE.get("ip_proxy_store_list_key")
    best_sorted_ips = [ip_proxy['ip'] for ip_proxy in best_sorted_ips]
    cache.set(ip_proxy_store_key, best_sorted_ips, 24 * 60 * 60)
    return best_sorted_ips


def get_proxy_ip_from_cache(change_ip=False):
    ip_proxy_store_key = CACHE_KEY_TEMPLATE.get("ip_proxy_store_list_key")
    ip_proxy_store_active_key = CACHE_KEY_TEMPLATE.get("ip_proxy_store_active_key")
    active_ip_proxy = cache.get(ip_proxy_store_active_key)
    if not change_ip and active_ip_proxy:
        logger.info(f"get ip proxy cache {active_ip_proxy}")
        return active_ip_proxy

    ip_proxy_result = cache.get(ip_proxy_store_key)
    if not ip_proxy_result:
        ip_proxy_result = get_best_proxy_ips()

    if change_ip:
        try:
            ip_proxy_result.remove(active_ip_proxy)
        except Exception as e:
            logger.warning(f'remove bad ip proxy failed {e}')
        logger.error(f"remove bad ip proxy {active_ip_proxy}")
        cache.delete(ip_proxy_store_active_key)
        cache.set(ip_proxy_store_key, ip_proxy_result, 24 * 60 * 60)

    if len(ip_proxy_result) > 0:
        proxy_ip = ip_proxy_result[random.randint(0, 2 if len(ip_proxy_result) > 2 else len(ip_proxy_result) - 1)]
        proxy_info = {
            'http': proxy_ip,
            'https': proxy_ip
        }
    else:
        proxy_info = APPLE_DEVELOPER_API_PROXY
    logger.info(f"make ip proxy cache {proxy_info}")
    cache.set(ip_proxy_store_active_key, proxy_info, 24 * 60 * 60)
    return proxy_info
