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

from common.cache.storage import IpProxyListCache, IpProxyActiveCache
from common.core.sysconfig import Config

logger = logging.getLogger(__name__)


def get_best_proxy_ips(url='https://api.appstoreconnect.apple.com/agreement'):
    active_proxy_ips = [proxy_info['proxy'] for proxy_info in Config.APPLE_DEVELOPER_API_PROXY_LIST if
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
    best_sorted_ips = [ip_proxy['ip'] for ip_proxy in best_sorted_ips]
    IpProxyListCache().set_storage_cache(best_sorted_ips, 24 * 60 * 60)
    return best_sorted_ips


def get_proxy_ip_from_cache(change_ip=False):
    active_proxy_cache = IpProxyActiveCache()
    active_ip_proxy = active_proxy_cache.get_storage_cache()
    if not change_ip and active_ip_proxy:
        logger.info(f"get ip proxy cache {active_ip_proxy}")
        return active_ip_proxy

    list_proxy_cache = IpProxyListCache()
    ip_proxy_result = list_proxy_cache.get_storage_cache()
    if not ip_proxy_result:
        ip_proxy_result = get_best_proxy_ips()

    if change_ip and ip_proxy_result:
        try:
            ip_proxy_result.remove(active_ip_proxy)
        except Exception as e:
            logger.warning(f'remove bad ip proxy failed {e}')
        logger.error(f"remove bad ip proxy {active_ip_proxy}")
        active_proxy_cache.del_storage_cache()
        list_proxy_cache.set_storage_cache(ip_proxy_result, 24 * 60 * 60)

    if ip_proxy_result and len(ip_proxy_result) > 0:
        proxy_ip = ip_proxy_result[random.randint(0, 2 if len(ip_proxy_result) > 2 else len(ip_proxy_result) - 1)]
        proxy_info = {
            'http': proxy_ip,
            'https': proxy_ip
        }
    else:
        proxy_info = Config.APPLE_DEVELOPER_API_PROXY
    logger.info(f"make ip proxy cache {proxy_info}")
    active_proxy_cache.set_storage_cache(proxy_info, 24 * 60 * 60)
    return proxy_info


def clean_ip_proxy_infos():
    logger.info("clean ip proxy infos")
    IpProxyListCache().del_storage_cache()
    IpProxyActiveCache().del_storage_cache()
