from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Count

from common.base.baseutils import make_random_uuid
######################################## 用户表 ########################################
from common.base.daobase import AESCharField
from common.utils.token import generate_alphanumeric_token_of_length, generate_numeric_token_of_length


# Create your models here.


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
    notify_available_downloads = models.IntegerField(default=0, verbose_name="下载余额不足通知", blank=True, null=True)
    notify_available_signs = models.IntegerField(default=0, verbose_name="签名余额不足通知", blank=True, null=True)

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
        if not self.default_domain_name_id:
            default_domain_obj = min(
                DomainCnameInfo.objects.annotate(Count('userinfo')).filter(is_enable=True, is_system=True),
                key=lambda x: x.userinfo__count)
            if default_domain_obj:
                self.default_domain_name_id = default_domain_obj.pk
        super(UserInfo, self).save(*args, **kwargs)


class WeChatInfo(models.Model):
    openid = models.CharField(max_length=64, unique=True, verbose_name="普通用户的标识，对当前公众号唯一")
    nickname = models.CharField(max_length=64, verbose_name="昵称", blank=True)
    sex = models.SmallIntegerField(default=0, verbose_name="性别", help_text="值为1时是男性，值为2时是女性，值为0时是未知")
    subscribe_time = models.BigIntegerField(verbose_name="订阅时间")
    head_img_url = models.CharField(max_length=256, verbose_name="用户头像", blank=True, null=True)
    address = models.CharField(max_length=128, verbose_name="地址", blank=True, null=True)
    subscribe = models.BooleanField(verbose_name="是否订阅公众号", default=0)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="授权时间")

    class Meta:
        verbose_name = '微信信息'
        verbose_name_plural = "微信信息"

    def __str__(self):
        return f"{self.nickname}-{self.openid}"


class ThirdWeChatUserInfo(models.Model):
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    weixin = models.ForeignKey(to=WeChatInfo, verbose_name="微信信息", on_delete=models.CASCADE)
    enable_login = models.BooleanField(verbose_name="是否允许登录", default=0)
    enable_notify = models.BooleanField(verbose_name="是否允许推送消息", default=0)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="授权时间")

    class Meta:
        verbose_name = '微信登录通知相关信息'
        verbose_name_plural = "微信登录通知相关信息"
        unique_together = (('user_id', 'weixin'),)

    def __str__(self):
        return f"{self.user_id}-{self.weixin} enable_notify:{self.enable_notify} enable_login:{self.enable_login}"


class Token(models.Model):
    """
    The default authorization token model.
    """
    access_token = models.CharField(max_length=64, unique=True)
    user = models.ForeignKey(
        UserInfo, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name="关联用户"
    )
    remote_addr = models.GenericIPAddressField(verbose_name="远程IP地址", null=True, blank=True)
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


class Apps(models.Model):
    app_id = models.CharField(max_length=64, unique=True, db_index=True)  # ，唯一标识
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
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
    need_password = models.BooleanField(verbose_name="访问密码", help_text='默认 没有密码', default=False)
    isshow = models.BooleanField(verbose_name="下载页可见", default=True)
    issupersign = models.BooleanField(verbose_name="是否超级签名包", default=False)
    change_auto_sign = models.BooleanField(verbose_name="签名相关的数据更新自动签名", default=False)
    supersign_type_choices = ((0, '普通权限'), (1, '推送权限，请上传adhoc包'), (2, 'network、vpn、推送权限，请上传adhoc包'), (3, '特殊权限'))
    supersign_type = models.SmallIntegerField(choices=supersign_type_choices, default=1, verbose_name="签名类型")
    new_bundle_id = models.CharField(max_length=64, blank=True, null=True, verbose_name="new_bundle_id",
                                     help_text="用于超级签某些因素下需要修改包名")
    new_bundle_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="new_bundle_name",
                                       help_text="应用新名称")
    supersign_limit_number = models.IntegerField(verbose_name="签名使用限额", default=0)
    wxredirect = models.BooleanField(verbose_name="微信内第三方链接自动跳转", default=True)
    wxeasytype = models.BooleanField(verbose_name="微信内简易模式，避免微信封停", default=True)
    description = models.TextField('描述', blank=True, null=True, default=None, )
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '应用信息'
        verbose_name_plural = "应用信息"
        indexes = [models.Index(fields=['app_id']), models.Index(fields=['id', 'user_id', 'type'])]

    def __str__(self):
        return "%s %s-%s %s" % (self.name, self.get_type_display(), self.short, self.issupersign)


class AppBundleIdBlackList(models.Model):
    """
    :keyword 优先级：用户黑名单 > 用户白名单 > 全局黑名单 > 全局白名单
    """
    user_uid = models.CharField(max_length=64, verbose_name="用户ID,*表示全局", default='*')
    bundle_id = models.CharField(max_length=64, blank=True, verbose_name="bundle id")
    enable = models.BooleanField(default=True, verbose_name="是否启用该配置项")
    status_choices = ((0, '黑名单'), (1, '白名单'))
    status = models.SmallIntegerField(choices=status_choices, default=1, verbose_name="状态")
    description = models.CharField(verbose_name="备注", max_length=256, default='', blank=True)
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '新应用上传黑白名单'
        verbose_name_plural = "新应用上传黑白名单"
        unique_together = ('user_uid', 'bundle_id')

    def __str__(self):
        return "%s-%s-%s" % (self.user_uid, self.bundle_id, self.enable)


class AppScreenShot(models.Model):
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="属于哪个APP")
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
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="属于哪个APP")
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
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    name = models.CharField(max_length=64, blank=True, null=True, verbose_name="存储名字")
    storage_choices = ((0, '本地存储'), (1, '七牛云存储'), (2, '阿里云存储'), (3, '默认存储'))
    storage_type = models.SmallIntegerField(choices=storage_choices, default=3, verbose_name="存储类型")
    access_key = models.CharField(max_length=128, blank=True, null=True, verbose_name="存储访问key")
    secret_key = AESCharField(max_length=128, blank=True, null=True, verbose_name="存储访问secret")
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


class Order(models.Model):
    """订单"""
    payment_type_choices = ((0, '微信'), (1, '支付宝'), (2, '优惠码'), (4, '银联'))
    payment_type = models.SmallIntegerField(choices=payment_type_choices)
    payment_number = models.CharField(max_length=128, verbose_name="支付第3方订单号", null=True, blank=True)
    payment_name = models.CharField(max_length=128, verbose_name="支付商家名称", null=True, blank=True)
    order_number = models.CharField(max_length=128, verbose_name="订单号", unique=True)  # 考虑到订单合并支付的问题
    user_id = models.ForeignKey(UserInfo, on_delete=models.CASCADE)
    actual_amount = models.BigIntegerField(verbose_name="实付金额,单位分")
    actual_download_times = models.BigIntegerField(verbose_name="实际购买的数量", default=0)
    actual_download_gift_times = models.BigIntegerField(verbose_name="实际赠送的数量", default=0)
    status_choices = ((0, '交易成功'), (1, '待支付'), (2, '订单已创建'), (3, '退费申请中'), (4, '已退费'), (5, '主动取消'), (6, '超时取消'))
    status = models.SmallIntegerField(choices=status_choices, verbose_name="状态")
    order_type_choices = ((0, '用户下单'), (1, '后台充值'), (2, '系统赠送'))
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
    user_id = models.OneToOneField(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE,
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
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
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
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="APP专属域名", null=True, blank=True)
    cname_id = models.ForeignKey(to=DomainCnameInfo, verbose_name="cname解析ID", on_delete=models.CASCADE)
    domain_name = models.CharField(verbose_name="下载页面域名", db_index=True, max_length=64, null=False, blank=False)
    is_https = models.BooleanField(default=False, verbose_name="是否支持HTTPS")
    weight = models.IntegerField(verbose_name="下载页域名展示权重", default=10)
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
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    ad_name = models.CharField(verbose_name="广告名称", max_length=256, null=False, blank=False)
    ad_uri = models.CharField(verbose_name="广告跳转地址", max_length=256, null=False, blank=False)
    ad_pic = models.CharField(verbose_name="广告图片地址", max_length=256, null=False, blank=False, help_text="像素最高80px", )
    weight = models.IntegerField(verbose_name="广告展示权重", default=10)
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


class AppReportInfo(models.Model):
    app_id = models.ForeignKey(to=Apps, on_delete=models.SET_NULL, verbose_name="应用信息",
                               null=True, blank=True)
    app_name = models.CharField(max_length=32, blank=True, null=True, verbose_name="应用名称")
    bundle_id = models.CharField(max_length=64, blank=True, verbose_name="bundle id")
    remote_addr = models.GenericIPAddressField(verbose_name="远程IP地址")
    report_type_choices = ((0, '侵权'), (1, '色情'), (2, '赌博'), (3, '欺诈'), (4, '暴力'), (5, '其他'),)
    report_type = models.SmallIntegerField(choices=report_type_choices, default=5, verbose_name="举报类型")
    report_reason = models.CharField(max_length=512, verbose_name="举报详情")
    email = models.CharField(max_length=64, verbose_name="联系方式")
    username = models.CharField(max_length=64, verbose_name="姓名")
    status_choices = ((1, '处理中'), (2, '已经处理'))
    status = models.SmallIntegerField(choices=status_choices, default=1, verbose_name="处理状态")
    description = models.CharField(verbose_name="备注", max_length=256, default='', blank=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="访问时间")

    class Meta:
        verbose_name = '应用举报信息'
        verbose_name_plural = "应用举报信息"

    def __str__(self):
        return "%s-%s" % (self.app_name, self.report_reason)


class SystemConfig(models.Model):
    key = models.CharField(max_length=128, unique=True, verbose_name="配置名称")
    value = models.TextField(max_length=10240, verbose_name="配置值")
    enable = models.BooleanField(default=True, verbose_name="是否启用该配置项")
    description = models.CharField(verbose_name="备注", max_length=256, default='', blank=True)
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = '系统配置项'
        verbose_name_plural = "系统配置项"

    def __str__(self):
        return "%s-%s" % (self.key, self.description)


class NotifyReceiver(models.Model):
    receiver_name = models.CharField(max_length=128, verbose_name="姓名")
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    weixin = models.ForeignKey(to=ThirdWeChatUserInfo, verbose_name="微信ID", on_delete=models.CASCADE, null=True)
    email = models.EmailField(verbose_name='邮箱', max_length=255, blank=True, null=True)
    description = models.CharField(verbose_name="备注", max_length=256, default='', blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = '信息接收配置'
        verbose_name_plural = "信息接收配置"
        unique_together = (('user_id', 'email',), ('user_id', 'weixin'), ('user_id', 'receiver_name'))

    def __str__(self):
        return "%s-%s-%s" % (self.user_id, self.receiver_name, self.description)


class NotifyConfig(models.Model):
    user_id = models.ForeignKey(to=UserInfo, verbose_name="用户ID", on_delete=models.CASCADE)
    config_name = models.CharField(max_length=128, verbose_name="通知名称")
    message_type_choices = (
        (0, '签名余额不足'), (1, '下载次数不足'), (2, '应用签名限额'), (3, '应用签名失败'),
        (4, '充值到账提醒'), (5, '优惠活动通知'), (6, '证书到期消息'), (7, '系统提醒'))
    message_type = models.SmallIntegerField(choices=message_type_choices, default=5, verbose_name="消息类型")
    sender = models.ManyToManyField(to=NotifyReceiver, verbose_name="通知接受者方式")
    enable_weixin = models.BooleanField(default=True, verbose_name="是否启用该配置项")
    enable_email = models.BooleanField(default=True, verbose_name="是否启用该配置项")
    description = models.CharField(verbose_name="备注", max_length=256, default='', blank=True)
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = '信息接收配置'
        verbose_name_plural = "信息接收配置"
        unique_together = (('user_id', 'config_name',),)

    def __str__(self):
        return "%s-%s-%s" % (self.user_id, self.get_message_type_display(), self.sender)


class AppDownloadToken(models.Model):
    app_id = models.ForeignKey(to=Apps, on_delete=models.CASCADE, verbose_name="应用信息")
    token = models.CharField(max_length=64, verbose_name='授权码')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    used_count = models.BigIntegerField(verbose_name="已经使用次数", default=0)
    max_limit_count = models.BigIntegerField(verbose_name="最大可使用次数，0表示不限制", default=0)
    description = models.CharField(verbose_name="备注", max_length=256, default='', blank=True)

    class Meta:
        verbose_name = '应用下载授权token'
        verbose_name_plural = "应用下载授权token"
        unique_together = (('app_id', 'token',),)

    def __str__(self):
        return "%s-%s-%s" % (self.app_id, self.token, self.description)
