# Generated by Django 3.0.3 on 2020-05-05 14:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0004_auto_20200504_2054'),
    ]

    operations = [
        migrations.AddField(
            model_name='apptodeveloper',
            name='release_file',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='源包名称'),
        ),
    ]