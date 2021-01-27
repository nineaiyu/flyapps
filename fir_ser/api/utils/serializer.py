from rest_framework import serializers
from api import models
from api.utils.app.apputils import bytes2human
from api.utils.TokenManager import DownloadToken
from api.utils.storage.storage import Storage
from api.utils.utils import get_developer_udided
import os, json, logging

logger = logging.getLogger(__file__)

token_obj = DownloadToken()


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserInfo
        # fields="__all__"
        # exclude = ["password","is_active","user_permissions","role",]
        fields = ["username", "uid", "mobile", "job", "email", "domain_name", "last_login", "first_name",
                  'head_img', 'storage_active', 'supersign_active']

    head_img = serializers.SerializerMethodField()

    def get_head_img(self, obj):
        storage = Storage(obj)
        return storage.get_download_url(obj.head_img)


class AppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        # depth = 1
        exclude = ["user_id", "id"]

    has_combo = serializers.SerializerMethodField()

    def get_has_combo(self, obj):
        if obj.has_combo:
            obj.has_combo.has_combo = None
            return AppsSerializer(obj.has_combo, context=self.context).data

    master_release = serializers.SerializerMethodField()

    def get_master_release(self, obj):
        master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj, is_master=True).first()
        if self.context.get("release_id", None) and self.context.get("release_id") != "undefined":
            master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj,
                                                                      release_id=self.context.get("release_id")).first()
        if master_release_obj:

            icon_url = ""
            key = ''
            if self.context.get("key", None) and self.context.get("key") != "undefined":
                key = self.context.get("key", '')
            if self.context.get("storage", None) and self.context.get("storage") != "undefined":
                storage = self.context.get("storage", None)
                icon_url = storage.get_download_url(os.path.basename(master_release_obj.icon_url), 600, key=key)
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


class AppsShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        fields = ["app_id", "name", "short", "has_combo", "isshow", "description", "need_password", 'master_release',
                  'type', 'issupersign', 'wxeasytype', 'wxredirect']

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
        master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj, is_master=True).first()
        if self.context.get("release_id", None) and self.context.get("release_id") != "undefined":
            master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj,
                                                                      release_id=self.context.get("release_id")).first()
        if master_release_obj:

            icon_url = ""
            key = ''
            if self.context.get("key", None) and self.context.get("key") != "undefined":
                key = self.context.get("key", '')
            if self.context.get("storage", None) and self.context.get("storage") != "undefined":
                storage = self.context.get("storage", None)
                icon_url = storage.get_download_url(os.path.basename(master_release_obj.icon_url), 600, key=key,
                                                    force_new=True)
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
                  "is_master", 'download_token', 'binary_url', 'udid']

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

        download_token = token_obj.make_token(obj.release_id, 600)

        return download_token

    def get_icon_url(self, obj):
        icon_url = ""
        key = ''
        if self.context.get("key", None) and self.context.get("key") != "undefined":
            key = self.context.get("key", '')
        if self.context.get("storage", None) and self.context.get("storage") != "undefined":
            storage = self.context.get("storage", None)
            icon_url = storage.get_download_url(os.path.basename(obj.icon_url), 600, key=key)

        return icon_url

    def get_master_color(self, obj):
        if obj.is_master:
            return '#0bbd87'

    def get_size(self, obj):
        return "large"

    def get_type(self, obj):
        return "primary"

    def get_editing(self, obj):
        return {"changelog": False, "binary_url": False}


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppStorage
        exclude = ["user_id"]

    storage_type_display = serializers.CharField(source="get_storage_type_display", read_only=True)
    additionalparameters = serializers.CharField(write_only=True)
    additionalparameter = serializers.SerializerMethodField(read_only=True)

    def get_additionalparameter(self, obj):
        infos = {}
        try:
            infos = json.loads(obj.additionalparameters)
        except Exception as e:
            logger.error("%s additionalparameter loads failed Exception:%s" % (obj.additionalparameters, e))
        return infos

    def create(self, validated_data):
        if self.context.get("user_obj", None) and self.context.get("user_obj") != "undefined":
            user_obj = self.context.get("user_obj", None)
            if user_obj:
                storage_obj = models.AppStorage.objects.create(**validated_data, user_id=user_obj)
                return storage_obj
        return None


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppIOSDeveloperInfo
        # depth = 1
        exclude = ["password", "id", "user_id"]

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
        return obj.developerid.email

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
