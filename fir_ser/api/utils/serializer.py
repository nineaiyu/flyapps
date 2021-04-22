from rest_framework import serializers
from api import models
from api.utils.app.apputils import bytes2human
from api.utils.TokenManager import DownloadToken
from api.utils.app.supersignutils import get_redirect_server_domain
from api.utils.storage.storage import Storage
from api.utils.utils import get_developer_udided, get_choices_dict, get_choices_name_from_key
from api.utils.storage.caches import get_user_free_download_times, get_user_cert_auth_status
import os, json, logging

logger = logging.getLogger(__file__)

token_obj = DownloadToken()


def get_download_url_from_context(self, obj, key, url, force_new=False):
    icon_url = ""
    if self.context.get("key", None) and self.context.get("key") != "undefined":
        key = self.context.get("key", '')
    if self.context.get("storage", None) and self.context.get("storage") != "undefined":
        storage = self.context.get("storage", None)
    else:
        if isinstance(obj, models.Apps) or isinstance(obj, models.UserCertificationInfo):
            storage = Storage(obj.user_id)
        elif isinstance(obj, models.AppReleaseInfo):
            storage = Storage(obj.app_id.user_id)
        else:
            storage = None
    if storage:
        icon_url = storage.get_download_url(os.path.basename(url), 600, key, force_new)
    return icon_url


def get_app_master_obj_from_context(self, obj):
    master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj, is_master=True).first()
    if self.context.get("release_id", None) and self.context.get("release_id") != "undefined":
        master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj,
                                                                  release_id=self.context.get("release_id")).first()
    return master_release_obj


def get_screenshots_from_self(self, obj, force_new=False):
    screenshots_list = []
    for screenshot_obj in models.AppScreenShot.objects.filter(app_id=obj).all():
        key = ''
        icon_url = get_download_url_from_context(self, obj, key, screenshot_obj.screenshot_url, force_new)
        screenshots_list.append({'id': screenshot_obj.pk, 'url': icon_url})
    return screenshots_list


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = ["username", "uid", "mobile", "job", "email", "domain_name", "role", "first_name",
                  'head_img', 'storage_active', 'supersign_active', 'free_download_times', 'download_times',
                  'certification']

    head_img = serializers.SerializerMethodField()

    def get_head_img(self, obj):
        storage = Storage(obj)
        return storage.get_download_url(obj.head_img)

    free_download_times = serializers.SerializerMethodField()

    def get_free_download_times(self, obj):
        return get_user_free_download_times(obj.id, auth_status=get_user_cert_auth_status(obj.id))

    certification = serializers.SerializerMethodField()

    def get_certification(self, obj):
        auth_status = -1
        certification_obj = models.UserCertificationInfo.objects.filter(user_id=obj).first()
        if certification_obj:
            auth_status = certification_obj.status
        return auth_status


class AdminUserInfoSerializer(UserInfoSerializer):
    class Meta:
        model = models.UserInfo
        exclude = ["password", "api_token"]
        read_only_fields = ["id", "head_img", "free_download_times", "last_login",
                            "is_superuser", "last_name", "is_staff", "uid", "storage_active", "supersign_active",
                            "date_joined", "download_times", "all_download_times", "storage", "groups",
                            "user_permissions", "certification_id"]

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

    def update(self, instance, validated_data):
        return super(AdminUserInfoSerializer, self).update(instance, validated_data)


class AppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        exclude = ["user_id", "id"]

    has_combo = serializers.SerializerMethodField()

    def get_has_combo(self, obj):
        if obj.has_combo:
            obj.has_combo.has_combo = None
            return AppsSerializer(obj.has_combo, context=self.context).data

    preview_url = serializers.SerializerMethodField()

    def get_preview_url(self, obj):
        return get_redirect_server_domain(None, obj.user_id, obj.domain_name)

    sign_type_choice = serializers.SerializerMethodField()

    def get_sign_type_choice(self, obj):
        return get_choices_dict(obj.supersign_type_choices)

    supersign_used_number = serializers.SerializerMethodField()

    def get_supersign_used_number(self, obj):
        return models.APPSuperSignUsedInfo.objects.filter(app_id=obj).all().count()

    screenshots = serializers.SerializerMethodField()

    def get_screenshots(self, obj):
        return get_screenshots_from_self(self, obj)

    master_release = serializers.SerializerMethodField()

    def get_master_release(self, obj):
        master_release_obj = get_app_master_obj_from_context(self, obj)
        if master_release_obj:
            key = ''
            icon_url = get_download_url_from_context(self, obj, key, master_release_obj.icon_url)
            datainfo = {
                "app_version": master_release_obj.app_version,
                "icon_url": icon_url,
                "build_version": master_release_obj.build_version,
                "release_type": master_release_obj.release_type,
                "minimum_os_version": master_release_obj.minimum_os_version,
                "created_time": master_release_obj.created_time,
                "binary_size": bytes2human(master_release_obj.binary_size),
                "release_id": master_release_obj.release_id,
                "changelog": master_release_obj.changelog,
                "binary_url": master_release_obj.binary_url,
            }

            download_token = token_obj.make_token(master_release_obj.release_id, 600, key=key)
            datainfo["download_token"] = download_token
            udid_lists = []
            try:
                udid_data = eval(master_release_obj.udid)
                for udid in udid_data:
                    udid_lists.append({'udid': udid})
            except Exception as e:
                pass
            datainfo["udid"] = udid_lists

            return datainfo
        else:
            return {}


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


class AppsShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        fields = ["app_id", "name", "short", "has_combo", "isshow", "description", "need_password", 'master_release',
                  'type', 'issupersign', 'wxeasytype', 'wxredirect', 'domain_name', 'screenshots']

    screenshots = serializers.SerializerMethodField()

    def get_screenshots(self, obj):
        return get_screenshots_from_self(self, obj, True)

    need_password = serializers.SerializerMethodField()

    def get_need_password(self, obj):
        if obj.password != '':
            return True
        return False

    has_combo = serializers.SerializerMethodField()

    def get_has_combo(self, obj):
        if obj.has_combo:
            obj.has_combo.has_combo = None
            if obj.has_combo.isshow:
                return AppsShortSerializer(obj.has_combo, context=self.context).data

    master_release = serializers.SerializerMethodField()

    def get_master_release(self, obj):
        master_release_obj = get_app_master_obj_from_context(self, obj)
        if master_release_obj:
            key = ''
            icon_url = get_download_url_from_context(self, obj, key, os.path.basename(master_release_obj.icon_url),
                                                     True)
            datainfo = {
                "app_version": master_release_obj.app_version,
                "icon_url": icon_url,
                "build_version": master_release_obj.build_version,
                "release_type": master_release_obj.release_type,
                "created_time": master_release_obj.created_time,
                "binary_size": bytes2human(master_release_obj.binary_size),
                "release_id": master_release_obj.release_id,
                "changelog": master_release_obj.changelog,
                "binary_url": master_release_obj.binary_url,
            }

            download_token = token_obj.make_token(master_release_obj.release_id, 600, key=key, force_new=True)
            datainfo["download_token"] = download_token
            return datainfo
        else:
            return {}


class AppReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppReleaseInfo
        fields = ["app_version", "icon_url", "build_version",
                  "release_type", "minimum_os_version",
                  "created_time", "binary_size", "release_id", "size", "type", "editing", "master_color", "changelog",
                  "is_master", 'download_token', 'binary_url', 'udid', 'distribution_name']

    download_token = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    editing = serializers.SerializerMethodField()
    master_color = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()
    binary_size = serializers.SerializerMethodField()
    udid = serializers.SerializerMethodField()

    def get_udid(self, obj):
        udid_lists = []
        try:
            udid_data = eval(obj.udid)
            for udid in udid_data:
                udid_lists.append({'udid': udid})
        except Exception as e:
            pass
        return udid_lists

    def get_binary_size(self, obj):
        return bytes2human(obj.binary_size)

    def get_download_token(self, obj):
        return token_obj.make_token(obj.release_id, 600)

    def get_icon_url(self, obj):
        return get_download_url_from_context(self, obj, '', os.path.basename(obj.icon_url), force_new=False)

    def get_master_color(self, obj):
        if obj.is_master:
            return '#0bbd87'

    def get_size(self, obj):
        return "large"

    def get_type(self, obj):
        return "primary"

    def get_editing(self, obj):
        return {"changelog": False, "binary_url": False}


class AdminAppReleaseSerializer(AppReleaseSerializer):
    class Meta:
        model = models.AppReleaseInfo
        fields = "__all__"
        read_only_fields = ["id", "app_id", "release_id", "binary_size"]

    release_choices = serializers.SerializerMethodField()

    def get_release_choices(self, obj):
        return get_choices_dict(obj.release_choices)

    def update(self, instance, validated_data):
        if validated_data.get("is_master", False):
            models.AppReleaseInfo.objects.filter(app_id=instance.app_id).update(**{"is_master": False})
        else:
            if "is_master" in validated_data and validated_data.get("is_master") != True:
                del validated_data["is_master"]
        return super(AdminAppReleaseSerializer, self).update(instance, validated_data)


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppStorage
        exclude = ["user_id"]

    storage_type_display = serializers.CharField(source="get_storage_type_display", read_only=True)

    download_auth_type_choices = serializers.SerializerMethodField()

    def get_download_auth_type_choices(self, obj):
        return get_choices_dict(obj.download_auth_type_choices)

    def create(self, validated_data):
        if self.context.get("user_obj", None) and self.context.get("user_obj") != "undefined":
            user_obj = self.context.get("user_obj", None)
            if user_obj:
                storage_obj = models.AppStorage.objects.create(**validated_data, user_id=user_obj)
                return storage_obj
        return None


class AdminStorageSerializer(StorageSerializer):
    class Meta:
        model = models.AppStorage
        fields = "__all__"
        read_only_fields = ["id", "user_id", "updated_time", "created_time", "storage_type"]

    storage_choices = serializers.SerializerMethodField()

    def get_storage_choices(self, obj):
        return get_choices_dict(obj.storage_choices[1:])

    used_id = serializers.SerializerMethodField()

    def get_used_id(self, obj):
        return obj.user_id_id


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppIOSDeveloperInfo
        # depth = 1
        exclude = ["password", "id", "user_id", "p8key"]

    developer_used_number = serializers.SerializerMethodField()
    developer_used_other_number = serializers.SerializerMethodField()

    def get_developer_used_number(self, obj):
        return models.UDIDsyncDeveloper.objects.filter(developerid=obj).count()

    def get_developer_used_other_number(self, obj):
        return get_developer_udided(obj)[0]


class SuperSignUsedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.APPSuperSignUsedInfo
        # depth = 1
        fields = ["created_time", "device_udid", "device_name", "developer_id", "bundle_id", "bundle_name"]

    device_udid = serializers.SerializerMethodField()
    device_name = serializers.SerializerMethodField()
    developer_id = serializers.SerializerMethodField()
    bundle_id = serializers.SerializerMethodField()
    bundle_name = serializers.SerializerMethodField()

    def get_device_udid(self, obj):
        return obj.udid.udid

    def get_device_name(self, obj):
        return obj.udid.product

    def get_developer_id(self, obj):
        developer_id = obj.developerid.email
        if obj.developerid.issuer_id:
            developer_id = obj.developerid.issuer_id
        return developer_id

    def get_bundle_id(self, obj):
        return obj.app_id.bundle_id

    def get_bundle_name(self, obj):
        return obj.app_id.name


class DeviceUDIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppUDID
        # depth = 1
        exclude = ["binary_file", "updated_time", "is_signed"]

    bundle_id = serializers.SerializerMethodField()
    bundle_name = serializers.SerializerMethodField()

    def get_bundle_id(self, obj):
        return obj.app_id.bundle_id

    def get_bundle_name(self, obj):
        return obj.app_id.name


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Price
        exclude = ["id"]


class OrdersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        exclude = ["id"]


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


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CertificationInfo
        fields = ["certification_url", "type"]

    certification_url = serializers.SerializerMethodField()

    def get_certification_url(self, obj):
        return get_download_url_from_context(self, obj, '', obj.certification_url)


class UserCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserCertificationInfo
        exclude = ["id", "user_id", "created_time"]


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
