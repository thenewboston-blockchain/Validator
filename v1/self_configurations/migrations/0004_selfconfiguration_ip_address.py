# Generated by Django 2.2.10 on 2020-05-17 00:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('self_configurations', '0003_selfconfiguration_primary'),
    ]

    operations = [
        migrations.AddField(
            model_name='selfconfiguration',
            name='ip_address',
            field=models.GenericIPAddressField(default='127.0.0.1', unique=True),
            preserve_default=False,
        ),
    ]
