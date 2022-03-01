# Generated by Django 3.2.3 on 2022-02-15 21:29

from django.conf import settings
from django.db import migrations

price_info_list = [
    {
        "name": "1k_times",
        "title": "1k_times",
        "description": "1k_times",
        "price": 2500,
        "package_size": 1000,
        "download_count_gift": 100,
        "is_enable": True,
    },
    {
        "name": "10k_times",
        "title": "10k_times",
        "description": "10k_times",
        "price": 22000,
        "package_size": 10000,
        "download_count_gift": 800,
        "is_enable": True,
    },
    {
        "name": "100k_times",
        "title": "100k_times",
        "description": "100k_times",
        "price": 200000,
        "package_size": 100000,
        "download_count_gift": 8000,
        "is_enable": True,
    },
]
WEB_DOMAIN = settings.WEB_DOMAIN.split('//')[1]
domain_cname_info_list = [
    {
        "domain_record": WEB_DOMAIN,
        "ip_address": WEB_DOMAIN,
        "is_enable": True,
        "is_system": True,
        "is_https": True if settings.WEB_DOMAIN.startswith('https') else False,
        "description": f"默认下载页域名 {WEB_DOMAIN}",
    },
]


def add_default_price(apps, schema_editor):
    for price in price_info_list:
        price_model = apps.get_model('api', 'Price')
        price_model.objects.create(**price)


def add_default_domain_cname(apps, schema_editor):
    for domain_cname_info in domain_cname_info_list:
        domain_cname_info_model = apps.get_model('api', 'DomainCnameInfo')
        domain_cname_info_model.objects.create(**domain_cname_info)


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_default_price),
        migrations.RunPython(add_default_domain_cname)
    ]