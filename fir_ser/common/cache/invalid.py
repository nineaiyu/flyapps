#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 12月 
# author: NinEveN
# date: 2021/12/23
from api.models import AppScreenShot, AppReleaseInfo, Apps
from common.cache.storage import AdPicShowCache, AppDownloadShortShowCache, RedisCacheBase, DownloadUrlCache, \
    TokenManagerCache, CloudStorageCache, AppInstanceCache, AppDownloadTimesCache


def invalid_screen_pic_cache(key, app_obj):
    for screen_shot_obj in AppScreenShot.objects.filter(app_id=app_obj).all():
        DownloadUrlCache(key, screen_shot_obj.screenshot_url).del_storage_cache()


def invalid_ad_pic_cache(key, short):
    ad_pic_short_cache = AdPicShowCache(key, short)
    ad_pic_cache_key = ad_pic_short_cache.get_storage_cache()
    if ad_pic_cache_key:
        DownloadUrlCache(key, ad_pic_cache_key).del_storage_cache()
    ad_pic_short_cache.del_storage_cache()


def invalid_short_response_cache(key, short):
    short_storage = AppDownloadShortShowCache(key, short)
    response_cache_key_list = short_storage.get_storage_cache()
    if response_cache_key_list and isinstance(response_cache_key_list, list):
        for response_cache_key in response_cache_key_list:
            RedisCacheBase(response_cache_key).del_storage_cache()
    short_storage.del_storage_cache()


def invalid_short_cache(app_obj, key='ShortDownloadView'.lower()):
    """
    失效下载页生成的缓存数据
    :param key:
    :param app_obj:
    :return:
    缓存key: 'ShortDownloadView'.lower()
    1.清理图片缓存
    2.清理下载token缓存
    3.清理广告缓存
    4.清理应用截图缓存
    5.清理下载token缓存[无需清理]
    6.清理response 响应缓存
    7.清理生成下载实例缓存
    # 8.如果有关联应用，还需要清理关联应用的图片缓存和下载token缓存
    """
    if not app_obj:
        return
    master_release_dict = AppReleaseInfo.objects.filter(app_id=app_obj, is_master=True).values('icon_url', 'release_id',
                                                                                               'release_type').first()
    if master_release_dict:
        # 1.清理图片缓存
        DownloadUrlCache(key, master_release_dict.get('icon_url')).del_storage_cache()

        release_id = master_release_dict.get('release_id')
        release_type = master_release_dict.get('release_type')
        # 2.清理下载token缓存
        TokenManagerCache(key, release_id).del_storage_cache()
        TokenManagerCache(key, f'{release_id}.{"apk" if release_type == 0 else "ipa"}').del_storage_cache()
        DownloadUrlCache(key, f'{release_id}.{"apk" if release_type == 0 else "ipa"}').del_storage_cache()
        TokenManagerCache('', f"{release_id}.plist").del_storage_cache()
        DownloadUrlCache('', f"{release_id}.plist").del_storage_cache()

    # 3.清理广告缓存
    invalid_ad_pic_cache(key, app_obj.short)

    # 4.清理应用截图缓存
    invalid_screen_pic_cache(key, app_obj)

    # 6.清理response 响应缓存
    invalid_short_response_cache(key, app_obj.short)

    # 7.清理生成下载实例缓存
    AppInstanceCache(app_obj.app_id).del_storage_cache()


def invalid_app_cache(app_obj):
    """
    删除app的时候，需要执行清理操作
    :param app_obj:
    :return:
    """
    invalid_short_cache(app_obj, '')
    invalid_short_cache(app_obj, 'ShortDownloadView'.lower())


def invalid_head_img_cache(user_obj):
    """
    :param user_obj:
    :return:
    """
    DownloadUrlCache('', user_obj.head_img).del_storage_cache()


def invalid_user_storage_cache(user_obj, storage_auth):
    """

    :param user_obj:
    :param storage_auth:
    :return:
    """
    CloudStorageCache(storage_auth, user_obj.uid).del_storage_cache()

    for app_obj in Apps.objects.filter(user_id=user_obj).all():
        invalid_app_cache(app_obj)

    invalid_head_img_cache(user_obj)


def invalid_app_download_times_cache(app_id):
    """
    删除应用的时候，需要清理一下下载次数缓存
    :param app_id:
    :return:
    """
    AppDownloadTimesCache(app_id).del_storage_cache()
    AppInstanceCache(app_id).del_storage_cache()


def invalid_app_download_plist_cache(release_id):
    TokenManagerCache('', release_id).del_storage_cache()
