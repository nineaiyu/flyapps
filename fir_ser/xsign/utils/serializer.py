import logging

from django.db.models import Sum
from rest_framework import serializers

from common.base.baseutils import AppleDeveloperUid, get_choices_dict
from common.core.sysconfig import Config
from xsign import models
from xsign.utils.modelutils import get_developer_udided, get_use_number

logger = logging.getLogger(__name__)


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
    status_display = serializers.CharField(source="get_status_display")

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
        app_id = self.context.get('app_id', '')
        if app_id:
            developer_app_obj = models.DeveloperAppID.objects.filter(developerid=obj,
                                                                     developerid__status__in=Config.DEVELOPER_USE_STATUS,
                                                                     developerid__certid__isnull=False)
            if developer_app_obj.filter(app_id__app_id=app_id).distinct().count():
                return False
            else:
                if developer_app_obj and developer_app_obj.distinct().count() < obj.app_limit_number:
                    return False
            return True
        return True

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
        return get_use_number(obj)

    def get_app_used_count(self, obj):
        return models.DeveloperAppID.objects.filter(developerid=obj).count()


class SuperSignUsedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.APPSuperSignUsedInfo
        fields = ["created_time", "device_udid", "device_name", "developer_id", "bundle_id", "bundle_name", "other_uid",
                  "developer_description", "developer_status"]

    device_udid = serializers.CharField(source="udid.udid.udid")
    device_name = serializers.CharField(source="udid.product")
    bundle_id = serializers.CharField(source="app_id.bundle_id")
    bundle_name = serializers.CharField(source="app_id.name")
    other_uid = serializers.SerializerMethodField()
    developer_id = serializers.SerializerMethodField()
    developer_description = serializers.SerializerMethodField()
    developer_status = serializers.SerializerMethodField()

    def get_developer_status(self, obj):
        return obj.developerid.get_status_display()

    def get_developer_id(self, obj):
        issuer_id = obj.developerid.issuer_id
        if self.context.get('mine'):
            return issuer_id
        else:
            return f"{Config.DEVELOPER_UID_KEY}{AppleDeveloperUid().get_encrypt_uid(issuer_id)}"

    def get_developer_description(self, obj):
        if self.context.get('mine'):
            return obj.developerid.description
        else:
            return '公共账号池'

    def get_other_uid(self, obj):
        user_obj = self.context.get('user_obj')
        if obj.user_id != obj.developerid.user_id:
            if user_obj.uid != obj.user_id.uid:
                return {'uid': obj.user_id.uid, 'name': obj.user_id.first_name}


class DeveloperDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UDIDsyncDeveloper
        exclude = ["id", "developerid"]

    developer_id = serializers.CharField(source="developerid.issuer_id")
    developer_description = serializers.CharField(source="developerid.description")
    developer_status = serializers.CharField(source="developerid.get_status_display")
    device_status = serializers.CharField(source="get_status_display")
    app_used_count = serializers.SerializerMethodField()

    def get_app_used_count(self, obj):
        return models.DeveloperDevicesID.objects.filter(udid=obj, developerid=obj.developerid).values(
            'app_id').distinct().count()


class DeviceUDIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppUDID
        # depth = 1
        exclude = ["updated_time", "sign_status"]

    bundle_name = serializers.CharField(source="app_id.name")
    bundle_id = serializers.CharField(source="app_id.bundle_id")
    issuer_id = serializers.SerializerMethodField()
    developer_description = serializers.SerializerMethodField()
    developer_status = serializers.SerializerMethodField()
    udid = serializers.CharField(source="udid.udid")
    is_mine = serializers.SerializerMethodField()
    other_uid = serializers.SerializerMethodField()
    can_resign = serializers.SerializerMethodField()

    def get_can_resign(self, obj):
        return obj.udid.developerid.status in Config.DEVELOPER_RESIGN_STATUS

    def get_issuer_id(self, obj):
        issuer_id = obj.udid.developerid.issuer_id
        if self.context.get('mine'):
            return issuer_id
        else:
            return f"{Config.DEVELOPER_UID_KEY}{AppleDeveloperUid().get_encrypt_uid(issuer_id)}"

    def get_developer_status(self, obj):
        return obj.udid.developerid.get_status_display()

    def get_developer_description(self, obj):
        if self.context.get('mine'):
            return obj.udid.developerid.description
        else:
            return '公共账号池'

    def get_other_uid(self, obj):
        user_obj = self.context.get('user_obj')
        user_obj_new = obj.app_id.user_id
        if user_obj.pk != user_obj_new.pk:
            super_user_obj = models.APPSuperSignUsedInfo.objects.filter(udid=obj, app_id=obj.app_id).first()
            if super_user_obj.developerid.user_id != user_obj_new:
                return {'uid': user_obj_new.uid, 'name': user_obj_new.first_name}

    def get_is_mine(self, obj):
        return self.context.get('mine')


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
        exclude = ["user_id", "developer_info", "app_info", "udid_sync_info", "app_id"]

    app_name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    is_used = serializers.SerializerMethodField()
    app_status = serializers.SerializerMethodField()
    remote_addr = serializers.SerializerMethodField()

    def get_remote_addr(self, obj):
        return obj.remote_addr

    def get_app_status(self, obj):
        if obj.app_id:
            return True
        return False

    def get_is_used(self, obj):
        if obj.udid_sync_info:
            return True
        return False

    def get_app_name(self, obj):
        if obj.app_info:
            return obj.app_info.get('name')

    def get_description(self, obj):
        if obj.udid:
            return f"{self.get_app_name(obj)}-消耗- {obj.number} 设备数"


class BillTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IosDeveloperBill
        exclude = ["id", "remote_addr", "user_id", "to_user_id"]

    target_user = serializers.SerializerMethodField()
    cancel = serializers.SerializerMethodField()
    number = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display')

    def get_target_user(self, obj):
        user_obj = obj.user_id
        if self.get_cancel(obj):
            user_obj = obj.to_user_id
        return {'uid': user_obj.uid, 'name': user_obj.first_name}

    def get_cancel(self, obj):
        return self.context.get('user_obj').pk == obj.user_id.pk

    def get_number(self, obj):
        if self.get_cancel(obj):
            return -obj.number
        else:
            return obj.number


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


class AdminBillInfoSerializer(BillInfoSerializer):
    class Meta:
        model = models.IosDeveloperPublicPoolBill
        fields = '__all__'
        read_only_fields = ["id", "user_id", "to_user_id", "action", "number", "app_info", "udid",
                            "udid_sync_info", "app_id", "remote_addr"]


class AppSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        exclude = ["user_id", "id"]

    private_developer_number = serializers.SerializerMethodField()

    def get_private_developer_number(self, obj):
        return models.AppleDeveloperToAppUse.objects.filter(app_id=obj).count()

    private_developer_used_number = serializers.SerializerMethodField()

    def get_private_developer_used_number(self, obj):
        return models.DeveloperDevicesID.objects.filter(app_id=obj,
                                                        developerid__appledevelopertoappuse__app_id=obj).distinct().count()

    supersign_used_number = serializers.SerializerMethodField()

    def get_supersign_used_number(self, obj):
        return models.APPSuperSignUsedInfo.objects.filter(app_id=obj).all().count()

    developer_used_count = serializers.SerializerMethodField()

    def get_developer_used_count(self, obj):
        return models.DeveloperAppID.objects.filter(app_id=obj).all().count()


class AppleSignMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppleSignMessage
        exclude = ["user_id", "id", "developerid", "app_id"]

    developer_id = serializers.CharField(source="developerid.issuer_id")
    developer_description = serializers.CharField(source="developerid.description")
    developer_status = serializers.CharField(source="developerid.get_status_display")
    app_info = serializers.SerializerMethodField()

    def get_app_info(self, obj):
        if obj.app_id:
            return {'bundle_name': obj.app_id.name, 'bundle_id': obj.app_id.bundle_id}
        return {}


class AbnormalDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceAbnormalUDID
        exclude = ["user_id", "udid"]

    udid_info = serializers.SerializerMethodField()

    def get_udid_info(self, obj):
        return DeveloperDeviceSerializer(obj.udid).data


class BlackDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeviceBlackUDID
        exclude = ["user_id"]
