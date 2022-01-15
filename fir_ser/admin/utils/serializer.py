import logging
import os

from rest_framework import serializers

from api import models
from api.utils.serializer import AppReleaseSerializer, UserInfoSerializer, AppsSerializer, StorageSerializer, \
    DeveloperSerializer, SuperSignUsedSerializer, ThirdWxSerializer, DomainNameSerializer, BillInfoSerializer, \
    AppReportSerializer
from api.utils.storage.storage import Storage
from common.base.baseutils import get_choices_dict, get_choices_name_from_key

logger = logging.getLogger(__name__)


def get_download_url_from_context(self, obj, key, url, force_new=False):
    download_url = ""
    if self.context.get("key", None) and self.context.get("key") != "undefined":
        key = self.context.get("key", '')
    if self.context.get("storage", None) and self.context.get("storage") != "undefined":
        storage = self.context.get("storage", None)
    else:
        if isinstance(obj, models.Apps):
            storage = Storage(obj.user_id)
        elif isinstance(obj, models.AppReleaseInfo):
            storage = Storage(obj.app_id.user_id)
        elif isinstance(obj, models.UserAdDisplayInfo):
            storage = Storage(obj.user_id)
        elif isinstance(obj, models.UserInfo):
            storage = Storage(obj)
        elif isinstance(obj, models.UserCertificationInfo) or isinstance(obj, models.CertificationInfo):
            storage = Storage(obj.user_id, None, True)
        else:
            storage = None
    if storage:
        download_url = storage.get_download_url(os.path.basename(url), 600, key, force_new)
        logger.info(f'get {os.path.basename(url)} download_url {download_url} force_new:{force_new} key:{key}')
    return download_url


def get_app_master_obj_from_context(self, obj):
    master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj, is_master=True).first()
    if self.context.get("release_id", None) and self.context.get("release_id") != "undefined":
        master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj,
                                                                  release_id=self.context.get("release_id")).first()
    return master_release_obj


def get_screenshots_from_self(self, obj, force_new=False):
    screenshots_list = []
    for screenshot_obj in models.AppScreenShot.objects.filter(app_id=obj).all():
        icon_url = get_download_url_from_context(self, obj, '', screenshot_obj.screenshot_url, force_new)
        screenshots_list.append({'id': screenshot_obj.pk, 'url': icon_url})
    return screenshots_list


class AdminUserInfoSerializer(UserInfoSerializer):
    class Meta:
        model = models.UserInfo
        exclude = ["password", "api_token"]
        read_only_fields = ["id", "head_img", "free_download_times", "last_login",
                            "is_superuser", "last_name", "is_staff", "uid",
                            "date_joined", "download_times", "all_download_times", "storage", "groups",
                            "user_permissions", "certification_id", " app_count"]

    gender_choices = serializers.SerializerMethodField()

    def get_gender_choices(self, obj):
        return get_choices_dict(obj.gender_choices)

    role_choices = serializers.SerializerMethodField()

    def get_role_choices(self, obj):
        return get_choices_dict(obj.role_choices)

    storage_choices = serializers.SerializerMethodField()

    def get_storage_choices(self, obj):
        return get_choices_dict(models.AppStorage.storage_choices[1:])

    certification_status_choices = serializers.SerializerMethodField()

    def get_certification_status_choices(self, obj):
        return get_choices_dict(models.UserCertificationInfo.status_choices)

    certification_id = serializers.SerializerMethodField()

    def get_certification_id(self, obj):
        return models.UserCertificationInfo.objects.filter(user_id=obj).values('id').first()

    app_count = serializers.SerializerMethodField()

    def get_app_count(self, obj):
        return models.Apps.objects.filter(user_id=obj).count()

    def update(self, instance, validated_data):
        return super(AdminUserInfoSerializer, self).update(instance, validated_data)


class AdminAppsSerializer(AppsSerializer):
    class Meta:
        model = models.Apps
        fields = "__all__"
        read_only_fields = ["id", "app_id", "user_id", "bundle_id", "count_hits", "updated_time", "created_time"]

    status_choices = serializers.SerializerMethodField()

    def get_status_choices(self, obj):
        return get_choices_dict(obj.status_choices)

    type_choices = serializers.SerializerMethodField()

    def get_type_choices(self, obj):
        return get_choices_dict(obj.type_choices)

    supersign_type_choices = serializers.SerializerMethodField()

    def get_supersign_type_choices(self, obj):
        return get_choices_dict(obj.supersign_type_choices)

    release_count = serializers.SerializerMethodField()

    def get_release_count(self, obj):
        return models.AppReleaseInfo.objects.filter(app_id=obj).count()

    def update(self, instance, validated_data):
        return super(AdminAppsSerializer, self).update(instance, validated_data)


class AdminAppReleaseSerializer(AppReleaseSerializer):
    class Meta:
        model = models.AppReleaseInfo
        fields = '__all__'
        read_only_fields = ["id", "app_id", "release_id", "binary_size", "udid", "icon_url"]

    release_choices = serializers.SerializerMethodField()
    app_aid = serializers.CharField(source='app_id.app_id', read_only=True)

    def get_release_choices(self, obj):
        return get_choices_dict(obj.release_choices)

    def update(self, instance, validated_data):
        print(validated_data)
        if validated_data.get("is_master", False):
            models.AppReleaseInfo.objects.filter(app_id=instance.app_id).update(**{"is_master": False})
        else:
            if "is_master" in validated_data and validated_data.get("is_master") != True:
                del validated_data["is_master"]
        return super(AdminAppReleaseSerializer, self).update(instance, validated_data)


class AdminStorageSerializer(StorageSerializer):
    class Meta:
        model = models.AppStorage
        fields = "__all__"
        read_only_fields = ["id", "user_id", "updated_time", "created_time", "storage_type"]

    storage_choices = serializers.SerializerMethodField()

    def get_storage_choices(self, obj):
        return get_choices_dict(obj.storage_choices[1:])

    used_id = serializers.IntegerField(source="user_id.pk")


class AdminDeveloperSerializer(DeveloperSerializer):
    class Meta:
        model = models.AppIOSDeveloperInfo
        # depth = 1
        exclude = ["p8key", ]

    auth_type_choices = serializers.SerializerMethodField()

    def get_auth_type_choices(self, obj):
        return get_choices_dict(obj.auth_type_choices)

    status_choices = serializers.SerializerMethodField()

    def get_status_choices(self, obj):
        return get_choices_dict(obj.status_choices)


class AdminSuperSignUsedSerializer(SuperSignUsedSerializer):
    class Meta:
        model = models.APPSuperSignUsedInfo
        fields = ["created_time", "device_udid", "device_name", "developer_id", "bundle_id", "bundle_name", "app_id",
                  "id", "user_id", "short", "developer_pk"]

    app_id = serializers.IntegerField(source="app_id.pk")

    user_id = serializers.IntegerField(source="user_id.pk")

    short = serializers.CharField(source="app_id.short")
    developer_status = serializers.CharField(source="developerid.get_status_display")
    developer_id = serializers.CharField(source="developerid.issuer_id")
    developer_description = serializers.CharField(source="developerid.description")
    developer_pk = serializers.IntegerField(source="developerid.pk")


class AdminOrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = "__all__"
        read_only_fields = ["id", "user_id", "updated_time", "created_time", "payment_number", "order_number",
                            "payment_name", "actual_amount", "actual_download_times", "actual_download_gift_times"]

    payment_type_choices = serializers.SerializerMethodField()

    def get_payment_type_choices(self, obj):
        return get_choices_dict(obj.payment_type_choices)

    status_choices = serializers.SerializerMethodField()

    def get_status_choices(self, obj):
        return get_choices_dict(obj.status_choices)

    order_type_choices = serializers.SerializerMethodField()

    def get_order_type_choices(self, obj):
        return get_choices_dict(obj.order_type_choices)


class AdminUserCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserCertificationInfo
        fields = "__all__"
        read_only_fields = ["id", "user_id", "reviewed_time", "created_time"]

    certification_status_choices = serializers.SerializerMethodField()

    def get_certification_status_choices(self, obj):
        return get_choices_dict(obj.status_choices)

    certification_infos = serializers.SerializerMethodField()

    def get_certification_infos(self, obj):
        result = []
        for c_info in models.CertificationInfo.objects.filter(user_id=obj.user_id).all():
            result.append({
                'name': get_choices_name_from_key(models.CertificationInfo.type_choices, c_info.type),
                'certification_url': get_download_url_from_context(self, obj, '', c_info.certification_url)
            })
        return result

    def update(self, instance, validated_data):
        return super(AdminUserCertificationSerializer, self).update(instance, validated_data)


class AdminThirdWxSerializer(ThirdWxSerializer):
    class Meta:
        model = models.ThirdWeChatUserInfo
        fields = "__all__"
        read_only_fields = ["id", "openid", "user_id", "head_img_url"]


class AdminDomainNameSerializer(DomainNameSerializer):
    class Meta:
        model = models.UserDomainInfo
        fields = "__all__"
        read_only_fields = ["id", "app_id", "domain_type", "created_time", "cname_id"]

    domain_type_choices = serializers.SerializerMethodField()

    def get_domain_type_choices(self, obj):
        return get_choices_dict(obj.domain_type_choices)


class AdminBillInfoSerializer(BillInfoSerializer):
    class Meta:
        model = models.IosDeveloperPublicPoolBill
        fields = '__all__'
        read_only_fields = ["id", "user_id", "to_user_id", "action", "number", "app_info", "udid",
                            "udid_sync_info", "app_id", "remote_addr"]

    action_choices = serializers.SerializerMethodField()

    def get_action_choices(self, obj):
        return get_choices_dict(obj.action_choices)


class AdminAppReportSerializer(AppReportSerializer):
    class Meta:
        model = models.AppReportInfo
        fields = '__all__'
        read_only_fields = ["id", "app_id", "username", "created_time", "email", "report_reason", "report_type",
                            "remote_addr", "bundle_id", "app_name"]

    report_type_choices = serializers.SerializerMethodField()

    def get_report_type_choices(self, obj):
        return get_choices_dict(obj.report_type_choices)

    status_choices = serializers.SerializerMethodField()

    def get_status_choices(self, obj):
        return get_choices_dict(obj.status_choices)
