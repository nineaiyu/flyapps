from django.db import models

from api.models import Apps, UserInfo
from common.base.daobase import AESCharField
from common.constants import DeviceStatus, AppleDeveloperStatus, SignStatus


class AppIOSDeveloperInfo(models.Model):
    """
    苹果开发者信息
    """
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    issuer_id = models.CharField(max_length=64, null=False, verbose_name="标识创建认证令牌的发放者")
    private_key_id = models.CharField(max_length=64, null=False, verbose_name="密钥 ID")
    p8key = AESCharField(max_length=512, null=False, verbose_name="p8key")
    certid = models.CharField(max_length=64, blank=True, verbose_name="超级签名自动创建证书ID", null=True)
    usable_number = models.IntegerField(verbose_name="可使用设备数", default=100)
    app_limit_number = models.IntegerField(verbose_name="可分配应用数，最大160", default=100)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    cert_expire_time = models.DateTimeField(blank=True, null=True, verbose_name="证书过期时间")
    description = models.TextField('备注', blank=True, null=True, default='')
    auth_type_choices = ((0, 'p8key认证'),)
    auth_type = models.SmallIntegerField(choices=auth_type_choices, default=0, verbose_name="认证类型")

    # 协议待同意和维护中：代表只读，不可创建和注册新设备号
    status_choices = ((AppleDeveloperStatus.BAN, '疑似被封'), (AppleDeveloperStatus.INACTIVATED, '未激活'),
                      (AppleDeveloperStatus.ACTIVATED, '已激活'),
                      (AppleDeveloperStatus.AGREEMENT_NOT_AGREED, '协议待同意'),
                      (AppleDeveloperStatus.MAINTENANCE, '维护中'),
                      (AppleDeveloperStatus.CERTIFICATE_EXPIRED, '证书过期'),
                      (AppleDeveloperStatus.CERTIFICATE_MISSING, '证书丢失'),
                      (AppleDeveloperStatus.DEVICE_ABNORMAL, '设备异常'),
                      (AppleDeveloperStatus.ABNORMAL_STATUS, '状态异常'))
    status = models.SmallIntegerField(choices=status_choices, verbose_name="账户状态",
                                      default=AppleDeveloperStatus.INACTIVATED)

    clean_status = models.BooleanField(verbose_name="清理是否同时禁用设备ID", default=False)
    auto_check = models.BooleanField(verbose_name="是否自动检测开发者状态", default=False)

    class Meta:
        verbose_name = '苹果开发者账户'
        verbose_name_plural = "苹果开发者账户"
        unique_together = (('user_id', 'issuer_id'),)

    def save(self, *args, **kwargs):
        if self.usable_number > 100:
            self.usable_number = 100
        elif self.usable_number < 0:
            self.usable_number = 0

        if self.app_limit_number > 160:
            self.app_limit_number = 160
        elif self.app_limit_number < 0:
            self.app_limit_number = 0

        return super(AppIOSDeveloperInfo, self).save(*args, **kwargs)

    def __str__(self):
        return "%s-%s" % (self.user_id, self.issuer_id)


class UDIDsyncDeveloper(models.Model):
    """
    开发者设备ID记录
    """
    developerid = models.ForeignKey(to=AppIOSDeveloperInfo, on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    udid = models.CharField(max_length=64, verbose_name="udid唯一标识", db_index=True)
    product = models.CharField(max_length=64, verbose_name="产品", blank=True, null=True, )
    serial = models.CharField(max_length=64, verbose_name="序列号", blank=True, null=True, )
    version = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")  # django.utils.timezone.now()
    status_choices = ((DeviceStatus.DISABLED, '禁用'), (DeviceStatus.ENABLED, '启用'),
                      (DeviceStatus.PROCESSING, '处理中'), (DeviceStatus.INELIGIBLE, '不合格'))
    status = models.CharField(choices=status_choices, verbose_name="设备状态", default=DeviceStatus.DISABLED, max_length=16)

    class Meta:
        verbose_name = 'iOS开发平台同步设备信息'
        verbose_name_plural = "iOS开发平台同步设备信息"
        unique_together = ('udid', 'developerid',)

    def __str__(self):
        return "%s-%s-%s-%s" % (self.product, self.udid, self.developerid, self.status)


class AppUDID(models.Model):
    """
    用户发送的设备记录信息
    """
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="属于哪个APP")
    udid = models.ForeignKey(to=UDIDsyncDeveloper, verbose_name="udid唯一标识", on_delete=models.CASCADE)
    product = models.CharField(max_length=64, verbose_name="产品", blank=True, null=True, )
    serial = models.CharField(max_length=64, verbose_name="序列号", blank=True, null=True, )
    version = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    imei = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    iccid = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    sign_status_choices = ((SignStatus.SIGNATURE_PREPARE, '新设备入库准备'),
                           (SignStatus.DEVICE_REGISTRATION_COMPLETE, '设备ID已经注册'),
                           (SignStatus.APP_REGISTRATION_COMPLETE, 'bundelid已经注册'),
                           (SignStatus.PROFILE_DOWNLOAD_COMPLETE, '描述文件已经下载'),
                           (SignStatus.SIGNATURE_PACKAGE_COMPLETE, '已经完成签名打包'))
    sign_status = models.SmallIntegerField(choices=sign_status_choices, default=SignStatus.SIGNATURE_PREPARE,
                                           verbose_name="签名状态")

    class Meta:
        verbose_name = '设备详情'
        verbose_name_plural = "设备详情"
        unique_together = ('app_id', 'udid',)

    def __str__(self):
        return "%s-%s" % (self.app_id.name, self.udid)


class APPSuperSignUsedInfo(models.Model):
    """
    设备消耗统计
    """
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="属于哪个APP")
    udid = models.ForeignKey(to=AppUDID, on_delete=models.CASCADE, verbose_name="所消耗的udid")
    developerid = models.ForeignKey(to=AppIOSDeveloperInfo, on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '设备使用统计'
        verbose_name_plural = "设备使用统计"

    def __str__(self):
        return "%s-%s-%s" % (self.user_id, self.app_id, self.udid)


class APPToDeveloper(models.Model):
    """
    签名完成之后，通过该表查询 签名包地址
    """
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="属于哪个APP")
    developerid = models.ForeignKey(to=AppIOSDeveloperInfo, on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    binary_file = models.CharField(max_length=128, blank=True, verbose_name="签名包名称", null=True, unique=True)
    release_file = models.CharField(max_length=128, blank=True, verbose_name="源包名称", null=True)
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '应用开发者绑定'
        verbose_name_plural = "应用开发者绑定"

    def __str__(self):
        return "%s-%s-%s" % (self.developerid, self.app_id, self.binary_file)


class DeveloperAppID(models.Model):
    """
    苹果应用消耗某个开发者某个描述文件对应记录表，一个苹果应用对应一个苹果开发者和该开发者下面对应的描述文件
    """
    aid = models.CharField(max_length=64, null=False)  # ，apple APP 唯一标识
    profile_id = models.CharField(max_length=64, null=True, blank=True)  # ，profile_id 唯一标识
    developerid = models.ForeignKey(to=AppIOSDeveloperInfo, on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="属于哪个APP")

    class Meta:
        verbose_name = '超级签APP id'
        verbose_name_plural = "超级签APP id"
        unique_together = ('aid', 'developerid', 'app_id')

    def __str__(self):
        return "%s-%s-%s" % (self.aid, self.app_id, self.developerid)


class DeveloperDevicesID(models.Model):
    """
    苹果应用消耗某个开发者某个设备对应记录表，有一个苹果应用可能有该开发者下面多个设备记录
    """
    did = models.CharField(max_length=64, null=False)  # ，apple 设备唯一标识
    udid = models.ForeignKey(to=UDIDsyncDeveloper, on_delete=models.CASCADE, verbose_name="所消耗的udid")
    developerid = models.ForeignKey(to=AppIOSDeveloperInfo, on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="属于哪个APP")

    class Meta:
        verbose_name = '超级签Devices id'
        verbose_name_plural = "超级签Devices id"
        unique_together = ('did', 'developerid', 'app_id')

    def __str__(self):
        return "%s-%s-%s-%s" % (self.id, self.app_id, self.developerid, self.udid)


class IosDeveloperPublicPoolBill(models.Model):
    """
    苹果应用设备消费记录表
    """
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name="消耗次数", default=1)
    app_info = models.JSONField(max_length=256, verbose_name="属于哪个APP", null=True, blank=True)
    udid = models.CharField(max_length=64, verbose_name="设备udid", null=True, blank=True)
    product = models.CharField(max_length=64, verbose_name="设备udid", null=True, blank=True)
    version = models.CharField(max_length=64, verbose_name="设备udid", null=True, blank=True)
    developer_info = models.JSONField(max_length=256, verbose_name="开发者信息", null=True, blank=True)
    udid_sync_info = models.ForeignKey(to=UDIDsyncDeveloper, on_delete=models.SET_NULL, verbose_name="关联同步设备信息",
                                       null=True, blank=True)
    app_id = models.ForeignKey(to=Apps, on_delete=models.SET_NULL, verbose_name="属于哪个APP", null=True, blank=True)
    description = models.CharField(verbose_name="操作描述", max_length=128, default='', blank=True)
    remote_addr = models.GenericIPAddressField(verbose_name="远程IP地址")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = '设备消耗账单'
        verbose_name_plural = "设备消耗账单"

    def __str__(self):
        return "%s-%s" % (self.user_id, self.description)


class IosDeveloperBill(models.Model):
    """
    用户共享设备数，可将该用户设备数共享给 其他用户使用
    """
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE,
                                related_name='org_user_id')
    to_user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE,
                                   related_name='to_user_id', null=True, blank=True)

    status_choices = ((0, '失效'), (1, '已撤回'), (2, '成功'))
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="状态",
                                      help_text="0 失效 1 撤回 2 转账")
    number = models.IntegerField(verbose_name="设备数量", default=1)
    description = models.CharField(verbose_name="操作描述", max_length=128, default='', blank=True)
    remote_addr = models.GenericIPAddressField(verbose_name="远程IP地址")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '设备划转账单'
        verbose_name_plural = "设备划转账单"

    def __str__(self):
        return "%s-%s—%s" % (self.user_id, self.to_user_id, self.description)


class AppleDeveloperToAppUse(models.Model):
    """
    苹果应用专属开发者配置表
    """
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE)
    developerid = models.ForeignKey(to=AppIOSDeveloperInfo, on_delete=models.CASCADE)
    usable_number = models.IntegerField(verbose_name="可使用设备数", default=100)
    description = models.CharField(verbose_name="备注", max_length=256, default='', blank=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = '开发者专属于应用'
        verbose_name_plural = "开发者专属于应用"
        unique_together = ('app_id', 'developerid')

    def __str__(self):
        return "%s-%s" % (self.app_id.name, self.developerid.issuer_id)


class OperateMessageBase(models.Model):
    """
    操作详细记录，一般为失败的记录
    """
    user_id = models.ForeignKey(to=UserInfo, verbose_name="操作用户", on_delete=models.CASCADE)
    title = models.CharField(verbose_name="操作功能", max_length=256, default='', blank=True)
    status_choices = ((0, '失败'), (1, '成功'))
    operate_status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="状态")
    message = models.TextField(verbose_name="操作详细日志", default='', blank=True)
    operate_time = models.DateTimeField(auto_now_add=True, verbose_name="操作时间")

    class Meta:
        abstract = True


class AppleSignMessage(OperateMessageBase):
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, null=True, blank=True)
    developerid = models.ForeignKey(to=AppIOSDeveloperInfo, on_delete=models.CASCADE)

    class Meta:
        verbose_name = '应用签名操作记录'
        verbose_name_plural = "应用签名操作记录"

    def __str__(self):
        return "%s-%s-%s" % (self.app_id.name, self.developerid.issuer_id, self.title)
