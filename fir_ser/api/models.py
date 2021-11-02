from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models

from api.utils.TokenManager import generate_alphanumeric_token_of_length, generate_numeric_token_of_length
from api.utils.baseutils import make_random_uuid


# Create your models here.


######################################## 用户表 ########################################


class UserInfo(AbstractUser):
    username = models.CharField("用户名", max_length=64, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        db_index=True,
        blank=True,
        null=True
    )
    uid = models.CharField(max_length=64, unique=True, db_index=True)  # user_id，唯一标识
    mobile = models.BigIntegerField(verbose_name="手机", db_index=True, help_text="用于手机验证码登录", null=True)
    is_active = models.BooleanField(default=True, verbose_name="账户状态，默认启用")
    storage_active = models.BooleanField(default=False, verbose_name="配置存储，默认关闭")
    supersign_active = models.BooleanField(default=True, verbose_name="配置超级签，默认关闭")

    job = models.TextField("职位", max_length=128, blank=True, null=True)
    company = models.CharField("公司", max_length=128, blank=True, null=True)

    gender_choices = ((0, '保密'), (1, '男'), (2, '女'))
    gender = models.SmallIntegerField(choices=gender_choices, default=0, verbose_name="性别")
    head_img = models.CharField(max_length=256, default='head_img.jpeg',
                                verbose_name="个人头像")
    role_choices = ((0, '普通会员'), (1, 'VIP'), (2, 'SVIP'), (3, '管理员'))
    role = models.SmallIntegerField(choices=role_choices, default=0, verbose_name="角色")

    memo = models.TextField('备注', blank=True, null=True, default=None, )
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="注册时间")
    download_times = models.PositiveIntegerField(default=0, verbose_name="可用下载次数,需要用户充值")
    all_download_times = models.BigIntegerField(default=0, verbose_name="总共下载次数")
    default_domain_name = models.ForeignKey(to="DomainCnameInfo", verbose_name="默认下载页域名", on_delete=models.CASCADE)
    history_release_limit = models.IntegerField(default=10, verbose_name="app 历史记录版本", blank=True, null=True)
    storage = models.OneToOneField(to='AppStorage', related_name='app_storage',
                                   on_delete=models.SET_NULL, verbose_name="存储", null=True, blank=True)
    api_token = models.CharField(max_length=256, verbose_name='api访问密钥', default='')

    class Meta:
        verbose_name = '账户信息'
        verbose_name_plural = "账户信息"

    def __str__(self):
        return "%s_%s_%s(%s)" % (self.uid, self.email, self.mobile, self.get_role_display())

    def save(self, *args, **kwargs):
        if len(self.uid) < 8:
            self.uid = make_random_uuid()
        if len(self.api_token) < 8:
            self.api_token = self.uid + generate_alphanumeric_token_of_length(64)
        super(UserInfo, self).save(*args, **kwargs)


class ThirdWeChatUserInfo(models.Model):
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE)
    openid = models.CharField(max_length=64, unique=True, verbose_name="普通用户的标识，对当前公众号唯一")
    nickname = models.CharField(max_length=64, verbose_name="昵称", blank=True)
    sex = models.SmallIntegerField(default=0, verbose_name="性别", help_text="值为1时是男性，值为2时是女性，值为0时是未知")
    subscribe_time = models.BigIntegerField(verbose_name="订阅时间")
    head_img_url = models.CharField(max_length=256, verbose_name="用户头像", blank=True, null=True)
    address = models.CharField(max_length=128, verbose_name="地址", blank=True, null=True)
    subscribe = models.BooleanField(verbose_name="是否订阅公众号", default=0)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="授权时间")

    def __str__(self):
        return f"{self.user_id}-{self.nickname}-{self.openid}"


class Token(models.Model):
    """
    The default authorization token model.
    """
    access_token = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        UserInfo, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name="关联用户"
    )
    created = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

    def __str__(self):
        return self.access_token


class VerifyName(models.Model):
    user = models.OneToOneField(
        UserInfo, related_name='verify_info',
        on_delete=models.CASCADE, verbose_name="关联用户"
    )
    name = models.CharField(max_length=32, default="", verbose_name="真实姓名")
    id_card = models.CharField(max_length=32, blank=True, null=True, verbose_name="身份证号或护照号")
    address = models.CharField(max_length=128, blank=True, null=True, verbose_name="联系地址")
    mobile = models.BigIntegerField(blank=True, verbose_name="联系电话", null=True)
    date_verify = models.DateTimeField(auto_now_add=True, verbose_name="认证时间")

    class Meta:
        verbose_name = '实名认证'
        verbose_name_plural = "实名认证"

    def __str__(self):
        return f"self.name"


######################################## APP表 ########################################

class Apps(models.Model):
    app_id = models.CharField(max_length=64, unique=True, db_index=True)  # ，唯一标识
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE)
    type_choices = ((0, 'android'), (1, 'ios'))
    type = models.SmallIntegerField(choices=type_choices, default=0, verbose_name="类型")
    status_choices = ((0, '封禁'), (1, '正常'), (2, '违规'))
    status = models.SmallIntegerField(choices=status_choices, default=1, verbose_name="应用状态")
    name = models.CharField(max_length=32, blank=True, null=True, verbose_name="应用名称")
    short = models.CharField(max_length=16, unique=True, verbose_name="短链接", db_index=True)
    bundle_id = models.CharField(max_length=64, blank=True, verbose_name="bundle id")
    has_combo = models.OneToOneField(to="Apps", related_name='combo_app_info',
                                     verbose_name="关联应用", on_delete=models.SET_NULL, null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    count_hits = models.BigIntegerField(verbose_name="下载次数", default=0)
    password = models.CharField(verbose_name="访问密码", blank=True, help_text='默认 没有密码', max_length=32)
    isshow = models.BooleanField(verbose_name="下载页可见", default=True)
    issupersign = models.BooleanField(verbose_name="是否超级签名包", default=False)
    supersign_type_choices = ((0, '普通权限'), (1, '推送权限，请上传adhoc包'), (2, 'network、vpn、推送权限，请上传adhoc包'), (3, '特殊权限'))
    supersign_type = models.SmallIntegerField(choices=supersign_type_choices, default=1, verbose_name="签名类型")
    new_bundle_id = models.CharField(max_length=64, blank=True, null=True, verbose_name="new_bundle_id",
                                     help_text="用于超级签某些因素下需要修改包名")
    new_bundle_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="new_bundle_name",
                                       help_text="应用新名称")
    supersign_limit_number = models.IntegerField(verbose_name="签名使用限额", default=0)
    wxredirect = models.BooleanField(verbose_name="微信内第三方链接自动跳转", default=True)
    wxeasytype = models.BooleanField(verbose_name="微信内简易模式，避免微信封停", default=True)
    # domain_name = models.CharField(verbose_name="专属访问域名", blank=True, null=True, max_length=64)
    description = models.TextField('描述', blank=True, null=True, default=None, )
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '应用信息'
        verbose_name_plural = "应用信息"
        indexes = [models.Index(fields=['app_id']), models.Index(fields=['id', 'user_id', 'type'])]

    def __str__(self):
        return "%s %s-%s %s" % (self.name, self.get_type_display(), self.short, self.issupersign)


class AppScreenShot(models.Model):
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")
    screenshot_url = models.CharField(max_length=128, blank=True, verbose_name="应用截图URL")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '应用截图'
        verbose_name_plural = "应用截图"
        indexes = [models.Index(fields=['app_id'])]

    def __str__(self):
        return "%s-%s" % (self.app_id, self.screenshot_url)


class AppReleaseInfo(models.Model):
    is_master = models.BooleanField(verbose_name="是否master版本", default=True)
    release_id = models.CharField(max_length=64, unique=True, verbose_name="release 版本id", db_index=True)
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")
    build_version = models.CharField(max_length=64, verbose_name="build版本", blank=True)
    app_version = models.CharField(max_length=64, verbose_name="app版本", blank=True)
    release_choices = ((0, 'android'), (1, 'adhoc'), (2, 'Inhouse'), (3, 'unknown'))
    release_type = models.SmallIntegerField(choices=release_choices, default=0, verbose_name="版本类型")
    minimum_os_version = models.CharField(max_length=64, verbose_name="应用可安装的最低系统版本")
    binary_size = models.BigIntegerField(verbose_name="应用大小")
    binary_url = models.CharField(max_length=128, blank=True, verbose_name="第三方下载URL")
    icon_url = models.CharField(max_length=128, blank=True, verbose_name="图标url")
    changelog = models.TextField('更新日志', blank=True, null=True, default=None, )
    udid = models.TextField('ios内测版 udid', blank=True, null=True, default='', )
    distribution_name = models.CharField(max_length=128, null=True, blank=True, default='', verbose_name="企业签名")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '应用详情'
        verbose_name_plural = "应用详情"

    def __str__(self):
        return "%s-%s" % (self.app_id, self.release_id)


class AppStorage(models.Model):
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="存储名字")
    storage_choices = ((0, '本地存储'), (1, '七牛云存储'), (2, '阿里云存储'), (3, '默认存储'))
    storage_type = models.SmallIntegerField(choices=storage_choices, default=3, verbose_name="存储类型")
    access_key = models.CharField(max_length=128, blank=True, null=True, verbose_name="存储访问key")
    secret_key = models.CharField(max_length=128, blank=True, null=True, verbose_name="存储访问secret")
    bucket_name = models.CharField(max_length=128, blank=True, null=True, verbose_name="存储空间bucket_name")
    domain_name = models.CharField(max_length=128, blank=True, null=True, verbose_name="下载域名",
                                   help_text='fly-storage.dvcloud.xin,可以自定义端口')
    is_https = models.BooleanField(default=True, verbose_name="是否支持https")

    sts_role_arn = models.CharField(max_length=128, blank=True, null=True, verbose_name="阿里云sts_role_arn")
    endpoint = models.CharField(max_length=128, blank=True, null=True, verbose_name="阿里云endpoint")
    download_auth_type_choices = ((1, 'OSS模式： 需要把OSS权限开启私有模式'), (2, 'CDN模式： 请先配置好阿里云CDN，开启阿里云OSS私有Bucket回源，将使用鉴权A方式'))
    download_auth_type = models.SmallIntegerField(choices=download_auth_type_choices, default=1,
                                                  verbose_name="阿里云下载授权方式")
    cnd_auth_key = models.CharField(max_length=128, blank=True, null=True, verbose_name="阿里云cnd_auth_key")

    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    description = models.TextField('备注', blank=True, null=True, default='')

    class Meta:
        verbose_name = '存储配置'
        verbose_name_plural = "存储配置"

    def save(self, *args, **kwargs):
        if self.storage_type in (1, 2):
            if self.bucket_name and self.secret_key and self.access_key:
                if self.storage_type == 2:
                    if not self.sts_role_arn or not self.endpoint:
                        return
                    if self.download_auth_type == 2 and not self.cnd_auth_key:
                        return
                return super(AppStorage, self).save(*args, **kwargs)
            else:
                return
        return super(AppStorage, self).save(*args, **kwargs)

    def __str__(self):
        return "%s %s" % (self.user_id.get_username(), self.name)


class AppUDID(models.Model):
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")
    # udid = models.CharField(max_length=64, verbose_name="udid唯一标识", db_index=True)
    udid = models.ForeignKey(to="UDIDsyncDeveloper", verbose_name="udid唯一标识", on_delete=models.CASCADE)
    product = models.CharField(max_length=64, verbose_name="产品", blank=True, null=True, )
    serial = models.CharField(max_length=64, verbose_name="序列号", blank=True, null=True, )
    version = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    imei = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    iccid = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_signed = models.BooleanField(verbose_name="是否完成签名打包", default=False)
    is_download = models.BooleanField(verbose_name="描述文件是否已经下载", default=False)
    binary_file = models.CharField(max_length=128, blank=True, verbose_name="签名包名称", null=True)

    class Meta:
        verbose_name = '设备详情'
        verbose_name_plural = "设备详情"
        unique_together = ('app_id', 'udid',)

    def __str__(self):
        return "%s-%s" % (self.app_id.name, self.udid)


class AppIOSDeveloperInfo(models.Model):
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE)
    issuer_id = models.CharField(max_length=64, null=False, verbose_name="标识创建认证令牌的发放者")
    private_key_id = models.CharField(max_length=64, null=False, verbose_name="密钥 ID")
    p8key = models.TextField(max_length=512, null=False, verbose_name="p8key")
    is_actived = models.BooleanField(default=False, verbose_name="是否已经激活")
    certid = models.CharField(max_length=64, blank=True, verbose_name="超级签名自动创建证书ID", null=True)
    usable_number = models.IntegerField(verbose_name="可使用设备数", default=100)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    cert_expire_time = models.DateTimeField(blank=True, null=True, verbose_name="证书过期时间")
    description = models.TextField('备注', blank=True, null=True, default='')
    auth_type_choices = ((0, 'p8key认证'),)
    auth_type = models.SmallIntegerField(choices=auth_type_choices, default=0, verbose_name="认证类型")

    class Meta:
        verbose_name = '苹果开发者账户'
        verbose_name_plural = "苹果开发者账户"
        unique_together = (('user_id', 'issuer_id'),)

    def save(self, *args, **kwargs):
        if self.usable_number > 100:
            self.usable_number = 100
        elif self.usable_number < 0:
            self.usable_number = 0
        return super(AppIOSDeveloperInfo, self).save(*args, **kwargs)

    def __str__(self):
        return "%s-%s" % (self.user_id, self.issuer_id)


class APPSuperSignUsedInfo(models.Model):
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE)
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")
    udid = models.ForeignKey(to="AppUDID", on_delete=models.CASCADE, verbose_name="所消耗的udid")
    developerid = models.ForeignKey(to="AppIOSDeveloperInfo", on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '设备使用统计'
        verbose_name_plural = "设备使用统计"

    def __str__(self):
        return "%s-%s-%s" % (self.user_id, self.app_id, self.udid)


class APPToDeveloper(models.Model):
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")
    developerid = models.ForeignKey(to="AppIOSDeveloperInfo", on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    binary_file = models.CharField(max_length=128, blank=True, verbose_name="签名包名称", null=True, unique=True)
    release_file = models.CharField(max_length=128, blank=True, verbose_name="源包名称", null=True)
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '应用开发者绑定'
        verbose_name_plural = "应用开发者绑定"

    def __str__(self):
        return "%s-%s-%s" % (self.developerid, self.app_id, self.binary_file)


class UDIDsyncDeveloper(models.Model):
    developerid = models.ForeignKey(to="AppIOSDeveloperInfo", on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    udid = models.CharField(max_length=64, verbose_name="udid唯一标识", db_index=True)
    product = models.CharField(max_length=64, verbose_name="产品", blank=True, null=True, )
    serial = models.CharField(max_length=64, verbose_name="序列号", blank=True, null=True, )
    version = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
    status = models.BooleanField(verbose_name="设备在开发者平台状态", default=False)

    class Meta:
        verbose_name = 'iOS开发平台同步设备信息'
        verbose_name_plural = "iOS开发平台同步设备信息"
        unique_together = ('udid', 'developerid',)

    def __str__(self):
        return "%s-%s-%s" % (self.product, self.udid, self.developerid)


class DeveloperAppID(models.Model):
    aid = models.CharField(max_length=64, null=False)  # ，apple APP 唯一标识
    profile_id = models.CharField(max_length=64, null=True, blank=True)  # ，profile_id 唯一标识
    developerid = models.ForeignKey(to="AppIOSDeveloperInfo", on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")

    class Meta:
        verbose_name = '超级签APP id'
        verbose_name_plural = "超级签APP id"
        unique_together = ('aid', 'developerid', 'app_id')

    def __str__(self):
        return "%s-%s-%s" % (self.aid, self.app_id, self.developerid)


class DeveloperDevicesID(models.Model):
    did = models.CharField(max_length=64, null=False)  # ，apple 设备唯一标识
    udid = models.ForeignKey(to="UDIDsyncDeveloper", on_delete=models.CASCADE, verbose_name="所消耗的udid")
    developerid = models.ForeignKey(to="AppIOSDeveloperInfo", on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户")
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")

    class Meta:
        verbose_name = '超级签Devices id'
        verbose_name_plural = "超级签Devices id"
        unique_together = ('did', 'developerid', 'app_id')

    def __str__(self):
        return "%s-%s-%s-%s" % (self.id, self.app_id, self.developerid, self.udid)


######################################## 订单表 ########################################

class Order(models.Model):
    """订单"""
    payment_type_choices = ((0, '微信'), (1, '支付宝'), (2, '优惠码'), (4, '银联'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices)
    payment_number = models.CharField(max_length=128, verbose_name="支付第3方订单号", null=True, blank=True)
    payment_name = models.CharField(max_length=128, verbose_name="支付商家名称", null=True, blank=True)
    order_number = models.CharField(max_length=128, verbose_name="订单号", unique=True)  # 考虑到订单合并支付的问题
    user_id = models.ForeignKey("UserInfo", on_delete=models.CASCADE)
    actual_amount = models.BigIntegerField(verbose_name="实付金额,单位分")
    actual_download_times = models.BigIntegerField(verbose_name="实际购买的数量", default=0)
    actual_download_gift_times = models.BigIntegerField(verbose_name="实际赠送的数量", default=0)
    status_choices = ((0, '交易成功'), (1, '待支付'), (2, '订单已创建'), (3, '退费申请中'), (4, '已退费'), (5, '主动取消'), (6, '超时取消'))
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态")
    order_type_choices = ((0, '用户下单'), (1, '后台充值'),)
    order_type = models.SmallIntegerField(choices=order_type_choices, default=0, verbose_name="订单类型")
    pay_time = models.DateTimeField(blank=True, null=True, verbose_name="付款时间")
    cancel_time = models.DateTimeField(blank=True, null=True, verbose_name="订单取消时间")
    created_time = models.DateTimeField(verbose_name="订单创建时间", auto_now_add=True)
    description = models.TextField('备注', blank=True, null=True, default='')


def __str__(self):
    return "%s-%s-%s元" % (self.user_id, self.order_number, self.actual_amount / 100)


class Price(models.Model):
    name = models.CharField(max_length=128, unique=True, verbose_name="下载包唯一名称")
    title = models.CharField(max_length=128, verbose_name="下载包名称")
    description = models.CharField(max_length=128, verbose_name="下载包描述")
    price = models.BigIntegerField(null=False, verbose_name="下载包价格，单位分")
    package_size = models.BigIntegerField(null=False, verbose_name="下载包次数")
    download_count_gift = models.IntegerField(default=0, null=False, verbose_name="赠送下载次数")
    is_enable = models.BooleanField(default=True, verbose_name="是否启用该价格")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '价格列表'
        verbose_name_plural = "价格列表"
        unique_together = ('price', 'package_size')

    def save(self, *args, **kwargs):
        if Price.objects.filter(is_enable=True).count() > 3:  # 最多3个启用的价格表
            raise
        super(Price, self).save(*args, **kwargs)

    def __str__(self):
        return "%s-%s-%s-%s" % (self.name, self.price, self.package_size, self.download_count_gift)


class UserCertificationInfo(models.Model):
    user_id = models.OneToOneField(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE,
                                   related_name='certification')
    name = models.CharField(max_length=128, null=False, verbose_name="真实姓名")
    card = models.CharField(max_length=128, null=False, verbose_name="身份证号码", unique=True)
    addr = models.CharField(max_length=128, null=False, verbose_name="居住地址")
    mobile = models.BigIntegerField(verbose_name="手机号码", null=True, blank=True)
    status_choices = ((-1, '待认证'), (0, '认证中'), (1, '认证成功'), (2, '认证失败'))
    status = models.SmallIntegerField(choices=status_choices, default=0, verbose_name="认证状态")
    msg = models.CharField(max_length=512, null=True, blank=True, verbose_name="备注")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    reviewed_time = models.DateTimeField(auto_now=True, verbose_name="审核时间")

    class Meta:
        verbose_name = '用户认证信息'
        verbose_name_plural = "用户认证信息"
        indexes = [models.Index(fields=['card'])]

    def __str__(self):
        return "%s-%s" % (self.user_id, self.name)


class CertificationInfo(models.Model):
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE)
    certification_url = models.CharField(max_length=128, blank=True, verbose_name="认证URL")
    type_choices = ((0, '未知'), (1, '国徽面照片'), (2, '人像面照片'), (3, '手持身份证照片'))
    type = models.SmallIntegerField(choices=type_choices, default=0, verbose_name="图像类型")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '身份证截图'
        verbose_name_plural = "身份证截图"

    def __str__(self):
        return "%s-%s" % (self.user_id, self.certification_url)


class DomainCnameInfo(models.Model):
    domain_record = models.CharField(max_length=128, unique=True, verbose_name="记录值")
    ip_address = models.CharField(max_length=128, verbose_name="域名解析地址", null=False)
    is_enable = models.BooleanField(default=True, verbose_name="是否启用该解析")
    is_system = models.BooleanField(default=False, verbose_name="是否是系统自带解析")
    is_https = models.BooleanField(default=False, verbose_name="是否支持HTTPS")
    description = models.TextField(verbose_name='备注', blank=True, null=True, default='')
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '系统分发域名配置'
        verbose_name_plural = "系统分发域名配置"

    def save(self, *args, **kwargs):
        if not self.domain_record or (self.domain_record and len(self.domain_record) < 26):  # 最多3个启用的价格表
            self.domain_record = '%s.%s' % (generate_numeric_token_of_length(24, 'abcdef'), self.domain_record)
        super(DomainCnameInfo, self).save(*args, **kwargs)

    def __str__(self):
        return "%s-%s-is_enable:%s-is_system:%s" % (self.domain_record, self.ip_address, self.is_enable, self.is_system)


class UserDomainInfo(models.Model):
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE)
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="APP专属域名", null=True, blank=True)
    cname_id = models.ForeignKey(to="DomainCnameInfo", verbose_name="cname解析ID", on_delete=models.CASCADE)
    domain_name = models.CharField(verbose_name="下载页面域名", db_index=True, max_length=64, null=False, blank=False)
    is_enable = models.BooleanField(default=False, verbose_name="绑定成功")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    domain_type_choices = ((0, '下载码域名'), (1, '下载页域名'), (2, '应用专用域名'))
    domain_type = models.SmallIntegerField(choices=domain_type_choices, default=1, verbose_name="域名类型",
                                           help_text="0 表示下载码域名，扫描下载码域名，会自动跳转到预览域名")

    class Meta:
        verbose_name = '用户分发域名绑定'
        verbose_name_plural = "用户分发域名绑定"

    def save(self, *args, **kwargs):
        if self.domain_type == 2:
            if not self.app_id:
                raise KeyError('app_id must exists when domain_type is 2')
        super(UserDomainInfo, self).save(*args, **kwargs)

    def __str__(self):
        return "%s-%s-%s" % (self.user_id, self.cname_id, self.domain_name)


class UserAdDisplayInfo(models.Model):
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE)
    ad_name = models.CharField(verbose_name="广告名称", max_length=256, null=False, blank=False)
    ad_uri = models.CharField(verbose_name="广告跳转地址", max_length=256, null=False, blank=False)
    ad_pic = models.CharField(verbose_name="广告图片地址", max_length=256, null=False, blank=False, help_text="像素最高80px", )
    weight = models.IntegerField(verbose_name="广告展示权重", default=1)
    description = models.TextField('描述信息', blank=True, null=True, default='')
    is_enable = models.BooleanField(default=False, verbose_name="广告开启状态")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="广告创建时间")

    class Meta:
        verbose_name = '用户自定义广告'
        verbose_name_plural = "用户自定义广告"
        indexes = [models.Index(fields=['ad_name', 'user_id'])]
        unique_together = ('ad_name', 'user_id',)

    def __str__(self):
        return "%s-%s-%s" % (self.user_id, self.description, self.is_enable)


class IosDeveloperPublicPoolBill(models.Model):
    user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE,
                                related_name='org_user_id')
    to_user_id = models.ForeignKey(to="UserInfo", verbose_name="用户ID", on_delete=models.CASCADE,
                                   related_name='to_user_id', null=True, blank=True)

    action_choices = ((0, '消费'), (1, '充值'), (2, '转账'))
    action = models.SmallIntegerField(choices=action_choices, default=0, verbose_name="资金类型",
                                      help_text="0 消费 1 充值 2 转账")
    number = models.IntegerField(verbose_name="消耗次数", default=1)
    app_info = models.JSONField(max_length=256, verbose_name="属于哪个APP", null=True, blank=True)
    udid_info = models.JSONField(max_length=256, verbose_name="设备id信息", null=True, blank=True)
    developer_info = models.JSONField(max_length=256, verbose_name="开发者信息", null=True, blank=True)
    udid_sync_info = models.ForeignKey(to="UDIDsyncDeveloper", on_delete=models.SET_NULL, verbose_name="关联同步设备信息",
                                       null=True, blank=True)
    # app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP",null=True,blank=True)
    # udid = models.ForeignKey(to="AppUDID", on_delete=models.CASCADE, verbose_name="所消耗的udid",null=True,blank=True)
    # developerid = models.ForeignKey(to="AppIOSDeveloperInfo", on_delete=models.CASCADE, verbose_name="所使用苹果开发者账户",null=True,blank=True)
    description = models.CharField(verbose_name="操作描述", max_length=128, default='', blank=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = '资金流转账单'
        verbose_name_plural = "资金流转账单"

    def __str__(self):
        return "%s-%s—%s" % (self.user_id, self.to_user_id, self.description)


class RemoteClientInfo(models.Model):
    remote_addr = models.GenericIPAddressField(verbose_name="远程IP地址")
    user_agent = models.CharField(verbose_name="客户端agent", max_length=512)
    method = models.CharField(verbose_name="请求方式", max_length=16)
    uri_info = models.CharField(verbose_name="访问的URI", max_length=256)
    a_domain = models.CharField(verbose_name="前端域名", max_length=128)
    description = models.CharField(verbose_name="访问描述", max_length=256)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="访问时间")

    class Meta:
        verbose_name = '客户端访问记录'
        verbose_name_plural = "客户端访问记录"

    def __str__(self):
        return "%s-%s" % (self.remote_addr, self.description)
