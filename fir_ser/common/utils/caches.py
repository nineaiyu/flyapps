#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 4月
# author: liuyu
# date: 2020/4/7
import datetime
import logging
import time

from django.core.cache import cache
from django.db.models import F
from django.utils import timezone

from api.models import Apps, UserInfo, UserCertificationInfo, Order, StorageExchange
from api.utils.modelutils import get_app_d_count_by_app_id, get_app_domain_name, get_user_domain_name
from common.base.baseutils import get_order_num
from common.cache.invalid import invalid_app_cache, invalid_short_cache, invalid_app_download_times_cache, \
    invalid_head_img_cache
from common.cache.storage import AppDownloadTodayTimesCache, AppDownloadTimesCache, \
    UploadTmpFileNameCache, RedisCacheBase, UserCanDownloadCache, UserFreeDownloadTimesCache, WxTicketCache, \
    SignUdidQueueCache, CloudStorageCache
from common.core.sysconfig import Config
from common.notify.notify import pay_success_notify, download_times_not_enough
from fir_ser.settings import CACHE_KEY_TEMPLATE, SYNC_CACHE_TO_DATABASE

logger = logging.getLogger(__name__)


def sync_download_times_by_app_id(app_ids):
    for k, v in AppDownloadTimesCache(app_ids).get_many().items():
        app_id = k.split(CACHE_KEY_TEMPLATE.get("download_times_key"))[1].strip('_')
        Apps.objects.filter(app_id=app_id).update(count_hits=v)
        logger.info(f"sync_download_times_by_app_id app_id:{app_id} count_hits:{v}")


def del_cache_response_by_short(app_id, udid=''):
    app_obj = Apps.objects.filter(app_id=app_id).first()
    if app_obj:
        invalid_app_cache(app_obj)
        if app_obj.has_combo:
            invalid_app_cache(app_obj.has_combo)


def del_cache_by_delete_app(app_id):
    invalid_app_download_times_cache(app_id)
    app_obj = Apps.objects.filter(app_id=app_id).first()
    if app_obj:
        invalid_app_cache(app_obj)
        if app_obj.has_combo:
            invalid_app_cache(app_obj.has_combo)


def del_cache_by_app_id(app_id, user_obj):
    del_cache_by_delete_app(app_id)
    invalid_head_img_cache(user_obj)


def del_cache_storage(user_obj):
    logger.info(f"del_cache_storage user:{user_obj}")
    for app_obj in Apps.objects.filter(user_id=user_obj):
        del_cache_response_by_short(app_obj.app_id)
        del_cache_by_app_id(app_obj.app_id, user_obj)
    CloudStorageCache('*', user_obj.uid).del_many()
    invalid_head_img_cache(user_obj)


def get_app_today_download_times(app_ids):
    sync_download_times_by_app_id(app_ids)
    download_times_count = 0
    for k, v in AppDownloadTodayTimesCache(app_ids).get_many().items():
        download_times_count += v
    return download_times_count


def upload_file_tmp_name(act, filename, user_obj_id):
    cache_obj = UploadTmpFileNameCache(filename)
    if act == "set":
        cache_obj.del_storage_cache()
        cache_obj.set_storage_cache({'u_time': time.time(), 'id': user_obj_id, "filename": filename}, 2 * 60 * 60)
    elif act == "get":
        return cache_obj.get_storage_cache()
    elif act == "del":
        cache_obj.del_storage_cache()


def limit_cache_util(act, cache_key, cache_limit_times):
    (limit_times, cache_times) = cache_limit_times
    cache_obj = RedisCacheBase(cache_key)
    if act == "set":
        data = {
            "count": 1,
            "time": time.time()
        }
        cdata = cache_obj.get_storage_cache()
        if cdata:
            data["count"] = cdata["count"] + 1
            data["time"] = time.time()
        logger.info(f"limit_cache_util  cache_key:{cache_key}  data:{data}")
        cache_obj.set_storage_cache(data, cache_times)
    elif act == "get":
        cdata = cache_obj.get_storage_cache()
        if cdata:
            if cdata["count"] > limit_times:
                logger.error(f"limit_cache_util cache_key {cache_key}  over limit ,is locked . cdata:{cdata}")
                return False
        return True
    elif act == "del":
        cache_obj.del_storage_cache()


def login_auth_failed(act, email):
    logger.error(f"login email:{email} act:{act}")
    auth_code_key = "_".join([CACHE_KEY_TEMPLATE.get("login_failed_try_times_key"), email])
    return limit_cache_util(act, auth_code_key, SYNC_CACHE_TO_DATABASE.get("try_login_times"))


def send_msg_over_limit(act, email):
    auth_code_key = "_".join([CACHE_KEY_TEMPLATE.get("super_sign_failed_send_msg_times_key"), email])
    return limit_cache_util(act, auth_code_key, SYNC_CACHE_TO_DATABASE.get("try_send_msg_over_limit_times"))


def reset_short_response_cache(user_obj, app_obj=None):
    if app_obj is None:
        app_obj_short_list = Apps.objects.filter(user_id=user_obj).all()
    else:
        app_obj_short_list = [app_obj]
    for app_obj in app_obj_short_list:
        invalid_short_cache(app_obj)


def reset_app_wx_easy_type(user_obj, app_obj=None):
    if get_user_domain_name(user_obj):
        return reset_short_response_cache(user_obj, app_obj)
    if app_obj is None:
        app_obj_list = Apps.objects.filter(user_id=user_obj).all()
    else:
        app_obj_list = [app_obj]
    for app_obj in app_obj_list:
        if not get_app_domain_name(app_obj):
            app_obj.wxeasytype = True
            app_obj.save(update_fields=['wxeasytype'])
        invalid_short_cache(app_obj)


def enable_user_download_times_flag(user_id):
    set_user_download_times_flag(user_id, 1)


def disable_user_download_times_flag(user_id):
    set_user_download_times_flag(user_id, 0)


def check_user_can_download(user_id):
    return set_user_download_times_flag(user_id, 2)


def set_user_download_times_flag(user_id, act):
    cache_obj = UserCanDownloadCache(user_id)
    if act == 2:
        result = cache_obj.get_storage_cache()
        if result is None:
            return True
        return result
    return cache_obj.set_storage_cache(act, 3600 * 24)


def get_user_free_download_times(user_id, act='get', amount=1, auth_status=False):
    free_download_times = Config.USER_FREE_DOWNLOAD_TIMES
    if auth_status:
        free_download_times = Config.AUTH_USER_FREE_DOWNLOAD_TIMES
    cache_obj = UserFreeDownloadTimesCache(user_id)
    user_free_download_times = cache_obj.get_storage_cache()
    if user_free_download_times is not None:
        if act == 'set':
            return cache_obj.incr(-amount)
        else:
            return user_free_download_times
    else:
        cache_obj.set_storage_cache(free_download_times, 3600 * 24)
        if act == 'set':
            return cache_obj.incr(-amount)
        else:
            return free_download_times


def consume_user_download_times(user_id, app_id, amount=1, auth_status=False):
    with cache.lock(f"consume_user_download_times_{user_id}", timeout=10, blocking_timeout=6):
        if get_user_free_download_times(user_id, 'get', amount, auth_status) - amount >= 0:
            get_user_free_download_times(user_id, 'set', amount, auth_status)
        else:
            if not check_user_can_download(user_id):
                return False
            try:
                UserInfo.objects.filter(pk=user_id).update(download_times=F('download_times') - amount)
            except Exception as e:
                logger.error(f"{user_id} download_times less then 0. Exception:{e}")
                disable_user_download_times_flag(user_id)
                del_cache_response_by_short(app_id)
                msg = f"您当前账户下载次数不足，应用已经无法下载安装。为了避免业务使用，望您尽快充值!"
                download_times_not_enough(UserInfo.objects.filter(pk=user_id).first(), msg)
                return False
        return True


def enable_user_download(user_id):
    enable_user_download_times_flag(user_id)
    for app_obj in Apps.objects.filter(pk=user_id):
        del_cache_response_by_short(app_obj.app_id)
    return True


def add_user_download_times(user_id, download_times=0):
    with cache.lock(f"consume_user_download_times_{user_id}", timeout=10, blocking_timeout=6):
        try:
            UserInfo.objects.filter(pk=user_id).update(download_times=F('download_times') + download_times)
            return enable_user_download(user_id)
        except Exception as e:
            logger.error(f"{user_id} download_times less then 0. Exception:{e}")
            return False


def get_user_cert_auth_status(user_id):
    user_cert_obj = UserCertificationInfo.objects.filter(user_id=user_id).first()
    auth_status = False
    if user_cert_obj and user_cert_obj.status == 1:
        auth_status = True
    return auth_status


def check_user_has_all_download_times(app_obj, user_obj):
    if not user_obj:
        user_obj = app_obj.user_id
    user_id = user_obj.pk
    auth_status = get_user_cert_auth_status(user_id)
    d_count = get_app_d_count_by_app_id(app_obj.app_id, user_obj)
    a = get_user_free_download_times(user_id, auth_status=auth_status)
    b = d_count
    c = check_user_can_download(user_id)
    return get_user_free_download_times(user_id, auth_status=auth_status) - d_count >= 0 or check_user_can_download(
        user_id)


def consume_user_download_times_by_app_obj(app_obj):
    user_obj = app_obj.user_id
    auth_status = get_user_cert_auth_status(user_obj.pk)
    amount = get_app_d_count_by_app_id(app_obj.app_id, user_obj)
    if consume_user_download_times(user_obj.pk, app_obj.app_id, int(amount * (Config.SIGN_EXTRA_MULTIPLE - 1)),
                                   auth_status):
        return False
    return True


def user_auth_success(user_id):
    """
    认证成功，需要调用该方法增加次数
    :param user_id:
    :return:
    """
    get_user_free_download_times(user_id, 'get')
    get_user_free_download_times(user_id, 'set', Config.USER_FREE_DOWNLOAD_TIMES - Config.AUTH_USER_FREE_DOWNLOAD_TIMES)
    return enable_user_download(user_id)


def update_order_status(out_trade_no, status):
    with cache.lock(f"user_order_{out_trade_no}", timeout=10, blocking_timeout=6):
        order_obj = Order.objects.filter(order_number=out_trade_no).first()
        if order_obj:
            order_obj.status = status
            order_obj.save(update_fields=['status'])


def update_order_info(user_id, out_trade_no, payment_number, payment_type, description=None):
    with cache.lock("%s_%s" % ('user_order_', out_trade_no), timeout=10, blocking_timeout=6):
        try:
            user_obj = UserInfo.objects.filter(pk=user_id).first()
            order_obj = Order.objects.filter(user_id=user_obj, order_number=out_trade_no).first()
            if order_obj:
                if order_obj.status == 1:
                    download_times = order_obj.actual_download_times + order_obj.actual_download_gift_times
                    try:
                        order_obj.status = 0
                        order_obj.payment_type = payment_type
                        order_obj.payment_number = payment_number
                        now = timezone.now()
                        if not timezone.is_naive(now):
                            now = timezone.make_naive(now, timezone.utc)
                        order_obj.pay_time = now
                        default_description = "充值成功，充值下载次数 %s ，现共可用次数 %s"
                        if description:
                            default_description = description
                        order_obj.description = default_description % (
                            download_times // Config.APP_USE_BASE_DOWNLOAD_TIMES,
                            (user_obj.download_times + download_times) // Config.APP_USE_BASE_DOWNLOAD_TIMES)
                        order_obj.save(
                            update_fields=["status", "payment_type", "payment_number", "pay_time",
                                           "description"])
                        add_user_download_times(user_id, download_times)
                        logger.info(f"{user_obj} 订单 {out_trade_no} msg：{order_obj.description}")
                        pay_success_notify(user_obj, order_obj)
                        return True
                    except Exception as e:
                        logger.error(f"{user_obj} 订单 {out_trade_no} 更新失败 Exception：{e}")
                elif order_obj.status == 0:
                    return True
                else:
                    return False
            else:
                logger.error(f"{user_obj} 订单 {out_trade_no} 订单获取失败，或订单已经支付")

        except Exception as e:
            logger.error(f"{user_obj} download_times less then 0. Exception:{e}")
        return False


def check_app_permission(app_obj, res, user_obj=None):
    if not app_obj:
        res.code = 1003
        res.msg = "该应用不存在"
    elif app_obj.status != 1:
        res.code = 1004
        res.msg = "该应用被封禁，无法下载安装"
    elif not check_user_has_all_download_times(app_obj, user_obj):
        res.code = 1009
        res.msg = "可用下载额度不足，请联系开发者"
    elif not app_obj.isshow:
        res.code = 1004
        res.msg = "您没有权限访问该应用"

    return res


def set_wx_ticket_login_info_cache(ticket, data=None, expire_seconds=600):
    if data is None:
        data = {}
    WxTicketCache(ticket).set_storage_cache(data, expire_seconds)


def get_wx_ticket_login_info_cache(ticket):
    cache_obj = WxTicketCache(ticket)
    wx_ticket_info = cache_obj.get_storage_cache()
    if wx_ticket_info:
        cache_obj.del_storage_cache()
    return wx_ticket_info


def add_download_times_free_base(user_obj, amount, payment_name, description, order_type=1):
    if amount <= 0:
        return True
    order_number = get_order_num()
    order_obj = Order.objects.create(payment_type=2, order_number=order_number, payment_number=order_number,
                                     user_id=user_obj, status=1, order_type=order_type, actual_amount=0,
                                     actual_download_times=amount, payment_name=payment_name,
                                     actual_download_gift_times=0)
    if update_order_info(user_obj.pk, order_obj.order_number, order_obj.order_number, order_obj.payment_type,
                         description):
        return True
    return False


def new_user_download_times_gift(user_obj, amount=200):
    description = '新用户赠送下载次数 %s ，现共可用次数 %s'
    return add_download_times_free_base(user_obj, amount, '系统', description, 2)


def admin_change_user_download_times(user_obj, amount=200):
    description = '管理员充值下载次数 %s ，现共可用次数 %s'
    return add_download_times_free_base(user_obj, amount, '后台管理员充值', description)


def auth_user_download_times_gift(user_obj, amount=200):
    description = '实名认证赠送下载次数 %s ，现共可用次数 %s'
    return add_download_times_free_base(user_obj, amount, '系统', description, 2)


def add_udid_cache_queue(prefix_key, values):
    prefix_key = f"{CACHE_KEY_TEMPLATE.get('ipa_sign_udid_queue_key')}_{prefix_key}"
    with cache.lock("%s_%s" % ('add_udid_cache_queue', prefix_key), timeout=10):
        cache_obj = SignUdidQueueCache(prefix_key)
        data = cache_obj.get_storage_cache()
        if data and isinstance(data, list):
            data.append(values)
        else:
            data = [values]
        cache_obj.set_storage_cache(list(set(data)), 60 * 60)
        return data


def get_and_clean_udid_cache_queue(prefix_key):
    prefix_key = f"{CACHE_KEY_TEMPLATE.get('ipa_sign_udid_queue_key')}_{prefix_key}"
    with cache.lock("%s_%s" % ('add_udid_cache_queue', prefix_key), timeout=10):
        cache_obj = SignUdidQueueCache(prefix_key)
        data = cache_obj.get_storage_cache()
        if data and isinstance(data, list):
            ...
        else:
            data = []
        cache_obj.del_storage_cache()
        return data


def add_user_storage_exchange(user_obj, exchange_number, exchange_month, remote_addr):
    with cache.lock("%s_%s" % ('user_storage_order_', user_obj.uid), timeout=10, blocking_timeout=6):
        try:
            download_times = exchange_number * exchange_month * Config.OSS_EXCHANGE_DOWNLOAD_TIMES
            expires_time = datetime.datetime.now() + datetime.timedelta(days=30 * exchange_month)
            description = f'扩容成功，消费下载点数{download_times} 兑换了 {exchange_number} GB存储空间'
            obj = StorageExchange.objects.create(user_id=user_obj, download_times=download_times,
                                                 storage_size=exchange_number * 1024 * 1024 * 1024,
                                                 expires_time=expires_time, remote_addr=remote_addr,
                                                 description=description)

            if add_user_download_times(user_obj.pk, -download_times):
                logger.info(f"{user_obj} 存储扩容成功  msg：{description}")
                return True
            else:
                obj.delete()
        except Exception as e:
            logger.error(f"{user_obj} download_times less then 0. Exception:{e}")
        return False


def add_user_ds(uid, amount):
    obj = UserInfo.objects.filter(uid=uid).first()
    try:
        amount = int(amount)
    except Exception:
        amount = 0
    if obj and amount:
        return admin_change_user_download_times(obj, amount * Config.APP_USE_BASE_DOWNLOAD_TIMES)
