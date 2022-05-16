#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月
# author: liuyu
# date: 2020/3/4
import logging

from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from api.base_views import app_delete
from api.models import AppStorage, Apps, StorageShareInfo, UserInfo, StorageExchange, Price
from api.tasks import migrate_storage_job
from api.utils.apputils import clean_history_apps
from api.utils.modelutils import PageNumber, get_user_storage_capacity, get_user_storage_used
from api.utils.response import BaseResponse
from api.utils.serializer import StorageSerializer, StorageShareSerializer, StorageExchangeSerializer, PriceSerializer
from api.utils.utils import upload_oss_default_head_img
from common.base.baseutils import get_choices_dict, get_choices_name_from_key, get_real_ip_address
from common.cache.state import MigrateStorageState
from common.cache.storage import TaskProgressCache
from common.core.auth import ExpiringTokenAuthentication, StoragePermission
from common.core.sysconfig import Config
from common.utils.caches import del_cache_storage, add_user_storage_exchange

logger = logging.getLogger(__name__)


def get_storage_group(request, res, storage_type, is_default=True):
    use_storage_obj = request.user.storage
    if use_storage_obj:
        res.storage = use_storage_obj.id
    else:
        res.storage = -1  # 默认存储
    storage_group = []
    if is_default:
        storage_group.append({'group_name': '默认存储',
                              'storages': [{'id': -1, 'name': '默认存储', 'used': True if res.storage == -1 else False}]})
    for s_type in storage_type:
        s_group = {'group_name': get_choices_name_from_key(AppStorage.storage_choices, s_type), 'storages': []}

        for obj in AppStorage.objects.filter(storage_type=s_type).filter(
                Q(user_id=request.user) | Q(storageshareinfo__to_user_id=request.user,
                                            storageshareinfo__status=1)).values('id', 'name', 'user_id__first_name',
                                                                                'user_id__uid').distinct():
            if obj['user_id__uid'] != request.user.uid:
                ext = {'username': obj['user_id__first_name']}
            else:
                share_count = StorageShareInfo.objects.filter(storage_id=obj['id'], status=1).count()
                share_used = StorageShareInfo.objects.filter(storage_id=obj['id'], status=1,
                                                             to_user_id__storage__id=obj['id']).count()
                ext = {'share_count': share_count, 'share_used': share_used}
            s_info = {'id': obj['id'], 'name': obj['name'], 'used': False, 'ext': ext}
            if request.user.storage and request.user.storage.id == obj['id']:
                s_info['used'] = True
            if not is_default and obj['user_id__uid'] != request.user.uid:
                continue
            else:
                s_group['storages'].append(s_info)
        storage_group.append(s_group)
    return storage_group


class StorageView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [StoragePermission, ]
    storage_type = [2]

    def get(self, request):
        res = BaseResponse()
        res.storage_list = []
        storage_org_list = list(AppStorage.storage_choices)
        for storage_t in storage_org_list:
            if storage_t[0] in self.storage_type:
                res.storage_list.append({'id': storage_t[0], 'name': storage_t[1]})
        res.endpoint_list = get_choices_dict([(x, x) for x in Config.STORAGE_ALLOW_ENDPOINT])

        act = request.query_params.get("act", None)
        is_default = request.query_params.get("is_default", 'true')
        pk = request.query_params.get("pk", None)
        keysearch = request.query_params.get("keysearch", None)
        if act == 'storage_type':
            res.download_auth_type_choices = get_choices_dict(AppStorage.download_auth_type_choices)
            res.default_max_storage_capacity = Config.STORAGE_OSS_CAPACITY
            return Response(res.dict)

        if act == 'storage_group':
            res.storage_group_list = get_storage_group(request, res, self.storage_type, is_default == 'true')
            migrate_progress = TaskProgressCache('migrating_storage_data', request.user.uid).get_storage_cache()
            res.migrate_progress = migrate_progress if migrate_progress else {}
            return Response(res.dict)
        if pk:
            if pk == '-1':
                default_storage = {
                    'id': -1,
                    'max_storage_capacity': get_user_storage_capacity(request.user),
                    'used_number': get_user_storage_used(request.user)
                }
                res.data = [default_storage]
                return Response(res.dict)
            else:
                share_obj = StorageShareInfo.objects.filter(to_user_id=request.user, storage_id_id=pk, status=1).first()
                if share_obj:
                    default_storage = {
                        'id': -1,
                        'max_storage_capacity': share_obj.number,
                        'used_number': get_user_storage_used(request.user)
                    }
                    res.data = [default_storage]
                    return Response(res.dict)

        # [1,2] 表示七牛存储和阿里云存储
        storage_queruset = AppStorage.objects.filter(user_id=request.user, storage_type__in=self.storage_type)
        if pk:
            storage_queruset = storage_queruset.filter(pk=pk)
        if keysearch:
            storage_queruset = storage_queruset.filter(Q(name__contains=keysearch) | Q(bucket_name=keysearch))

        if storage_queruset:
            page_obj = PageNumber()
            page_serializer = page_obj.paginate_queryset(queryset=storage_queruset.order_by("-created_time"),
                                                         request=request,
                                                         view=self)
            storage_serializer = StorageSerializer(page_serializer, many=True)
            storage_data_lists = storage_serializer.data
            storage_lists = {}
            for storage_data in storage_data_lists:
                storage_type = storage_data.get("storage_type")
                storage_data['secret_key'] = ''
                if not storage_lists.get(storage_type):
                    storage_lists[storage_type] = []
                storage_lists[storage_type].append(storage_data)
            res.data = storage_data_lists
            res.count = storage_queruset.count()
        else:
            res.data = []

        use_storage_obj = request.user.storage
        if use_storage_obj:
            res.storage = use_storage_obj.id
        else:
            res.storage = -1  # 默认存储
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        data = request.data
        logger.info(f"user {request.user} add new storage data:{data}")
        serializer = StorageSerializer(data=data, context={'user_obj': request.user})
        if serializer.is_valid():
            storage_obj = serializer.save()
            if storage_obj:
                if upload_oss_default_head_img(request.user, storage_obj):
                    res.msg = serializer.validated_data
                    logger.info(f"user {request.user} add new storage success")
                else:
                    storage_obj.delete()
                    logger.error(f"user {request.user} add new storage failed")
                    res.msg = "文件上传校验失败，请检查参数是否正确"
                    res.code = 1005
            else:
                logger.info(f"user {request.user} add new storage failed")
                res.msg = str(serializer.errors)
                res.code = 1005
        else:
            logger.info(f"user {request.user} add new storage failed")
            res.msg = str(serializer.errors)
            res.code = 1005
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        data = request.data
        logger.info(f"user {request.user} update storage data:{data}")
        use_storage_id = data.get("use_storage_id", None)
        force = data.get("force", None)
        if use_storage_id:
            if use_storage_id != -1:
                obj = AppStorage.objects.filter(pk=use_storage_id).first()
                if obj:
                    if obj.user_id != request.user:
                        if not StorageShareInfo.objects.filter(to_user_id=request.user, status=1,
                                                               storage_id=obj).first():
                            res.code = 1007
                            res.msg = "数据异常，请重试"
                            return Response(res.dict)
                else:
                    res.code = 1007
                    res.msg = "数据异常，请重试"
                    return Response(res.dict)

            c_task = migrate_storage_job.apply_async((use_storage_id, request.user.pk, force))
            msg = c_task.get(propagate=False)
            logger.info(f"run migrate storage task {request.user} msg:{msg}")
            if c_task.successful():
                c_task.forget()
            else:
                res.code = 1006
                res.msg = msg

            return Response(res.dict)

        storage_id = data.get("id", None)
        if storage_id:
            if request.user.storage and storage_id == request.user.storage.id and MigrateStorageState(
                    request.user.uid).get_state():
                res.msg = '存储迁移中，无法修改'
                res.code = 1007
                return Response(res.dict)
            storage_obj = AppStorage.objects.filter(id=storage_id, user_id=request.user).first()
            storage_obj_bak = AppStorage.objects.filter(id=storage_id, user_id=request.user).first()
            serializer = StorageSerializer(instance=storage_obj, data=data, context={'user_obj': request.user},
                                           partial=True)
            if serializer.is_valid():
                new_storage_obj = serializer.save()
                if new_storage_obj:
                    if upload_oss_default_head_img(request.user, new_storage_obj):
                        res.msg = serializer.validated_data
                        logger.info(f"user {request.user} update storage success")
                        del_cache_storage(request.user)
                        for share_obj in StorageShareInfo.objects.filter(user_id=request.user,
                                                                         storage_id=new_storage_obj, status=1).all():
                            del_cache_storage(share_obj.user_id)
                    else:
                        storage_obj_bak.save()
                        logger.error(f"user {request.user} update storage failed")
                        res.msg = "文件上传校验失败，请检查参数是否正确"
                        res.code = 1005
                else:
                    logger.info(f"user {request.user} update storage failed")
                    res.msg = str(serializer.errors)
                    res.code = 1005
            else:
                res.msg = str(serializer.errors)
                res.code = 1005
        else:
            res.msg = '该存储不存在'
            res.code = 1007
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        storage_id = request.query_params.get("id", None)
        if storage_id:
            try:
                if request.user.storage and storage_id == request.user.storage.id:
                    res.msg = '存储使用中，无法删除'
                    res.code = 1007
                    return Response(res.dict)
                AppStorage.objects.filter(user_id=request.user, id=storage_id).delete()
                logger.error(f"user {request.user} delete storage id:{storage_id} success")
            except Exception as e:
                logger.error(f"user {request.user} delete storage id:{storage_id} failed Exception:{e}")
        else:
            res.code = 1004
            res.msg = '该存储不存在'
        return Response(res.dict)


class CleanStorageView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [StoragePermission, ]

    def post(self, request):
        res = BaseResponse()
        data = request.data
        logger.info(f"user {request.user} clean storage data:{data}")
        act = data.get('act', '')
        if act in ['history', 'all']:
            if request.user.check_password(data.get('confirm_pwd', '')):
                app_obj_lists = Apps.objects.filter(user_id=request.user).all()
                for app_obj in app_obj_lists:
                    if act == 'all':
                        res = app_delete(app_obj)
                    elif act == 'history':
                        clean_history_apps(app_obj, request.user, 1)
            else:
                res.code = 1007
                res.msg = "密码有误，请检查"
        else:
            res.code = 1007
            res.msg = "参数不合法，清理失败"
        return Response(res.dict)


class ShareStorageView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [StoragePermission, ]

    def get(self, request):
        res = BaseResponse()
        uidsearch = request.query_params.get("uidsearch", None)
        status = request.query_params.get("operatestatus", '-1')
        share_list = StorageShareInfo.objects.filter(Q(user_id=request.user) | Q(to_user_id=request.user)).distinct()
        page_obj = PageNumber()
        if uidsearch:
            share_list = share_list.filter(
                Q(user_id__uid=uidsearch) | Q(to_user_id__uid=uidsearch) | Q(storage_id__name__contains=uidsearch))
        try:
            if status != '' and get_choices_name_from_key(StorageShareInfo.status_choices, int(status)):
                share_list = share_list.filter(status=status)
        except Exception as e:
            logger.error(f'status {status} check failed  Exception:{e}')

        page_serializer = page_obj.paginate_queryset(queryset=share_list.order_by("-created_time"),
                                                     request=request,
                                                     view=self)
        app_serializer = StorageShareSerializer(page_serializer, many=True, context={'user_obj': request.user})
        res.data = app_serializer.data
        res.count = share_list.count()
        res.status_choices = get_choices_dict(StorageShareInfo.status_choices)
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        uid = request.data.get('target_uid')
        sid = request.data.get('target_sid')
        number = request.data.get('target_number')
        if uid and number and sid:
            to_user_obj = UserInfo.objects.filter(uid=uid, is_active=True, supersign_active=True).first()
            storage_obj = AppStorage.objects.filter(pk=sid, user_id=request.user).first()
            if to_user_obj and storage_obj:
                if isinstance(number, int) and 0 < number < 999999999:
                    number = number * 1024 * 1024

                    max_storage_capacity = storage_obj.max_storage_capacity
                    storage_capacity = max_storage_capacity if max_storage_capacity else Config.STORAGE_OSS_CAPACITY
                    number = number if number < storage_capacity else storage_capacity
                    user_obj = request.user
                    if user_obj.pk != to_user_obj.pk:
                        try:
                            if True:
                                share_obj = StorageShareInfo.objects.filter(user_id=user_obj, to_user_id=to_user_obj,
                                                                            status=1, storage_id=storage_obj).first()
                                if share_obj:
                                    # number += share_obj.number
                                    share_obj.number = number
                                    share_obj.remote_addr = get_real_ip_address(request)
                                    share_obj.description = f'{user_obj.first_name} 共享给 {to_user_obj.first_name} {share_obj.number} Mb存储空间 '
                                    share_obj.save(update_fields=['number', 'remote_addr', 'description'])
                                else:
                                    StorageShareInfo.objects.create(user_id=user_obj, to_user_id=to_user_obj,
                                                                    status=1, number=number,
                                                                    storage_id=storage_obj,
                                                                    remote_addr=get_real_ip_address(request),
                                                                    description=f'{user_obj.first_name} 共享给 {to_user_obj.first_name} {number} Mb存储空间')
                                return Response(res.dict)
                            else:
                                res.msg = f'私有存储空间余额不足,当前存储余额最大为 {all_balance}'
                        except Exception as e:
                            res.msg = str(e)
                    else:
                        res.msg = '用户不合法'
                else:
                    res.msg = '共享数量异常'
            else:
                res.msg = '用户信息不存在'
        else:
            res.msg = '参数有误'
        res.code = 1003
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        uid = request.data.get('uid')
        sid = request.data.get('sid')
        if uid:
            user_obj = UserInfo.objects.filter(uid=uid, is_active=True, supersign_active=True).first()
            if user_obj:
                share_obj = StorageShareInfo.objects.filter(user_id=request.user, to_user_id__uid=uid, status=1).all()
                info_list = []
                number = 0
                for obj in share_obj:
                    storage_obj = obj.storage_id
                    info_list.append(
                        {
                            'storage_name': storage_obj.name, 'number': obj.number,
                            'storage_id': storage_obj.pk, 'storage_access_key': storage_obj.access_key
                        })
                    number += obj.number
                res.data = {'uid': user_obj.uid, 'name': user_obj.first_name, "info_list": info_list, "number": number}
            else:
                res.msg = '用户信息不存在'
                res.code = 1003
        else:
            res.msg = '参数有误'
            res.code = 1003
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        uid = request.query_params.get("uid", None)
        status = request.query_params.get("status", None)
        number = request.query_params.get("number", None)
        sid = request.query_params.get("sid", None)
        if MigrateStorageState(request.user.uid).get_state():
            res.code = 1008
            res.msg = "数据迁移中，无法处理该操作"
            return Response(res.dict)
        if uid and status and number and sid:
            share_obj = StorageShareInfo.objects.filter(user_id=request.user, to_user_id__uid=uid, status=status,
                                                        number=abs(int(number)), storage_id_id=sid).first()
            if share_obj:
                target_user_obj = UserInfo.objects.filter(uid=uid).first()
                if target_user_obj and target_user_obj.storage:
                    if target_user_obj.storage.id == share_obj.storage_id.id:
                        app_obj_lists = Apps.objects.filter(user_id=target_user_obj).all()
                        for app_obj in app_obj_lists:
                            res = app_delete(app_obj)
                            logger.warning(f'clean share storage {target_user_obj} {app_obj} {res}')
                        target_user_obj.storage = None
                        target_user_obj.save(update_fields=['storage'])
                share_obj.status = 2
                share_obj.save(update_fields=['status'])
            else:
                res.code = 1003
                res.msg = '共享记录不存在'
        return Response(res.dict)


class StorageConfigView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [StoragePermission, ]

    def get(self, request):
        res = BaseResponse()
        migrate_progress = TaskProgressCache('migrating_storage_data', request.user.uid).get_storage_cache()
        res.data = {
            'user_max_storage_capacity': get_user_storage_capacity(request.user),
            'user_used_storage_capacity': get_user_storage_used(request.user),
            'user_history_limit': UserInfo.objects.filter(pk=request.user.pk).first().history_release_limit,
            'storage_status': MigrateStorageState(request.user.uid).get_state(),
        }
        res.migrate_progress = migrate_progress if migrate_progress else {}
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        history_release_limit = request.data.get('user_history_limit')
        if history_release_limit:
            try:
                history_release_limit = int(history_release_limit) if int(
                    history_release_limit) > 0 else request.user.history_release_limit
            except Exception as e:
                logger.warning(f"update user history_release_limit failed Exception:{e}")
                history_release_limit = request.user.history_release_limit

            UserInfo.objects.filter(pk=request.user.pk).update(history_release_limit=abs(history_release_limit))
            app_obj_lists = Apps.objects.filter(user_id=request.user).all()
            for app_obj in app_obj_lists:
                clean_history_apps(app_obj, request.user, abs(history_release_limit))

        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        migrate_obj = MigrateStorageState(request.user.uid)
        if migrate_obj.get_state() == request.data.get('storage_status'):
            migrate_obj.del_state()
        return Response(res.dict)


class StorageExchangeView(APIView):
    authentication_classes = [ExpiringTokenAuthentication, ]
    permission_classes = [StoragePermission, ]

    def get(self, request):
        res = BaseResponse()
        storage_exchange_queryset = StorageExchange.objects.filter(user_id=request.user)
        page_obj = PageNumber()
        page_serializer = page_obj.paginate_queryset(queryset=storage_exchange_queryset.order_by("-created_time"),
                                                     request=request,
                                                     view=self)
        app_serializer = StorageExchangeSerializer(page_serializer, many=True)
        res.data = app_serializer.data
        res.count = storage_exchange_queryset.count()
        return Response(res.dict)

    def post(self, request):
        res = BaseResponse()
        exchange_number = request.data.get('exchange_number')
        exchange_prices_key = request.data.get('exchange_prices_key')
        if exchange_number and exchange_prices_key:
            price_obj = Price.objects.filter(is_enable=True, price_type=2, name=exchange_prices_key).first()
            if price_obj:
                exchange_month = price_obj.price
                if not add_user_storage_exchange(request.user, exchange_number, exchange_month,
                                                 get_real_ip_address(request)):
                    res.code = 1002
                    res.msg = '扩容失败，账号可用下载次数不足'
            else:
                res.code = 1001
                res.msg = '价格异常'

        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        price_obj_lists = Price.objects.filter(is_enable=True, price_type=2).all().order_by("updated_time").order_by(
            "price")
        res.data = {
            'pay_times': PriceSerializer(price_obj_lists, many=True).data,
            'storage_every_month_price': Config.OSS_EXCHANGE_DOWNLOAD_TIMES,
            'download_times': Config.APP_USE_BASE_DOWNLOAD_TIMES,
        }
        return Response(res.dict)
