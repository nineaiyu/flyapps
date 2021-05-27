#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7

from django.core.cache import cache
from api.models import Apps, UserInfo, AppReleaseInfo, AppUDID, APPToDeveloper, APPSuperSignUsedInfo, \
    UserCertificationInfo, Order
import time, os
from django.utils import timezone
from fir_ser.settings import CACHE_KEY_TEMPLATE, SERVER_DOMAIN, SYNC_CACHE_TO_DATABASE, DEFAULT_MOBILEPROVISION, \
    USER_FREE_DOWNLOAD_TIMES, AUTH_USER_FREE_DOWNLOAD_TIMES
from api.utils.storage.storage import Storage, LocalStorage
from api.utils.baseutils import get_app_d_count_by_app_id, get_app_domain_name  # file_format_path,
import logging
from django.db.models import F

logger = logging.getLogger(__file__)


def sync_download_times_by_app_id(app_ids):
    app_id_lists = []
    for app_id in app_ids:
        down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_times_key"), app_id.get("app_id")])
        app_id_lists.append(down_tem_key)
    down_times_lists = cache.get_many(app_id_lists)
    for k, v in down_times_lists.items():
        app_id = k.split(CACHE_KEY_TEMPLATE.get("download_times_key"))[1].strip('_')
        Apps.objects.filter(app_id=app_id).update(count_hits=v)
        logger.info("sync_download_times_by_app_id app_id:%s count_hits:%s" % (app_id, v))


def get_download_url_by_cache(app_obj, filename, limit, isdownload=True, key='', udid=None):
    now = time.time()
    if isdownload is None:
        local_storage = LocalStorage(**SERVER_DOMAIN.get("IOS_PMFILE_DOWNLOAD_DOMAIN"))
        download_url_type = 'plist'
        if not udid:
            if app_obj.get('issupersign', None):
                download_url_type = 'mobileconifg'
        else:
            appudid_obj = AppUDID.objects.filter(app_id_id=app_obj.get("pk"), udid=udid, is_signed=True).first()
            if appudid_obj:
                SuperSign_obj = APPSuperSignUsedInfo.objects.filter(udid__udid=udid,
                                                                    app_id_id=app_obj.get("pk")).first()
                if SuperSign_obj and SuperSign_obj.user_id.supersign_active:
                    APPToDeveloper_obj = APPToDeveloper.objects.filter(app_id_id=app_obj.get("pk"),
                                                                       developerid=SuperSign_obj.developerid).first()
                    if APPToDeveloper_obj:
                        release_obj = AppReleaseInfo.objects.filter(app_id_id=app_obj.get("pk"), is_master=True).first()
                        if release_obj.release_id == APPToDeveloper_obj.release_file:
                            binary_file = APPToDeveloper_obj.binary_file
                        else:
                            binary_file = APPToDeveloper_obj.release_file
                        return local_storage.get_download_url(
                            binary_file + "." + download_url_type, limit), ""
                    else:
                        return "", ""
                else:
                    return "", ""
            else:
                return "", ""

        supersign = DEFAULT_MOBILEPROVISION.get("supersign")
        mobileconifg = ""

        if download_url_type == 'plist':
            enterprise = DEFAULT_MOBILEPROVISION.get("enterprise")
            mpath = enterprise.get('path', None)
            murl = enterprise.get('url', None)
        else:
            mpath = supersign.get('path', None)
            murl = supersign.get('url', None)

        if murl and len(murl) > 5:
            mobileconifg = murl

        if mpath and os.path.isfile(mpath):
            mobileconifg = local_storage.get_download_url(filename.split(".")[0] + "." + "dmobileprovision", limit)

        if download_url_type == 'mobileconifg' and supersign.get("self"):
            mobileconifg = local_storage.get_download_url(filename.split(".")[0] + "." + "mobileprovision", limit)

        return local_storage.get_download_url(filename.split(".")[0] + "." + download_url_type, limit), mobileconifg
    down_key = "_".join([key.lower(), CACHE_KEY_TEMPLATE.get('download_url_key'), filename])
    download_val = cache.get(down_key)
    if download_val:
        if download_val.get("time") > now - 60:
            return download_val.get("download_url"), ""
    else:
        user_obj = UserInfo.objects.filter(pk=app_obj.get("user_id")).first()
        storage = Storage(user_obj)
        return storage.get_download_url(filename, limit), ""


def get_app_instance_by_cache(app_id, password, limit, udid):
    if udid:
        app_info = Apps.objects.filter(app_id=app_id).values("pk", 'user_id', 'type', 'password', 'issupersign',
                                                             'user_id__certification__status').first()
        if app_info:
            app_info['d_count'] = get_app_d_count_by_app_id(app_id)
        return app_info
    app_key = "_".join([CACHE_KEY_TEMPLATE.get("app_instance_key"), app_id])
    app_obj_cache = cache.get(app_key)
    if not app_obj_cache:
        app_obj_cache = Apps.objects.filter(app_id=app_id).values("pk", 'user_id', 'type', 'password',
                                                                  'issupersign',
                                                                  'user_id__certification__status').first()
        if app_obj_cache:
            app_obj_cache['d_count'] = get_app_d_count_by_app_id(app_id)
            cache.set(app_key, app_obj_cache, limit)

    app_password = app_obj_cache.get("password")

    if app_password != '':
        if password is None:
            return None

        if app_password.lower() != password.strip().lower():
            return None

    return app_obj_cache


def set_app_download_by_cache(app_id, limit=900):
    down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_times_key"), app_id])
    download_times = cache.get(down_tem_key)
    if not download_times:
        download_times = Apps.objects.filter(app_id=app_id).values("count_hits").first().get('count_hits')
        cache.set(down_tem_key, download_times + 1, limit)
    else:
        cache.incr(down_tem_key)
        cache.expire(down_tem_key, timeout=limit)
    set_app_today_download_times(app_id)
    return download_times + 1


def del_cache_response_by_short(app_id, udid=''):
    apps_dict = Apps.objects.filter(app_id=app_id).values("id", "short", "app_id", "has_combo").first()
    if apps_dict:
        del_cache_response_by_short_util(apps_dict.get("short"), apps_dict.get("app_id"), udid)
        if apps_dict.get("has_combo"):
            combo_dict = Apps.objects.filter(pk=apps_dict.get("has_combo")).values("id", "short", "app_id").first()
            if combo_dict:
                del_cache_response_by_short_util(combo_dict.get("short"), combo_dict.get("app_id"), udid)


def del_cache_response_by_short_util(short, app_id, udid):
    logger.info("del_cache_response_by_short short:%s app_id:%s udid:%s" % (short, app_id, udid))
    cache.delete("_".join([CACHE_KEY_TEMPLATE.get("download_short_key"), short]))
    key = "_".join([CACHE_KEY_TEMPLATE.get("download_short_key"), short, '*'])
    for app_download_key in cache.iter_keys(key):
        cache.delete(app_download_key)

    cache.delete("_".join([CACHE_KEY_TEMPLATE.get("app_instance_key"), app_id]))

    key = 'ShortDownloadView'.lower()
    master_release_dict = AppReleaseInfo.objects.filter(app_id__app_id=app_id, is_master=True).values('icon_url',
                                                                                                      'release_id').first()
    if master_release_dict:
        download_val = CACHE_KEY_TEMPLATE.get('download_url_key')
        cache.delete("_".join([key, download_val, os.path.basename(master_release_dict.get("icon_url")), udid]))
        cache.delete("_".join([key, download_val, master_release_dict.get('release_id'), udid]))
        cache.delete(
            "_".join([key, CACHE_KEY_TEMPLATE.get("make_token_key"), master_release_dict.get('release_id'), udid]))


def del_cache_by_delete_app(app_id):
    now = timezone.now()
    down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_today_times_key"),
                             str(now.year), str(now.month), str(now.day), app_id])
    cache.delete(down_tem_key)

    cache.delete("_".join([CACHE_KEY_TEMPLATE.get("download_times_key"), app_id]))

    cache.delete("_".join([CACHE_KEY_TEMPLATE.get("app_instance_key"), app_id]))


def del_cache_by_app_id(app_id, user_obj):
    key = ''
    master_release_dict = AppReleaseInfo.objects.filter(app_id__app_id=app_id, is_master=True).values('icon_url',
                                                                                                      'release_id').first()
    download_val = CACHE_KEY_TEMPLATE.get('download_url_key')
    cache.delete("_".join([key, download_val, os.path.basename(master_release_dict.get("icon_url"))]))
    cache.delete("_".join([key, download_val, master_release_dict.get('release_id')]))
    cache.delete(
        "_".join([key.lower(), CACHE_KEY_TEMPLATE.get("make_token_key"), master_release_dict.get('release_id')]))
    cache.delete("_".join([key, download_val, user_obj.head_img]))


def del_cache_storage(user_obj):
    logger.info("del_cache_storage user:%s" % user_obj)
    for app_obj in Apps.objects.filter(user_id=user_obj):
        del_cache_response_by_short(app_obj.app_id)
        del_cache_by_app_id(app_obj.app_id, user_obj)

    storage_keys = "_".join([CACHE_KEY_TEMPLATE.get('user_storage_key'), user_obj.uid, '*'])
    for storage_key in cache.iter_keys(storage_keys):
        cache.delete(storage_key)

    download_val = CACHE_KEY_TEMPLATE.get('download_url_key')
    cache.delete("_".join(['', download_val, os.path.basename(user_obj.head_img)]))


def set_app_today_download_times(app_id):
    now = timezone.now()
    down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_today_times_key"),
                             str(now.year), str(now.month), str(now.day), app_id])
    if cache.get(down_tem_key):
        cache.incr(down_tem_key)
    else:
        cache.set(down_tem_key, 1, 3600 * 24)


def get_app_today_download_times(app_ids):
    sync_download_times_by_app_id(app_ids)

    now = timezone.now()
    app_id_lists = []
    download_times_count = 0
    for app_id in app_ids:
        down_tem_key = "_".join([CACHE_KEY_TEMPLATE.get("download_today_times_key"),
                                 str(now.year), str(now.month), str(now.day), app_id.get("app_id")])
        app_id_lists.append(down_tem_key)
    down_times_lists = cache.get_many(app_id_lists)
    for k, v in down_times_lists.items():
        download_times_count += v
    return download_times_count


# def developer_auth_code(act, user_obj, developer_issuer_id, code=None):
#     auth_key = file_format_path(user_obj, email=developer_issuer_id)
#     key = "_".join([CACHE_KEY_TEMPLATE.get("developer_auth_code_key"), auth_key])
#     if act == "set":
#         cache.delete(key)
#         cache.set(key, code, 60 * 10)
#     elif act == "get":
#         return cache.get(key)
#     elif act == "del":
#         cache.delete(key)


def upload_file_tmp_name(act, filename, user_obj_id):
    tmp_key = "_".join([CACHE_KEY_TEMPLATE.get("upload_file_tmp_name_key"), filename])
    if act == "set":
        cache.delete(tmp_key)
        cache.set(tmp_key, {'time': time.time(), 'id': user_obj_id, "filename": filename}, 60 * 60)
    elif act == "get":
        return cache.get(tmp_key)
    elif act == "del":
        cache.delete(tmp_key)


def limit_cache_util(act, cache_key, cache_limit_times):
    (limit_times, cache_times) = cache_limit_times
    if act == "set":
        data = {
            "count": 1,
            "time": time.time()
        }
        cdata = cache.get(cache_key)
        if cdata:
            data["count"] = cdata["count"] + 1
            data["time"] = time.time()
        logger.info("limit_cache_util  cache_key:%s  data:%s" % (cache_key, data))
        cache.set(cache_key, data, cache_times)
    elif act == "get":
        cdata = cache.get(cache_key)
        if cdata:
            if cdata["count"] > limit_times:
                logging.error("limit_cache_util cache_key %s  over limit ,is locked . cdata:%s" % (cache_key, cdata))
                return False
        return True
    elif act == "del":
        cache.delete(cache_key)


def login_auth_failed(act, email):
    logger.error("login email:%s act:%s" % (email, act))
    auth_code_key = "_".join([CACHE_KEY_TEMPLATE.get("login_failed_try_times_key"), email])
    return limit_cache_util(act, auth_code_key, SYNC_CACHE_TO_DATABASE.get("try_login_times"))


def send_msg_over_limit(act, email):
    auth_code_key = "_".join([CACHE_KEY_TEMPLATE.get("super_sign_failed_send_msg_times_key"), email])
    return limit_cache_util(act, auth_code_key, SYNC_CACHE_TO_DATABASE.get("try_send_msg_over_limit_times"))


def set_default_app_wx_easy(user_obj, only_clean_cache=False):
    app_obj_lists = Apps.objects.filter(user_id=user_obj)
    for app_obj in app_obj_lists:
        if only_clean_cache:
            del_cache_response_by_short(app_obj.app_id)
        else:
            if not get_app_domain_name(app_obj):
                app_obj.wxeasytype = True
                app_obj.save()
                del_cache_response_by_short(app_obj.app_id)


def enable_user_download_times_flag(user_id):
    set_user_download_times_flag(user_id, 1)


def disable_user_download_times_flag(user_id):
    set_user_download_times_flag(user_id, 0)


def check_user_can_download(user_id):
    return set_user_download_times_flag(user_id, 2)


def set_user_download_times_flag(user_id, act):
    user_can_download_key = "_".join(
        [CACHE_KEY_TEMPLATE.get("user_can_download_key"), str(user_id)])
    if act == 2:
        result = cache.get(user_can_download_key)
        if result is None:
            return True
        return result
    return cache.set(user_can_download_key, act, 3600 * 24)


def get_user_free_download_times(user_id, act='get', amount=1, auth_status=False):
    free_download_times = USER_FREE_DOWNLOAD_TIMES
    if auth_status:
        free_download_times = AUTH_USER_FREE_DOWNLOAD_TIMES
    now = timezone.now()
    user_free_download_times_key = "_".join(
        [CACHE_KEY_TEMPLATE.get("user_free_download_times_key"), str(now.year), str(now.month), str(now.day),
         str(user_id)])
    user_free_download_times = cache.get(user_free_download_times_key)
    if user_free_download_times is not None:
        if act == 'set':
            return cache.incr(user_free_download_times_key, -amount)
        else:
            return user_free_download_times
    else:
        cache.set(user_free_download_times_key, free_download_times, 3600 * 24)
        if act == 'set':
            return cache.incr(user_free_download_times_key, -amount)
        else:
            return free_download_times


def consume_user_download_times(user_id, app_id, amount=1, auth_status=False):
    with cache.lock("%s_%s" % ('consume_user_download_times', user_id)):
        if get_user_free_download_times(user_id, 'get', amount, auth_status) > 0:
            get_user_free_download_times(user_id, 'set', amount, auth_status)
        else:
            if not check_user_can_download(user_id):
                return False
            try:
                UserInfo.objects.filter(pk=user_id).update(download_times=F('download_times') - amount)
            except Exception as e:
                logger.error("%s download_times less then 0. Exception:%s" % (user_id, e))
                disable_user_download_times_flag(user_id)
                del_cache_response_by_short(app_id)
                return False
        return True


def enable_user_download(user_id):
    enable_user_download_times_flag(user_id)
    for app_obj in Apps.objects.filter(pk=user_id):
        del_cache_response_by_short(app_obj.app_id)
    return True


def add_user_download_times(user_id, download_times=0):
    with cache.lock("%s_%s" % ('consume_user_download_times', user_id)):
        try:
            UserInfo.objects.filter(pk=user_id).update(download_times=F('download_times') + download_times)
            return enable_user_download(user_id)
        except Exception as e:
            logger.error("%s download_times less then 0. Exception:%s" % (user_id, e))
            return False


def get_user_cert_auth_status(user_id):
    user_cert_obj = UserCertificationInfo.objects.filter(user_id=user_id).first()
    auth_status = False
    if user_cert_obj and user_cert_obj.status == 1:
        auth_status = True
    return auth_status


def check_user_has_all_download_times(app_obj):
    user_id = app_obj.user_id_id
    auth_status = get_user_cert_auth_status(user_id)
    return get_user_free_download_times(user_id, auth_status=auth_status) > 0 or check_user_can_download(user_id)


def user_auth_success(user_id):
    '''
    认证成功，需要调用该方法增加次数
    :param user_id:
    :return:
    '''
    get_user_free_download_times(user_id, 'get')
    get_user_free_download_times(user_id, 'set', USER_FREE_DOWNLOAD_TIMES - AUTH_USER_FREE_DOWNLOAD_TIMES)
    return enable_user_download(user_id)


def update_order_status(out_trade_no, status):
    with cache.lock("%s_%s" % ('user_order_', out_trade_no)):
        order_obj = Order.objects.filter(order_number=out_trade_no).first()
        if order_obj:
            order_obj.status = status
            order_obj.save()


def update_order_info(user_id, out_trade_no, payment_number, payment_type):
    with cache.lock("%s_%s" % ('user_order_', out_trade_no)):
        try:
            user_obj = UserInfo.objects.filter(pk=user_id).first()
            order_obj = Order.objects.filter(user_id=user_obj, order_number=out_trade_no).first()
            if order_obj:
                if order_obj.status == 1:
                    download_times = order_obj.actual_download_times + order_obj.actual_download_gift_times
                    try:
                        order_obj.status = 0
                        order_obj.payment_type = payment_type
                        order_obj.order_type = 0
                        order_obj.payment_number = payment_number
                        now = timezone.now()
                        if not timezone.is_naive(now):
                            now = timezone.make_naive(now, timezone.utc)
                        order_obj.pay_time = now
                        order_obj.description = "充值成功，充值下载次数 %s ，现总共可用次数 %s" % (
                            download_times, user_obj.download_times)
                        order_obj.save()
                        add_user_download_times(user_id, download_times)
                        logger.info("%s 订单 %s msg：%s" % (user_obj, out_trade_no, order_obj.description))
                        return True
                    except Exception as e:
                        logger.error("%s 订单 %s 更新失败 Exception：%s" % (user_obj, out_trade_no, e))
                elif order_obj.status == 0:
                    return True
                else:
                    return False
            else:
                logger.error("%s 订单 %s 订单获取失败，或订单已经支付" % (user_obj, out_trade_no))

        except Exception as e:
            logger.error("%s download_times less then 0. Exception:%s" % (user_obj, e))
        return False
