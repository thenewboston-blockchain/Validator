# Generated by Django 2.2.10 on 2020-05-17 17:59

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registrations', '0002_auto_20200517_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bankregistration',
            name='port',
            field=models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(65535)]),
        ),
    ]