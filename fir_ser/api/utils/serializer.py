from rest_framework import serializers
from api import models
from api.utils.app.apputils import bytes2human
from api.utils.storage.storage import Storage

import os



class UserInfoSerializer(serializers.ModelSerializer):
    # gender = serializers.SerializerMethodField(source="get_gender_display")

    # def get_gender(self, obj):
    #     return obj.gender

    class Meta:
        model = models.UserInfo
        # fields="__all__"
        # exclude = ["password","is_active","user_permissions","role",]
        fields=["username","uid","qq","mobile","job","email","domain_name","last_login","first_name",'head_img']
    head_img = serializers.SerializerMethodField()
    def get_head_img(self,obj):
        return "/".join([obj.domain_name, obj.head_img])


class AppsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Apps
        # depth = 1
        exclude = ["user_id", "id"]

    has_combo = serializers.SerializerMethodField()

    def get_has_combo(self, obj):
        if obj.has_combo:
            obj.has_combo.has_combo = None
            return AppsSerializer(obj.has_combo,context=self.context).data

    master_release = serializers.SerializerMethodField()

    def get_master_release(self, obj):
        master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj, is_master=True).first()
        if self.context.get("release_id", None) and self.context.get("release_id") != "undefined":
            master_release_obj = models.AppReleaseInfo.objects.filter(app_id=obj,
                                                                      release_id=self.context.get("release_id")).first()
        if master_release_obj:

            icon_url = "/".join([obj.user_id.domain_name, master_release_obj.icon_url])

            if self.context.get("storage", None) and self.context.get("storage") != "undefined":
                storage = self.context.get("storage", None)
                icon_url = storage.get_download_url(os.path.basename(master_release_obj.icon_url))
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
                "binary_url":master_release_obj.binary_url,
            }

            if self.context.get("download_token", None) and self.context.get("download_token") != "download_token":
                download_url = "/".join([obj.user_id.domain_name, "download", master_release_obj.release_id])
                download_url = download_url + "?token=" + self.context.get("download_token")
                if obj.type == 0:
                    apptype='.apk'
                else:
                    apptype = '.ipa'
                if self.context.get("storage", None) and self.context.get("storage") != "undefined":
                    storage = self.context.get("storage", None)
                    download_url = storage.get_download_url(master_release_obj.release_id+apptype)
                datainfo["download_url"] = download_url

            return datainfo
        else:
            return {}






class AppReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AppReleaseInfo
        fields = ["app_version", "icon_url", "build_version",
                  "release_type", "minimum_os_version",
                  "created_time", "binary_size", "release_id", "size", "type", "editing", "master_color", "changelog",
                  "is_master",'download_url','binary_url']
    download_url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    editing = serializers.SerializerMethodField()
    master_color = serializers.SerializerMethodField()
    icon_url = serializers.SerializerMethodField()
    binary_size= serializers.SerializerMethodField()



    def get_binary_size(self,obj):
        return bytes2human(obj.binary_size)

    def get_download_url(self,obj):

        # download_url = "/".join([obj.app_id.user_id.domain_name, "download", obj.release_id])
        # download_url = download_url + "?token=" + make_download_token(obj.release_id,300)
        download_url=''
        if obj.release_type == 0:
            apptype = '.apk'
        else:
            apptype = '.ipa'
        if self.context.get("storage", None) and self.context.get("storage") != "undefined":
            storage = self.context.get("storage", None)
            download_url = storage.get_download_url(obj.release_id + apptype)
        return download_url

    def get_icon_url(self, obj):
        icon_url="/".join([obj.app_id.user_id.domain_name, obj.icon_url])
        if self.context.get("storage", None) and self.context.get("storage") != "undefined":
            storage = self.context.get("storage", None)
            icon_url = storage.get_download_url(os.path.basename(obj.icon_url))

        return icon_url

    def get_master_color(self, obj):
        if obj.is_master:
            return '#0bbd87'

    def get_size(self, obj):
        return "large"

    def get_type(self, obj):
        return "primary"

    def get_editing(self, obj):
        return {"changelog":False,"binary_url":False}
