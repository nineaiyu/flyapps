from django.db import models

# Create your models here.

from django.contrib.contenttypes.models import ContentType
from api.utils.app.randomstrings import make_random_uuid,make_app_uuid
from django.contrib.auth.models import AbstractUser

######################################## 用户表 ########################################



class UserInfo(AbstractUser):
    username = models.CharField("用户名", max_length=64, unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
        blank=True,
        null=True
    )
    uid = models.CharField(max_length=64, unique=True,db_index=True)  # user_id，唯一标识
    mobile = models.BigIntegerField(verbose_name="手机", unique=True, help_text="用于手机验证码登录", null=True)
    qq = models.BigIntegerField(verbose_name="QQ",  blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True, verbose_name="账户状态，默认启用")

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
    download_times = models.IntegerField(default=100, verbose_name="下载次数")
    all_download_times = models.BigIntegerField(default=0, verbose_name="总共下载次数")
    domain_name = models.CharField(verbose_name="域名",blank=True,null=True,max_length=64)
    history_release_limit = models.IntegerField(default=10,verbose_name="app 历史记录版本",blank=True,null=True)
    storage = models.OneToOneField(to='AppStorage',related_name='app_storage',
        on_delete=models.SET_NULL, verbose_name="存储",null=True,blank=True)

    class Meta:
        verbose_name = '账户信息'
        verbose_name_plural = "账户信息"

    def __str__(self):
        return "%s(%s)" % (self.username, self.get_role_display())

    def save(self, *args, **kwargs):
        if len(self.uid) < 8:
            self.uid = make_random_uuid()
        super(UserInfo, self).save(*args, **kwargs)

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
        return "%s" % (self.name)


######################################## APP表 ########################################

class Apps(models.Model):
    app_id =  models.CharField(max_length=64, unique=True,db_index=True)  # ，唯一标识
    user_id = models.ForeignKey(to="UserInfo",verbose_name="用户ID",on_delete=models.CASCADE)
    type_choices = ((0, 'android'),(1, 'ios'))
    type = models.SmallIntegerField(choices=type_choices, default=0, verbose_name="类型")
    name = models.CharField(max_length=32,blank=True, null=True,verbose_name="应用名称")
    short = models.CharField(max_length=16,unique=True,verbose_name="短链接",db_index=True)
    bundle_id = models.CharField(max_length=64,blank=True,verbose_name="bundle id")
    has_combo = models.OneToOneField(to="Apps", related_name='combo_app_info',
         verbose_name="关联应用",on_delete=models.SET_NULL,null=True,blank=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    count_hits = models.BigIntegerField(verbose_name="下载次数",default=0)
    password = models.CharField(verbose_name="访问密码",default='',help_text='默认 没有密码',max_length=32)
    isshow = models.BigIntegerField(verbose_name="下载页可见",default=1)
    issupersign = models.BigIntegerField(verbose_name="是否超级签名包",default=False)
    description = models.TextField('描述', blank=True, null=True, default=None, )
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    class Meta:
        verbose_name = '应用信息'
        verbose_name_plural = "应用信息"
        indexes = [models.Index(fields=['app_id']),models.Index(fields=['id','user_id','type'])]

    def __str__(self):
        return "%s %s" % (self.name,self.get_type_display())


class AppReleaseInfo(models.Model):
    is_master = models.BooleanField(verbose_name="是否master版本",default=True)
    release_id = models.CharField(max_length=64, unique=True,verbose_name="release 版本id",db_index=True)
    app_id = models.ForeignKey(to="Apps",on_delete=models.CASCADE,verbose_name="属于哪个APP")
    build_version = models.CharField(max_length=16,verbose_name="build版本",blank=True)
    app_version = models.CharField(max_length=16,verbose_name="app版本",blank=True)
    release_choices=((0,'android'),(1,'adhoc'),(2,'Inhouse'),(3,'unknown'))
    release_type = models.SmallIntegerField(choices=release_choices, default=0, verbose_name="版本类型")
    minimum_os_version = models.CharField(max_length=64,verbose_name="应用可安装的最低系统版本")
    binary_size = models.BigIntegerField(verbose_name="应用大小")
    binary_url = models.CharField(max_length=128,blank=True,verbose_name="第三方下载URL")
    icon_url = models.CharField(max_length=128,blank=True,verbose_name="图标url")
    changelog = models.TextField('更新日志', blank=True, null=True, default=None, )
    udid = models.TextField('ios内测版 udid', blank=True, null=True, default='', )

    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = '应用详情'
        verbose_name_plural = "应用详情"

    def __str__(self):
        return "%s" % (self.release_id)


class AppStorage(models.Model):
    user_id = models.ForeignKey(to="UserInfo",verbose_name="用户ID",on_delete=models.CASCADE)
    name = models.CharField(max_length=64,blank=True, null=True, verbose_name="存储名字")
    # is_used = models.BooleanField(verbose_name="是否使用该存储",default=True)
    storage_choices=((0,'本地存储'),(1,'七牛云存储'),(2,'阿里云存储'),(3,'默认存储'))
    storage_type = models.SmallIntegerField(choices=storage_choices, default=3, verbose_name="存储类型")
    access_key =models.CharField(max_length=128,blank=True, null=True, verbose_name="存储访问key")
    secret_key =models.CharField(max_length=128,blank=True, null=True, verbose_name="存储访问secret")
    bucket_name=models.CharField(max_length=128,blank=True, null=True, verbose_name="存储空间bucket_name")
    domain_name=models.CharField(max_length=128,blank=True, null=True, verbose_name="下载域名",help_text='fly-storage.dvcloud.xin,可以自定义端口')
    is_https = models.BooleanField(default=True, verbose_name="是否支持https")
    additionalparameters = models.TextField(blank=True, null=True,verbose_name="额外参数",
                                            help_text='阿里云:{"sts_role_arn":"arn信息","endpoint":""} ', default=None)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    description = models.TextField('备注', blank=True, null=True, default='')

    class Meta:
        verbose_name = '存储配置'
        verbose_name_plural = "存储配置"

    def __str__(self):
        return "%s %s" % (self.user_id.get_username(),self.name)

class AppUDID(models.Model):
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")
    udid = models.CharField(max_length=64, unique=True,verbose_name="udid唯一标识",db_index=True)
    product = models.CharField(max_length=64, verbose_name="产品", blank=True, null=True, )
    serial = models.CharField(max_length=64, verbose_name="序列号", blank=True, null=True, )
    version = models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    imei= models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    iccid= models.CharField(max_length=64, verbose_name="型号", blank=True, null=True, )
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_signed = models.BooleanField(verbose_name="是否完成签名打包",default=False)
    binary_file = models.CharField(max_length=128,blank=True,verbose_name="签名包名称",null=True)


    class Meta:
        verbose_name = '设备详情'
        verbose_name_plural = "设备详情"
        unique_together = ('app_id', 'udid',)

    def __str__(self):
        return "%s-%s" % (self.app_id.name,self.udid)

class AppIOSDeveloperInfo(models.Model):
    user_id = models.ForeignKey(to="UserInfo",verbose_name="用户ID",on_delete=models.CASCADE)
    name = models.CharField(max_length=64,verbose_name="开发者标识",unique=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=64,
        unique=True,
        blank=True,
        null=True
    )
    password = models.CharField(max_length=64,)
    is_actived = models.BooleanField(default=False,verbose_name="是否已经激活")
    certid = models.CharField(max_length=64,blank=True,verbose_name="超级签名自动创建证书ID",null=True)
    usable_number = models.IntegerField(verbose_name="可使用设备数",default=100)
    use_number = models.IntegerField(verbose_name="已消耗设备数",default=0)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    class Meta:
        verbose_name = '苹果开发者账户'
        verbose_name_plural = "苹果开发者账户"


    def __str__(self):
        return "%s-%s" % (self.name,self.email)

class APPSuperSignUsedInfo(models.Model):
    user_id = models.ForeignKey(to="UserInfo",verbose_name="用户ID",on_delete=models.CASCADE)
    app_id = models.ForeignKey(to="Apps", on_delete=models.CASCADE, verbose_name="属于哪个APP")
    udid = models.ForeignKey(to="AppUDID",on_delete=models.CASCADE, verbose_name="所消耗的udid")
    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    class Meta:
        verbose_name = '设备使用统计'
        verbose_name_plural = "设备使用统计"

    def __str__(self):
        return "%s-%s-%s" % (self.user_id,self.app_id,self.udid)