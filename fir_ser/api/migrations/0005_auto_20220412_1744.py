# Generated by Django 3.2.3 on 2022-04-12 17:44

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_auto_20220330_0009'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppDownloadToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64, verbose_name='授权码')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='添加时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('used_count', models.BigIntegerField(default=0, verbose_name='已经使用次数')),
                ('bind_status', models.BooleanField(default=False, verbose_name='是否绑定设备udid')),
                ('bind_udid', models.CharField(blank=True, max_length=64, null=True, verbose_name='设备udid')),
                ('max_limit_count', models.BigIntegerField(default=0, verbose_name='最大可使用次数，0表示不限制')),
                ('description', models.CharField(blank=True, default='', max_length=256, verbose_name='备注')),
                ('app_id',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.apps', verbose_name='应用信息')),
            ],
            options={
                'verbose_name': '应用下载授权token',
                'verbose_name_plural': '应用下载授权token',
                'unique_together': {('app_id', 'token')},
            },
        ),
        migrations.CreateModel(
            name='UserPersonalConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.TextField(max_length=10240, verbose_name='配置值')),
                ('enable', models.BooleanField(default=True, verbose_name='是否启用该配置项')),
                ('description', models.CharField(blank=True, default='', max_length=256, verbose_name='备注')),
                ('updated_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('key', models.CharField(max_length=128, verbose_name='配置名称')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL,
                                              verbose_name='用户ID')),
            ],
            options={
                'verbose_name': '个人配置项',
                'verbose_name_plural': '个人配置项',
                'unique_together': {('user_id', 'key')},
            },
        ),
    ]
