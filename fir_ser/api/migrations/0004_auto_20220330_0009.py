# Generated by Django 3.2.3 on 2022-03-30 00:09

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0003_appbundleidblacklist'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeChatInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('openid', models.CharField(max_length=64, unique=True, verbose_name='普通用户的标识，对当前公众号唯一')),
                ('nickname', models.CharField(blank=True, max_length=64, verbose_name='昵称')),
                ('sex', models.SmallIntegerField(default=0, help_text='值为1时是男性，值为2时是女性，值为0时是未知', verbose_name='性别')),
                ('subscribe_time', models.BigIntegerField(verbose_name='订阅时间')),
                ('head_img_url', models.CharField(blank=True, max_length=256, null=True, verbose_name='用户头像')),
                ('address', models.CharField(blank=True, max_length=128, null=True, verbose_name='地址')),
                ('subscribe', models.BooleanField(default=0, verbose_name='是否订阅公众号')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='授权时间')),
            ],
            options={
                'verbose_name': '微信信息',
                'verbose_name_plural': '微信信息',
            },
        ),
        migrations.AddField(
            model_name='userinfo',
            name='notify_available_downloads',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='下载余额不足通知'),
        ),
        migrations.AddField(
            model_name='userinfo',
            name='notify_available_signs',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='签名余额不足通知'),
        ),
        migrations.CreateModel(
            name='ThirdWeChatUserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enable_login', models.BooleanField(default=0, verbose_name='是否允许登录')),
                ('enable_notify', models.BooleanField(default=0, verbose_name='是否允许推送消息')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='授权时间')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                              verbose_name='用户ID')),
                ('weixin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.wechatinfo',
                                             verbose_name='微信信息')),
            ],
            options={
                'verbose_name': '微信登录通知相关信息',
                'verbose_name_plural': '微信登录通知相关信息',
                'unique_together': {('user_id', 'weixin')},
            },
        ),
        migrations.CreateModel(
            name='NotifyReceiver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('receiver_name', models.CharField(max_length=128, verbose_name='姓名')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='邮箱')),
                ('description', models.CharField(blank=True, default='', max_length=256, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                              verbose_name='用户ID')),
                ('weixin',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.thirdwechatuserinfo',
                                   verbose_name='微信ID')),
            ],
            options={
                'verbose_name': '信息接收配置',
                'verbose_name_plural': '信息接收配置',
                'unique_together': {('user_id', 'email'), ('user_id', 'weixin'), ('user_id', 'receiver_name')},
            },
        ),
        migrations.CreateModel(
            name='NotifyConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config_name', models.CharField(max_length=128, verbose_name='通知名称')),
                ('message_type', models.SmallIntegerField(
                    choices=[(0, '签名余额不足'), (1, '下载次数不足'), (2, '应用签名限额'), (3, '应用签名失败'), (4, '充值到账提醒'), (5, '优惠活动通知'),
                             (6, '证书到期消息'), (7, '系统提醒')], default=5, verbose_name='消息类型')),
                ('enable_weixin', models.BooleanField(default=True, verbose_name='是否启用该配置项')),
                ('enable_email', models.BooleanField(default=True, verbose_name='是否启用该配置项')),
                ('description', models.CharField(blank=True, default='', max_length=256, verbose_name='备注')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('sender', models.ManyToManyField(to='api.NotifyReceiver', verbose_name='通知接受者方式')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                              verbose_name='用户ID')),
            ],
            options={
                'verbose_name': '信息接收配置',
                'verbose_name_plural': '信息接收配置',
                'unique_together': {('user_id', 'config_name')},
            },
        ),
    ]