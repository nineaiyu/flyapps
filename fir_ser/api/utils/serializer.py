import logging
import os

from django.db.models import Sum
from rest_framework import serializers

from api import models
from api.utils.TokenManager import make_token
from api.utils.app.apputils import bytes2human
from api.utils.modelutils import get_user_domain_name, get_app_domain_name, get_redirect_server_domain
from api.utils.storage.caches import get_user_free_download_times, get_user_cert_auth_status
from api.utils.storage.storage import Storage
from api.utils.utils import get_developer_udided, get_choices_dict, get_choices_name_from_key

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


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        fields = ["username", "uid", "mobile", "job", "email", "domain_name", "role", "first_name",
                  'head_img', 'storage_active', 'supersign_active', 'free_download_times', 'download_times',
                  'certification', 'qrcode_domain_name']

    head_img = serializers.SerializerMethodField()

    def get_head_img(self, obj):
        return get_download_url_from_context(self, obj, '', obj.head_img)

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

    domain_name = serializers.SerializerMethodField()

    def get_domain_name(self, obj):
        return get_user_domain_name(obj)

    qrcode_domain_name = serializers.SerializerMethodField()

    def get_qrcode_domain_name(self, obj):
        if obj.role and obj.role > 1:
            return get_user_domain_name(obj, 0)


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


class AppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        exclude = ["user_id", "id"]

    has_combo = serializers.SerializerMethodField()

    def get_has_combo(self, obj):
        if obj.has_combo:
            obj.has_combo.has_combo = None
            return AppsListSerializer(obj.has_combo, context=self.context).data

    preview_url = serializers.SerializerMethodField()

    def get_preview_url(self, obj):
        return get_redirect_server_domain(None, obj.user_id, get_app_domain_name(obj))

    private_developer_number = serializers.SerializerMethodField()

    def get_private_developer_number(self, obj):
        return models.AppleDeveloperToAppUse.objects.filter(app_id=obj).count()

    private_developer_used_number = serializers.SerializerMethodField()

    def get_private_developer_used_number(self, obj):
        return models.DeveloperDevicesID.objects.filter(app_id=obj,
                                                        developerid__appledevelopertoappuse__app_id=obj).distinct().count()

    domain_name = serializers.SerializerMethodField()

    def get_domain_name(self, obj):
        return get_app_domain_name(obj)

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

            download_token = make_token(master_release_obj.release_id, 600, key=key)
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


class AppsListSerializer(AppsSerializer):
    class Meta:
        model = models.Apps
        fields = ["app_id", "bundle_id", "issupersign", "name", "preview_url", "short", "type", "master_release",
                  "has_combo"]

    def get_master_release(self, obj):
        master_release_obj = get_app_master_obj_from_context(self, obj)
        if master_release_obj:
            key = ''
            icon_url = get_download_url_from_context(self, obj, key, master_release_obj.icon_url)
            datainfo = {
                "app_version": master_release_obj.app_version,
                "icon_url": icon_url,
                "build_version": master_release_obj.build_version,
                "binary_size": bytes2human(master_release_obj.binary_size),
                "binary_url": master_release_obj.binary_url,
                "release_type": master_release_obj.release_type,
            }
            return datainfo
        else:
            return {}

    def get_has_combo(self, obj):
        if obj.has_combo:
            obj.has_combo.has_combo = None
            return AppsListSerializer(obj.has_combo, context=self.context).data


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

    domain_name = serializers.SerializerMethodField()

    def get_domain_name(self, obj):
        return get_app_domain_name(obj)

    need_password = serializers.SerializerMethodField()

    def get_need_password(self, obj):
        if obj.password != '':
            return True
        return False

    has_combo = serializers.SerializerMethodField()

    def get_has_combo(self, obj):
        if obj.has_combo:
            obj.has_combo.has_combo = None
            if obj.has_combo.isshow and obj.has_combo.status == 1:
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

            download_token = make_token(master_release_obj.release_id, 600, key=key, force_new=True)
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
    size = serializers.CharField(default='large')
    type = serializers.CharField(default='primary')
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
        return make_token(obj.release_id, 600)

    def get_icon_url(self, obj):
        return get_download_url_from_context(self, obj, '', os.path.basename(obj.icon_url))

    def get_master_color(self, obj):
        if obj.is_master:
            return '#0bbd87'

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

    # secret_key = serializers.SerializerMethodField()
    # 加上此选项，会导致update获取不到值
    # def get_secret_key(self, obj):
    #     return ''

    # def validate_secret_key(self, secret_key):
    #     ...

    def get_download_auth_type_choices(self, obj):
        return get_choices_dict(obj.download_auth_type_choices)

    def create(self, validated_data):
        if self.context.get("user_obj", None) and self.context.get("user_obj") != "undefined":
            user_obj = self.context.get("user_obj", None)
            if user_obj:
                storage_obj = models.AppStorage.objects.create(**validated_data, user_id=user_obj)
                return storage_obj
        return None

    def update(self, instance, validated_data):
        secret_key = validated_data.get('secret_key', '')
        if secret_key != "" and secret_key != instance.secret_key:
            ...
        else:
            validated_data['secret_key'] = instance.secret_key
        return super().update(instance, validated_data)


class AdminStorageSerializer(StorageSerializer):
    class Meta:
        model = models.AppStorage
        fields = "__all__"
        read_only_fields = ["id", "user_id", "updated_time", "created_time", "storage_type"]

    storage_choices = serializers.SerializerMethodField()

    def get_storage_choices(self, obj):
        return get_choices_dict(obj.storage_choices[1:])

    used_id = serializers.IntegerField(source="user_id.pk")


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppIOSDeveloperInfo
        # depth = 1
        exclude = ["id", "user_id", "p8key"]

    developer_used_number = serializers.SerializerMethodField()
    developer_used_other_number = serializers.SerializerMethodField()
    use_number = serializers.SerializerMethodField()
    app_used_count = serializers.SerializerMethodField()
    is_disabled = serializers.SerializerMethodField()
    app_private_number = serializers.SerializerMethodField()
    app_private_used_number = serializers.SerializerMethodField()
    app_usable_number = serializers.SerializerMethodField()
    app_used_number = serializers.SerializerMethodField()
    private_usable_number = serializers.SerializerMethodField()

    def get_app_usable_number(self, obj):
        app_id = self.context.get('app_id')
        if app_id:
            apple_to_app_obj = models.AppleDeveloperToAppUse.objects.filter(developerid=obj,
                                                                            app_id__app_id=app_id).first()
            if apple_to_app_obj:
                return apple_to_app_obj.usable_number
        return 0

    def get_app_used_number(self, obj):
        app_id = self.context.get('app_id', '')
        if app_id:
            return models.DeveloperDevicesID.objects.filter(developerid=obj,
                                                            app_id__app_id=app_id).distinct().count()
        return 0

    def get_developer_used_number(self, obj):
        return models.UDIDsyncDeveloper.objects.filter(developerid=obj).count()

    def get_developer_used_other_number(self, obj):
        return get_developer_udided(obj)[0]

    def get_is_disabled(self, obj):
        return bool(1 - obj.is_actived)

    def get_app_private_number(self, obj):
        return models.AppleDeveloperToAppUse.objects.filter(developerid=obj).count()

    def get_private_usable_number(self, obj):
        used_number = models.AppleDeveloperToAppUse.objects.filter(developerid=obj).values('usable_number').aggregate(
            Sum('usable_number')).get('usable_number__sum')
        if not used_number:
            used_number = 0
        return used_number

    def get_app_private_used_number(self, obj):
        return models.DeveloperDevicesID.objects.filter(developerid=obj,
                                                        app_id__appledevelopertoappuse__developerid=obj).values(
            'udid').distinct().count()

    def get_use_number(self, obj):
        return models.DeveloperDevicesID.objects.filter(developerid=obj).values('udid').distinct().count()

    def get_app_used_count(self, obj):
        return models.DeveloperAppID.objects.filter(developerid=obj).count()


class AdminDeveloperSerializer(DeveloperSerializer):
    class Meta:
        model = models.AppIOSDeveloperInfo
        # depth = 1
        exclude = ["p8key", ]

    auth_type_choices = serializers.SerializerMethodField()

    def get_auth_type_choices(self, obj):
        return get_choices_dict(obj.auth_type_choices)


class SuperSignUsedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.APPSuperSignUsedInfo
        fields = ["created_time", "device_udid", "device_name", "developer_id", "bundle_id", "bundle_name", "other_uid", "developer_description"]

    device_udid = serializers.CharField(source="udid.udid.udid")
    device_name = serializers.CharField(source="udid.product")
    bundle_id = serializers.CharField(source="app_id.bundle_id")
    bundle_name = serializers.CharField(source="app_id.name")
    other_uid = serializers.SerializerMethodField()
    developer_id = serializers.SerializerMethodField()
    developer_description = serializers.SerializerMethodField()

    def get_developer_id(self, obj):
        if self.context.get('mine'):
            return obj.developerid.issuer_id
        else:
            return '公共账号池'

    def get_developer_description(self, obj):
        if self.context.get('mine'):
            return obj.developerid.description
        else:
            return '公共账号池'

    def get_other_uid(self, obj):
        user_obj = self.context.get('user_obj')
        role = 0
        if user_obj:
            role = user_obj.role
        if role == 3:
            if obj.user_id != obj.developerid.user_id:
                return obj.user_id.uid


class AdminSuperSignUsedSerializer(SuperSignUsedSerializer):
    class Meta:
        model = models.APPSuperSignUsedInfo
        fields = ["created_time", "device_udid", "device_name", "developer_id", "bundle_id", "bundle_name", "app_id",
                  "id", "user_id", "short", "developer_pk"]

    app_id = serializers.IntegerField(source="app_id.pk")

    user_id = serializers.IntegerField(source="user_id.pk")

    short = serializers.CharField(source="app_id.short")

    developer_pk = serializers.IntegerField(source="developerid.pk")


class DeveloperDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UDIDsyncDeveloper
        exclude = ["id", "developerid"]

    developer_id = serializers.CharField(source="developerid.issuer_id")
    developer_description = serializers.CharField(source="developerid.description")


class DeviceUDIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppUDID
        # depth = 1
        exclude = ["updated_time", "is_signed"]

    bundle_name = serializers.CharField(source="app_id.name")
    bundle_id = serializers.CharField(source="app_id.bundle_id")
    issuer_id = serializers.SerializerMethodField()
    developer_description = serializers.SerializerMethodField()
    udid = serializers.CharField(source="udid.udid")
    is_mine = serializers.SerializerMethodField()
    other_uid = serializers.SerializerMethodField()

    def get_issuer_id(self, obj):
        if self.context.get('mine'):
            return obj.udid.developerid.issuer_id
        else:
            return '公共账号池'

    def get_developer_description(self, obj):
        if self.context.get('mine'):
            return obj.udid.developerid.description
        else:
            return '公共账号池'

    def get_other_uid(self, obj):
        user_obj = self.context.get('user_obj')
        role = 0
        if user_obj:
            role = user_obj.role
        if role == 3:
            super_user_obj = models.APPSuperSignUsedInfo.objects.filter(udid=obj, app_id=obj.app_id).first()
            if super_user_obj.developerid.user_id != obj.app_id.user_id:
                return obj.app_id.user_id.uid

    def get_is_mine(self, obj):
        return self.context.get('mine')


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


class ThirdWxSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ThirdWeChatUserInfo
        exclude = ["id", "sex", "address", "user_id"]


class AdminThirdWxSerializer(ThirdWxSerializer):
    class Meta:
        model = models.ThirdWeChatUserInfo
        fields = "__all__"
        read_only_fields = ["id", "openid", "user_id", "head_img_url"]


class DomainNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserDomainInfo
        exclude = ["id", "user_id"]

    app_info = serializers.SerializerMethodField()

    def get_app_info(self, obj):
        app_obj = obj.app_id
        if app_obj:
            app_info = {
                'app_id': app_obj.app_id,
                'name': app_obj.name,
            }
            return app_info
        return {}


class AdminDomainNameSerializer(DomainNameSerializer):
    class Meta:
        model = models.UserDomainInfo
        fields = "__all__"
        read_only_fields = ["id", "app_id", "domain_type", "created_time", "cname_id"]

    domain_type_choices = serializers.SerializerMethodField()

    def get_domain_type_choices(self, obj):
        return get_choices_dict(obj.domain_type_choices)


class UserAdInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserAdDisplayInfo
        exclude = ["user_id"]

    ad_pic = serializers.SerializerMethodField()

    def get_ad_pic(self, obj):
        return get_download_url_from_context(self, obj, '', obj.ad_pic)


class AppAdInfoSerializer(UserAdInfoSerializer):
    class Meta:
        model = models.UserAdDisplayInfo
        fields = ["ad_uri", "ad_pic"]

    ad_pic = serializers.SerializerMethodField()

    def get_ad_pic(self, obj):
        return get_download_url_from_context(self, obj, '', obj.ad_pic, True)


class BillAppInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        fields = ["pk", "app_id", "user_id", "name", "type", "bundle_id", "updated_time"]


class BillDeveloperInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppIOSDeveloperInfo
        fields = ["pk", "issuer_id", "user_id", "certid"]


class BillInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IosDeveloperPublicPoolBill
        exclude = ["user_id", "to_user_id", "developer_info", "app_info", "udid_sync_info", "app_id"]

    app_name = serializers.SerializerMethodField()
    action = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    is_used = serializers.SerializerMethodField()
    app_status = serializers.SerializerMethodField()
    remote_addr = serializers.SerializerMethodField()

    def get_remote_addr(self, obj):
        if obj.to_user_id == self.context.get('user_obj'):
            return ''
        return obj.remote_addr

    def get_app_status(self, obj):
        if obj.app_id:
            return True
        return False

    def get_is_used(self, obj):
        if obj.udid_sync_info or obj.to_user_id:
            return True
        return False

    def get_action(self, obj):
        return get_choices_name_from_key(obj.action_choices, obj.action)

    def get_app_name(self, obj):
        if obj.app_info:
            return obj.app_info.get('name')
        elif obj.to_user_id:
            return obj.user_id.first_name

    def get_description(self, obj):
        if obj.udid:
            return f"{self.get_app_name(obj)}-{self.get_action(obj)} -{obj.number} 设备数"
        if obj.to_user_id:
            if obj.to_user_id == self.context.get('user_obj'):
                return f"{obj.user_id.first_name}-{self.get_action(obj)} +{obj.number} 设备数"
            else:
                return f"向 {obj.to_user_id.first_name} {self.get_action(obj)} -{obj.number} 设备数"


class AdminBillInfoSerializer(BillInfoSerializer):
    class Meta:
        model = models.IosDeveloperPublicPoolBill
        fields = '__all__'
        read_only_fields = ["id", "user_id", "to_user_id", "action", "number", "app_info", "udid",
                            "udid_sync_info", "app_id", "remote_addr"]

    action_choices = serializers.SerializerMethodField()

    def get_action_choices(self, obj):
        return get_choices_dict(obj.action_choices)


class AppReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppReportInfo
        exclude = ["id"]


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


class AppleDeveloperToAppUseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppleDeveloperToAppUse
        # exclude = ["user_id", "to_user_id", "developer_info", "app_info", "udid_sync_info", "app_id"]
        fields = ["issuer_id", "app_id", "created_time", "description", "usable_number"]

    issuer_id = serializers.CharField(source="developerid.issuer_id")
    app_id = serializers.CharField(source="app_id.app_id")


class AppleDeveloperToAppUseAppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        fields = ["app_id", "name", "short", "bundle_id", "description", "app_usable_number", "app_used_number"]

    app_usable_number = serializers.SerializerMethodField()
    app_used_number = serializers.SerializerMethodField()

    def get_app_usable_number(self, obj):
        issuer_id = self.context.get('issuer_id')
        if issuer_id:
            apple_to_app_obj = models.AppleDeveloperToAppUse.objects.filter(developerid__issuer_id=issuer_id,
                                                                            app_id=obj).first()
            if apple_to_app_obj:
                return apple_to_app_obj.usable_number
        return 0

    def get_app_used_number(self, obj):
        issuer_id = self.context.get('issuer_id')
        if issuer_id:
            return models.DeveloperDevicesID.objects.filter(app_id=obj, developerid__issuer_id=issuer_id).count()
        return 0
